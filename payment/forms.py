from django import forms
from .models import PayWithCrypto



class InitializePaymentForm(forms.ModelForm):
    class Meta:
        model = PayWithCrypto
        fields = [
            'name',
            'email'
        ]