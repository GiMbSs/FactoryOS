from django.http import JsonResponse
from django.views import View
from producao.models import Produto, ProdutoMateriaPrima
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from estoque.models import SaldoEstoque

class ProdutoMateriasPrimasAPIView(View):
    def get(self, request, produto_id):
        quantidade = request.GET.get('quantidade', 1)
        try:
            quantidade = float(quantidade)
        except Exception:
            quantidade = 1
        materias_primas = ProdutoMateriaPrima.objects.filter(produto_id=produto_id)
        data = []
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
