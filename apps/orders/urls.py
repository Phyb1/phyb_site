from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("new/", views.order_create, name="create"),
    path("<int:pk>/payment/", views.payment_method, name="payment_method"),
    path("<int:pk>/payment/web/", views.initiate_web_payment, name="initiate_web"),
    path("<int:pk>/payment/mobile/", views.initiate_mobile_payment, name="initiate_mobile"),
    path("<int:pk>/status/", views.order_status, name="status"),
    path("<int:pk>/status/partial/", views.order_status_partial, name="status_partial"),
    path("payment/update/", views.paynow_update, name="paynow_update"),
    path("payment/return/", views.payment_return, name="payment_return"),
]
