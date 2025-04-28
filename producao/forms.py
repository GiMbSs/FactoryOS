from django import forms
from .models import OrdemProducao, Produto, MateriaPrima, ProdutoMateriaPrima, TipoProduto, TipoMateriaPrima

class OrdemProducaoForm(forms.ModelForm):
    class Meta:
        model = OrdemProducao
        fields = ['produto', 'quantidade', 'status', 'responsavel']
        # data_inicio será preenchido automaticamente no model/view

class TipoProdutoForm(forms.ModelForm):
    class Meta:
        model = TipoProduto
        fields = ['nome', 'descricao']  # Removidos 'icone' e 'cor'
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

class TipoMateriaPrimaForm(forms.ModelForm):
    class Meta:
        model = TipoMateriaPrima
        fields = ['nome', 'descricao']  # Removidos 'icone' e 'cor'
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }

class MateriaPrimaForm(forms.ModelForm):
    class Meta:
        model = MateriaPrima
        fields = ['nome', 'tipo_materia_prima', 'descricao', 'unidade_medida', 
                  'custo_unitario', 'estoque_minimo', 'ativo']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo_materia_prima'].queryset = TipoMateriaPrima.objects.filter(ativo=True)
        # Se não tiver tipos cadastrados, mostra uma mensagem
        if not self.fields['tipo_materia_prima'].queryset.exists():
            self.fields['tipo_materia_prima'].help_text = "Não existem tipos de matéria-prima cadastrados. Clique no botão '+' para adicionar um novo tipo."
            
    def save(self, commit=True):
        materia_prima = super().save(commit=False)
        
        # Se tiver um tipo_materia_prima selecionado, atualiza o campo tipo para compatibilidade
        if materia_prima.tipo_materia_prima:
            # Tenta encontrar o valor do tipo antigo mais próximo ao novo selecionado
            tipo_nome = materia_prima.tipo_materia_prima.nome.upper()
            tipo_mapeamento = {
                'MADEIRA': 'MADEIRA_BRUTA',
                'VARETA': 'VARETA_MADEIRA',
                'MALHA': 'TECIDO_MALHA',
                'PANO': 'TECIDO_PANO_CRU',
                'PLASTICO': 'CABO_PLASTICO',
            }
            
            # Percorre o mapeamento e atribui o tipo mais próximo
            for chave, valor in tipo_mapeamento.items():
                if chave in tipo_nome:
                    materia_prima.tipo = valor
                    break
            else:
                # Tipo padrão caso nenhum corresponda
                materia_prima.tipo = 'OUTROS'
        
        if commit:
            materia_prima.save()
        return materia_prima

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
