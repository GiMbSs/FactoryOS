from django import forms
from .models import OrdemProducao, Produto, MateriaPrima

class OrdemProducaoForm(forms.ModelForm):
    class Meta:
        model = OrdemProducao
        fields = ['produto', 'quantidade', 'status', 'responsavel']
        # data_inicio será preenchido automaticamente no model/view

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'descricao', 'codigo_sku', 'tipo']

class MateriaPrimaForm(forms.ModelForm):
    class Meta:
        model = MateriaPrima
        fields = ['nome', 'descricao', 'tipo', 'unidade_medida', 'custo_unitario', 'estoque_minimo']
