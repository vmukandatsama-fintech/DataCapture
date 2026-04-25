from django import forms
from django.contrib.auth.hashers import make_password


class UserImportForm(forms.Form):
    csv_file = forms.FileField()


class AdminUserCreationForm(forms.ModelForm):
    pin = forms.CharField(
        max_length=10,
        label="PIN",
        widget=forms.TextInput(attrs={'autocomplete': 'off'}),
        help_text="Will be hashed on save. User will be prompted to change it on first login.",
    )
    pin_confirm = forms.CharField(
        max_length=10,
        label="Confirm PIN",
        widget=forms.TextInput(attrs={'autocomplete': 'off'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        pin = cleaned_data.get('pin')
        pin_confirm = cleaned_data.get('pin_confirm')
        if pin and pin_confirm and pin != pin_confirm:
            self.add_error('pin_confirm', "PINs do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.pin = make_password(self.cleaned_data['pin'])
        user.set_unusable_password()
        if commit:
            user.save()
        return user

    class Meta:
        from .models import User
        model = User
        fields = ('username', 'role', 'is_staff', 'must_change_pin')


class GrowerImportForm(forms.Form):
    csv_file = forms.FileField(
        label="CSV File",
        help_text="Upload the CY26 masterlist CSV. See expected column headers below.",
        widget=forms.ClearableFileInput(attrs={
            'class': 'block w-full text-lg border rounded-lg p-3 mt-2',
            'style': 'min-height:48px;',
            'accept': '.csv',
            'autofocus': 'autofocus',
            'tabindex': '1',
        })
    )