# Importar views específicas de cada módulo
from .produtos import *
from .materias_primas import *
from .ordens import *

# Importar funções específicas do views.py principal
# A estrutura do projeto possui tanto um views.py quanto um pacote views/
import os
import sys
import django
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.template.loader import render_to_string

# Função para o modal de tipo de matéria-prima
@login_required
@require_http_methods(["GET", "POST"])
def tipo_materia_prima_modal(request):
    """View para criar ou editar um tipo de matéria-prima em um modal."""
    from producao.models import TipoMateriaPrima
    from producao.forms import TipoMateriaPrimaForm
    
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