from django import forms
from .models import SaldoEstoque
from producao.models import MateriaPrima

class SaldoEstoqueForm(forms.ModelForm):
    class Meta:
        model = SaldoEstoque
        fields = ['materia_prima', 'quantidade_atual']
        widgets = {
            'materia_prima': forms.Select(attrs={'class': 'form-select'}),
            'quantidade_atual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class MateriaPrimaForm(forms.ModelForm):
    quantidade_estoque = forms.DecimalField(label='Quantidade em Estoque', required=False, min_value=0)

    class Meta:
        model = MateriaPrima
        fields = ['nome', 'descricao', 'tipo', 'unidade_medida', 'custo_unitario', 'estoque_minimo', 'ativo']
