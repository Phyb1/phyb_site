from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Layout, Submit
from django import forms

from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["package", "business_name", "contact_name", "phone", "email", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        # Single column, full-width fields — deliberately simple for a
        # mobile form filled in on a small screen, no side-by-side rows.
        self.helper.layout = Layout(
            Div(Field("package"), css_class="mb-3"),
            Div(Field("business_name", placeholder="e.g. Samwa Bakery"), css_class="mb-3"),
            Div(Field("contact_name", placeholder="Your name"), css_class="mb-3"),
            Div(Field("phone", placeholder="0776298873"), css_class="mb-3"),
            Div(Field("email", placeholder="Optional"), css_class="mb-3"),
            Div(Field("notes", placeholder="What do you sell? Any existing social pages?"), css_class="mb-3"),
        )
        self.helper.add_input(Submit("submit", "Continue to Payment", css_class="btn btn-brand w-100"))

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip().replace(" ", "")
        digits = phone.lstrip("+")
        if not digits.isdigit() or len(digits) < 9:
            raise forms.ValidationError("Enter a valid phone number, e.g. 0776298873.")
        return phone
