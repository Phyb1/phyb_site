import factory

from apps.orders.models import Order, Package


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    package = Package.SIGNPOST
    business_name = factory.Sequence(lambda n: f"Test Business {n}")
    contact_name = "Test Owner"
    phone = "0776298873"
    email = "owner@example.com"
