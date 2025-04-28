from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework import viewsets
from django.db import models

from core.views import LoggingMixin
from ..models import MateriaPrima
from ..forms import MateriaPrimaForm
from ..serializers import MateriaPrimaSerializer


class MateriaPrimaViewSet(viewsets.ModelViewSet):
    """API REST para gerenciamento de matérias-primas"""
    queryset = MateriaPrima.objects.all()
    serializer_class = MateriaPrimaSerializer


class MateriaPrimaListView(LoginRequiredMixin, ListView):
    """
    Exibe a listagem de matérias-primas cadastradas com estatísticas por tipo.
    Inclui indicadores sobre custos e alertas de estoque mínimo.
    """
    model = MateriaPrima
    template_name = 'producao/materiaprima_list.html'
    context_object_name = 'materias_primas'
    ordering = ['nome']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estatísticas gerais
        context['total_materias'] = MateriaPrima.objects.count()
        context['materias_ativas'] = MateriaPrima.objects.filter(ativo=True).count()
        
        # Contagens por categoria de material
        context['materias_madeira'] = MateriaPrima.objects.filter(tipo='MADEIRA_BRUTA').count() + \
                                     MateriaPrima.objects.filter(tipo='VARETA_MADEIRA').count()
        context['materias_tecido'] = MateriaPrima.objects.filter(tipo='TECIDO_MALHA').count() + \
                                    MateriaPrima.objects.filter(tipo='TECIDO_PANO_CRU').count()
        context['materias_plastico'] = MateriaPrima.objects.filter(tipo='CABO_PLASTICO').count()
        
        # Informações financeiras
        from django.db.models import Sum
        context['custo_total'] = MateriaPrima.objects.aggregate(Sum('custo_unitario'))['custo_unitario__sum'] or 0
        
        # Alertas de estoque
        try:
            from estoque.models import SaldoEstoque
            context['materias_abaixo_minimo'] = SaldoEstoque.objects.filter(
                quantidade_atual__lt=models.F('materia_prima__estoque_minimo'),
                materia_prima__estoque_minimo__gt=0
            ).count()
        except ImportError:
            context['materias_abaixo_minimo'] = 0
        
        return context


class MateriaPrimaCreateView(LoginRequiredMixin, LoggingMixin, CreateView):
    """
    Cadastro de novas matérias-primas.
    Registra automaticamente no log do sistema.
    """
    model = MateriaPrima
    form_class = MateriaPrimaForm
    template_name = 'producao/cadastro_materiaprima.html'
    success_url = reverse_lazy('producao:materiaprima_list')
    
    log_module = 'Produção'
    log_create_message = "Cadastrou nova matéria-prima: {}"
    success_message = "Matéria-prima cadastrada com sucesso!"


class MateriaPrimaUpdateView(LoginRequiredMixin, LoggingMixin, UpdateView):
    """
    Edição de matérias-primas existentes.
    """
    model = MateriaPrima
    form_class = MateriaPrimaForm
    template_name = 'producao/cadastro_materiaprima.html'
    success_url = reverse_lazy('producao:materiaprima_list')
    
    log_module = 'Produção'
    log_update_message = "Editou matéria-prima: {}"
    success_message = "Matéria-prima atualizada com sucesso!"


class MateriaPrimaDeleteView(LoginRequiredMixin, LoggingMixin, DeleteView):
    """
    Exclusão de matérias-primas.
    """
    model = MateriaPrima
    template_name = 'producao/confirmar_exclusao_materiaprima.html'
    success_url = reverse_lazy('producao:materiaprima_list')
    
    log_module = 'Produção'
    log_delete_message = "Excluiu matéria-prima: {}"
    success_message = "Matéria-prima excluída com sucesso!"


@login_required
def get_materia_prima_info(request, materia_prima_id):
    """
    Endpoint para obter informações da matéria-prima via Ajax.
    
    Usado principalmente na tela de cadastro de produtos para
    preencher informações de unidade de medida e custo quando
    o usuário seleciona uma matéria-prima.
    """
    try:
        materia_prima = MateriaPrima.objects.get(id=materia_prima_id)
        
        # Determina a unidade de medida considerando o modelo atual ou legado
        unidade_sigla = None
        if hasattr(materia_prima, 'unidade') and materia_prima.unidade:
            unidade_sigla = materia_prima.unidade.sigla
        else:
            # Normaliza valores antigos para o padrão atual
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