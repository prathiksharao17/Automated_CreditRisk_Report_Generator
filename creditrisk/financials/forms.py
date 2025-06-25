# forms.py

from django import forms
from .models import Company, FinancialDocument

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'company_name', 'company_number', 'company_pan',
            'line_of_business', 'website', 'incorporated_on', 'location'
        ]

class FinancialDocumentForm(forms.ModelForm):
    class Meta:
        model = FinancialDocument
        fields = ['balance_sheet', 'income_statement', 'cash_flow_statement']

