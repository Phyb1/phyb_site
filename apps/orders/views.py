import logging

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import OrderForm
from .models import Order, PaymentAttempt
from .services import PaynowService

logger = logging.getLogger("apps.orders")


def order_create(request):
    initial = {}
    if request.GET.get("package"):
        initial["package"] = request.GET["package"]

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            logger.info("New order created: %s (id=%s)", order, order.pk)
            return redirect("orders:payment_method", pk=order.pk)
    else:
        form = OrderForm(initial=initial)

    return render(request, "orders/order_form.html", {"form": form})


def payment_method(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, "orders/payment_method.html", {"order": order})


@require_POST
def initiate_web_payment(request, pk):
    order = get_object_or_404(Order, pk=pk)
    result = PaynowService().initiate_web_checkout(order)
    if result.success:
        return redirect(result.redirect_url)
    messages.error(request, result.error)
    return redirect("orders:payment_method", pk=order.pk)


@require_POST
def initiate_mobile_payment(request, pk):
    order = get_object_or_404(Order, pk=pk)
    method = request.POST.get("method", "ecocash")
    phone = request.POST.get("phone", "").strip()

    if not phone:
        messages.error(request, "Enter the phone number to pay from.")
        return redirect("orders:payment_method", pk=order.pk)

    result = PaynowService().initiate_mobile_payment(order, phone, method)
    if not result.success:
        messages.error(request, result.error)
        return redirect("orders:payment_method", pk=order.pk)

    request.session[f"poll_url_{order.pk}"] = result.poll_url
    messages.info(request, result.instructions)
    return redirect("orders:status", pk=order.pk)


def order_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, "orders/order_status.html", {"order": order})


def order_status_partial(request, pk):
    """htmx polling target — swapped into order_status.html every few
    seconds while a mobile payment is awaiting the customer's PIN entry."""
    order = get_object_or_404(Order, pk=pk)
    attempt = order.payment_attempts.first()

    if attempt and attempt.poll_url and order.status == Order.Status.AWAITING_PAYMENT:
        PaynowService().sync_attempt_status(attempt)
        order.refresh_from_db()

    return render(request, "orders/_status_fragment.html", {"order": order})


def payment_return(request):
    """Paynow redirects the customer's browser here after web checkout
    (their RETURN_URL). Unlike the result_url webhook, this is just a
    friendly landing page — the reference query param tells us which
    order to show status for; the actual status update still comes from
    the webhook/poll, never from this redirect alone."""
    reference = request.GET.get("reference") or request.GET.get("paynowreference", "")
    order_pk = None
    if reference.startswith("PHYB-"):
        try:
            order_pk = int(reference.split("-", 1)[1])
        except (ValueError, IndexError):
            order_pk = None

    if order_pk and Order.objects.filter(pk=order_pk).exists():
        return redirect("orders:status", pk=order_pk)

    messages.info(request, "If you completed payment, your order status will update shortly.")
    return redirect("core:home")


@csrf_exempt
@require_POST
def paynow_update(request):
    """Paynow's server-to-server callback (their RESULT_URL). Must stay
    CSRF-exempt since the POST comes from Paynow, not a browser with our
    session — Paynow's own hash check on the payload is the real guard
    against forged callbacks, handled inside PaynowService/paynow client."""
    reference = request.POST.get("reference", "")
    logger.info("Paynow webhook received for reference=%s", reference)

    poll_url = request.POST.get("pollurl", "")
    if not poll_url:
        return render(request, "orders/_webhook_ack.html", status=400)

    attempt = PaymentAttempt.objects.filter(poll_url=poll_url).first()
    if attempt:
        PaynowService().sync_attempt_status(attempt)
    else:
        logger.warning("Paynow webhook: no matching PaymentAttempt for poll_url=%s", poll_url)

    return render(request, "orders/_webhook_ack.html")
