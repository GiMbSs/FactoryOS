"""
Funções auxiliares e views para modais do módulo producao.
"""
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from producao.models import TipoProduto, TipoMateriaPrima, MateriaPrima
from producao.forms import TipoProdutoForm, TipoMateriaPrimaForm


@login_required
@require_http_methods(["GET", "POST"])
def tipo_produto_modal(request):
    """View para criar ou editar um tipo de produto em um modal."""
    tipo_id = request.GET.get('id')
    
    if (tipo_id):
        tipo = TipoProduto.objects.get(id=tipo_id)
        title = f"Editar Tipo: {tipo.nome}"
    else:
        tipo = None
        title = "Novo Tipo de Produto"
    
    if request.method == "POST":
        form = TipoProdutoForm(request.POST, instance=tipo)
        if form.is_valid():
            tipo = form.save()
            return JsonResponse({
                'success': True,
                'id': tipo.id,
                'nome': tipo.nome,
                'message': f"Tipo de produto '{tipo.nome}' salvo com sucesso."
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors.as_json()
            })
    else:
        form = TipoProdutoForm(instance=tipo)
    
    html = render_to_string('producao/includes/tipo_produto_modal.html', {
        'form': form,
        'tipo': tipo,
        'title': title
    }, request=request)
    
    return JsonResponse({
        'html': html,
        'title': title
    })


@login_required
@require_http_methods(["GET", "POST"])
def tipo_materia_prima_modal(request):
    """View para criar ou editar um tipo de matéria-prima em um modal."""
    tipo_id = request.GET.get('id')
    
    if (tipo_id):
        tipo = TipoMateriaPrima.objects.get(id=tipo_id)
        title = f"Editar Tipo de Matéria-Prima: {tipo.nome}"
    else:
        tipo = None
        title = "Novo Tipo de Matéria-Prima"
    
    if request.method == "POST":
        form = TipoMateriaPrimaForm(request.POST, instance=tipo)
        if form.is_valid():
            tipo = form.save()
            return JsonResponse({
                'success': True,
                'id': tipo.id,
                'nome': tipo.nome,
                'message': f"Tipo de matéria-prima '{tipo.nome}' salvo com sucesso."
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors.as_json()
            })
    else:
        form = TipoMateriaPrimaForm(instance=tipo)
    
    html = render_to_string('producao/includes/tipo_materia_prima_modal.html', {
        'form': form,
        'tipo': tipo,
        'title': title
    }, request=request)
    
    return JsonResponse({
        'html': html,
        'title': title
    })


@login_required
def get_materia_prima_info(request, materia_prima_id):
    """Retorna informações da matéria-prima para uso via AJAX"""
    try:
        materia_prima = MateriaPrima.objects.get(id=materia_prima_id)
        
        # Determina a unidade de medida a partir do relacionamento ou do campo legacy
        unidade_sigla = None
        if materia_prima.unidade:
            unidade_sigla = materia_prima.unidade.sigla
        else:
            # Mapeia os valores antigos para siglas sensíveis
            mapeamento_unidades = {
                'KG': 'kg',
                'METRO': 'm',
                'UNIDADE': 'un',
            }
            unidade_sigla = mapeamento_unidades.get(materia_prima.unidade_medida, 'un')
        
        return JsonResponse({
            'success': True,
            'unidade': unidade_sigla,
            'nome': materia_prima.nome,
            'custo': float(materia_prima.custo_unitario)
        })
    except MateriaPrima.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Matéria-prima não encontrada'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)