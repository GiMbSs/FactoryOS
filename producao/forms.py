from django import forms
from .models import OrdemProducao, Produto, MateriaPrima, ProdutoMateriaPrima, TipoProduto

class OrdemProducaoForm(forms.ModelForm):
    class Meta:
        model = OrdemProducao
        fields = ['produto', 'quantidade', 'status', 'responsavel']
        # data_inicio será preenchido automaticamente no model/view

class TipoProdutoForm(forms.ModelForm):
    class Meta:
        model = TipoProduto
        fields = ['nome', 'descricao', 'icone', 'cor']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'descricao', 'codigo_sku', 'tipo_produto']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo_produto'].queryset = TipoProduto.objects.filter(ativo=True)
        # Se não tiver tipos cadastrados, mostra uma mensagem
        if not self.fields['tipo_produto'].queryset.exists():
            self.fields['tipo_produto'].help_text = "Não existem tipos de produto cadastrados. Clique no botão '+' para adicionar um novo tipo."

class MateriaPrimaForm(forms.ModelForm):
    class Meta:
        model = MateriaPrima
        fields = ['nome', 'descricao', 'tipo', 'unidade_medida', 'custo_unitario', 'estoque_minimo']

class ProdutoMateriaPrimaForm(forms.ModelForm):
    class Meta:
        model = ProdutoMateriaPrima
        fields = ['materia_prima', 'quantidade_utilizada', 'observacoes']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Para usar no template e obter a unidade de medida de cada matéria prima
        if hasattr(self, 'instance') and self.instance and self.instance.materia_prima_id:
            self.materia_prima_unidade = self.instance.materia_prima.unidade_medida
        else:
            self.materia_prima_unidade = None

from django.forms import inlineformset_factory
ProdutoMateriaPrimaFormSet = inlineformset_factory(
    Produto,
    ProdutoMateriaPrima,
    form=ProdutoMateriaPrimaForm,
    extra=1,
    can_delete=True
)
