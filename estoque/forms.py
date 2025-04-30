from django import forms
from .models import SaldoEstoque
from producao.models import MateriaPrima
from django.core.validators import MinValueValidator
from decimal import Decimal

class SaldoEstoqueForm(forms.ModelForm):
    quantidade_atual = forms.DecimalField(
        min_value=0, 
        error_messages={'min_value': 'A quantidade não pode ser negativa.'},
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    class Meta:
        model = SaldoEstoque
        fields = ['materia_prima', 'quantidade_atual']
        widgets = {
            'materia_prima': forms.Select(attrs={'class': 'form-select'}),
            'quantidade_atual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class MateriaPrimaForm(forms.ModelForm):
    quantidade_estoque = forms.DecimalField(
        label='Quantidade em Estoque', 
        required=False, 
        min_value=0,
        error_messages={'min_value': 'A quantidade não pode ser negativa.'}
    )

    class Meta:
        model = MateriaPrima
        fields = ['nome', 'descricao', 'tipo', 'unidade_medida', 'custo_unitario', 'estoque_minimo', 'ativo']
        
    def clean_custo_unitario(self):
        custo = self.cleaned_data.get('custo_unitario')
        if custo and custo < 0:
            raise forms.ValidationError("O custo unitário não pode ser negativo.")
        return custo
