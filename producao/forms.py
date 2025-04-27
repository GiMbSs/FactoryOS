from django import forms
from .models import OrdemProducao, Produto, MateriaPrima, ProdutoMateriaPrima

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

class ProdutoMateriaPrimaForm(forms.ModelForm):
    class Meta:
        model = ProdutoMateriaPrima
        fields = ['materia_prima', 'quantidade_utilizada', 'observacoes']

from django.forms import inlineformset_factory
ProdutoMateriaPrimaFormSet = inlineformset_factory(
    Produto,
    ProdutoMateriaPrima,
    form=ProdutoMateriaPrimaForm,
    extra=1,
    can_delete=True
)
