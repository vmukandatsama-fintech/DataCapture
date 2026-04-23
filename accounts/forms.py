from django import forms

class UserImportForm(forms.Form):
    csv_file = forms.FileField()