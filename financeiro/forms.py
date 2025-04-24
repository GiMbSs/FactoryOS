from django import forms
from .models import ContaPagar, ContaReceber

class ContaPagarForm(forms.ModelForm):
    class Meta:
        model = ContaPagar
        fields = ['fornecedor', 'valor', 'data_vencimento', 'status']
        widgets = {
            'data_vencimento': forms.DateInput(attrs={'type': 'date'}),
            'valor': forms.NumberInput(attrs={'step': '0.01'}),
        }

class ContaReceberForm(forms.ModelForm):
    class Meta:
        model = ContaReceber
        fields = ['cliente', 'valor', 'data_vencimento', 'status']
        widgets = {
            'data_vencimento': forms.DateInput(attrs={'type': 'date'}),
            'valor': forms.NumberInput(attrs={'step': '0.01'}),
        }
