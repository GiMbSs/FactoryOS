from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets

from ..models import Produto, ProdutoMateriaPrima, MateriaPrima, OrdemProducao
from ..serializers import ProdutoSerializer, MateriaPrimaSerializer, OrdemProducaoSerializer
from estoque.models import SaldoEstoque


class MateriaPrimaViewSet(viewsets.ModelViewSet):
    """
    API que oferece operações completas (CRUD) para matérias-primas.
    Endpoint: /api/materias-primas/
    """
    queryset = MateriaPrima.objects.all()
    serializer_class = MateriaPrimaSerializer


class ProdutoViewSet(viewsets.ModelViewSet):
    """
    API que oferece operações completas (CRUD) para produtos.
    Endpoint: /api/produtos/
    """
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer


class OrdemProducaoViewSet(viewsets.ModelViewSet):
    """
    API que oferece operações completas (CRUD) para ordens de produção.
    Endpoint: /api/ordens/
    """
    queryset = OrdemProducao.objects.all()
    serializer_class = OrdemProducaoSerializer


class ProdutoMateriasPrimasAPIView(View):
    """
    API especializada que retorna as matérias-primas necessárias para produzir
    determinada quantidade de um produto, verificando se há estoque suficiente.
    
    Endpoint: /api/produtos/{produto_id}/materias-primas/?quantidade={quantidade}
    
    Parâmetros:
    - produto_id: ID do produto a consultar
    - quantidade: Quantidade do produto a ser produzida (opcional, padrão=1)
    
    Retorna para cada matéria-prima:
    - nome da matéria-prima
    - quantidade total necessária
    - unidade de medida
    - estoque disponível
    - indicador se há estoque suficiente
    """
    def get(self, request, produto_id):
        quantidade = request.GET.get('quantidade', 1)
        try:
            quantidade = float(quantidade)
        except Exception:
            quantidade = 1
        
        # Busca todas as matérias-primas relacionadas ao produto
        materias_primas = ProdutoMateriaPrima.objects.filter(produto_id=produto_id)
        data = []
        
        # Calcula as quantidades necessárias e verifica o estoque
        for mp in materias_primas:
            quantidade_total = float(mp.quantidade_utilizada) * quantidade
            try:
                saldo = SaldoEstoque.objects.get(materia_prima=mp.materia_prima)
                estoque_disponivel = saldo.quantidade_atual
            except SaldoEstoque.DoesNotExist:
                estoque_disponivel = 0
                
            suficiente = estoque_disponivel >= quantidade_total
            data.append({
                'materia_prima': mp.materia_prima.nome,
                'quantidade_total': quantidade_total,
                'unidade': mp.materia_prima.unidade_medida,
                'estoque_disponivel': estoque_disponivel,
                'suficiente': suficiente,
            })
        return JsonResponse(data, safe=False)