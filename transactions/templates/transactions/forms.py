from django import forms
from django.contrib.auth.models import User
from .models import Wallet

class WalletUpdateForm(forms.ModelForm):
    shared_with = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Wallet
        fields = ['name', 'wallet_type', 'balance', 'shared_with']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['shared_with'].queryset = User.objects.exclude(pk=self.user.pk)