from django import forms


class UserImportForm(forms.Form):
    csv_file = forms.FileField()


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