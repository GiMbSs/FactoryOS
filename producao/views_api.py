from django.http import JsonResponse
from django.views import View
from producao.models import Produto, ProdutoMateriaPrima
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

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
            data.append({
                'materia_prima': mp.materia_prima.nome,
                'quantidade_total': float(mp.quantidade_utilizada) * quantidade,
                'unidade': mp.materia_prima.unidade_medida
            })
        return JsonResponse(data, safe=False)
