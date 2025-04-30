"""
Views para listagem de itens de estoque.
"""
from django.views.generic import TemplateView

from producao.models import MateriaPrima, Produto
from estoque.models import ProdutoEstoque


class EstoqueListView(TemplateView):
    """
    View principal para listagem de materiais e produtos em estoque.
    """
    template_name = 'estoque/estoque_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Listar todas as matérias-primas
        context['materias_primas'] = MateriaPrima.objects.all()
        
        # Listar produtos com seus respectivos saldos em estoque
        produtos = Produto.objects.all()
        produtos_com_estoque = []
        
        for produto in produtos:
            try:
                saldo = ProdutoEstoque.objects.get(produto=produto)
                quantidade = saldo.quantidade_atual
            except ProdutoEstoque.DoesNotExist:
                quantidade = 0
                
            produtos_com_estoque.append({
                'produto': produto,
                'quantidade_estoque': quantidade
            })
            
        context['produtos_acabados'] = produtos_com_estoque
        
        return context