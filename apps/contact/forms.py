from django import forms
from django.core.validators import EmailValidator

from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox


class ContactForm(forms.Form):
    name = forms.CharField(required=True)
    email = forms.EmailField(required=True, validators=[EmailValidator()])
    message = forms.CharField(required=True, widget=forms.Textarea)
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

