from django import forms
from .models import Customer, Lead
from django.core.exceptions import ValidationError

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'company']

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        email = cleaned_data.get('email')
        if Customer.objects.filter(name=name, email=email).exists():
            raise ValidationError("Customer with this name and email already exists.")
        return cleaned_data

class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['customer', 'title', 'status', 'follow_up_date', 'notes']
        widgets = {
            'follow_up_date': forms.DateInput(
                attrs={
                    'type': 'date',  # This enables the calendar picker
                    'class': 'form-control'
                }
            ),
        }

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(label='Select CSV file')
