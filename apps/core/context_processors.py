from django.conf import settings


def site_meta(request):
    """Global template context — site name/domain/contact details
    available everywhere without every view having to pass them in."""
    return {
        "SITE_NAME": settings.SITE_NAME,
        "SITE_DOMAIN": settings.SITE_DOMAIN,
        "WHATSAPP_NUMBER": settings.WHATSAPP_NUMBER,
        "CONTACT_PHONE_DISPLAY": settings.CONTACT_PHONE_DISPLAY,
        "CONTACT_EMAIL": settings.CONTACT_EMAIL,
        "BUSINESS_ADDRESS": settings.BUSINESS_ADDRESS,
    }
