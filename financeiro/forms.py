from django import forms
from .models import ContaPagar, ContaReceber
from django.core.validators import MinValueValidator
from decimal import Decimal

class ContaPagarForm(forms.ModelForm):
    valor = forms.DecimalField(
        min_value=0.01,
        error_messages={'min_value': 'O valor deve ser maior que zero.'},
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    class Meta:
        model = ContaPagar
        fields = ['fornecedor', 'valor', 'data_vencimento', 'status', 'data_pagamento', 'observacoes']
        widgets = {
            'data_vencimento': forms.DateInput(attrs={'type': 'date'}),
            'data_pagamento': forms.DateInput(attrs={'type': 'date'}),
            'valor': forms.NumberInput(attrs={'step': '0.01'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        data_pagamento = cleaned_data.get('data_pagamento')
        
        if status == 'PAGO' and not data_pagamento:
            self.add_error('data_pagamento', 'A data de pagamento é obrigatória quando o status é PAGO.')
        
        return cleaned_data

class ContaReceberForm(forms.ModelForm):
    valor = forms.DecimalField(
        min_value=0.01,
        error_messages={'min_value': 'O valor deve ser maior que zero.'},
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    class Meta:
        model = ContaReceber
        fields = ['cliente', 'valor', 'data_vencimento', 'status', 'data_recebimento', 'observacoes']
        widgets = {
            'data_vencimento': forms.DateInput(attrs={'type': 'date'}),
            'data_recebimento': forms.DateInput(attrs={'type': 'date'}),
            'valor': forms.NumberInput(attrs={'step': '0.01'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        data_recebimento = cleaned_data.get('data_recebimento')
        
        if status == 'RECEBIDO' and not data_recebimento:
            self.add_error('data_recebimento', 'A data de recebimento é obrigatória quando o status é RECEBIDO.')
        
        return cleaned_data
