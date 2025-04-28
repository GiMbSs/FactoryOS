from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from core.views import registrar_log, LoggingMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template, render_to_string
from xhtml2pdf import pisa
from rest_framework import viewsets
from .models import OrdemProducao, Produto, MateriaPrima, TipoProduto, TipoMateriaPrima
from .forms import OrdemProducaoForm, ProdutoForm, MateriaPrimaForm, TipoProdutoForm, TipoMateriaPrimaForm
from .serializers import (
    ProdutoSerializer,
    MateriaPrimaSerializer,
    OrdemProducaoSerializer
)
import logging
from datetime import datetime, timedelta
from django.db import models
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

# Importar views dos módulos reorganizados para manter compatibilidade
from .views.produtos import *
from .views.materias_primas import *
from .views.ordens import *

class MateriaPrimaViewSet(viewsets.ModelViewSet):
    queryset = MateriaPrima.objects.all()
    serializer_class = MateriaPrimaSerializer

class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer

class OrdemProducaoViewSet(viewsets.ModelViewSet):
    queryset = OrdemProducao.objects.all()
    serializer_class = OrdemProducaoSerializer

logger = logging.getLogger(__name__)

from django.contrib.auth.mixins import LoginRequiredMixin

class ProdutoListView(LoginRequiredMixin, ListView):
    model = Produto
    template_name = 'producao/produto_list.html'
    context_object_name = 'produtos'
    ordering = ['nome']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Usa o serviço para obter estatísticas de forma mais organizada
        from .services import EstatisticasService
        estatisticas = EstatisticasService.obter_estatisticas_produto()
        
        # Adiciona contagens por tipo de produto
        context['total_produtos'] = estatisticas['total_produtos']
        context['produtos_madeira'] = estatisticas['produtos_por_tipo']['madeira']
        context['produtos_plastico'] = estatisticas['produtos_por_tipo']['plastico']
        context['produtos_tecido'] = estatisticas['produtos_por_tipo']['tecido']
        context['produtos_misto'] = estatisticas['produtos_por_tipo']['misto']
        
        # Custo médio dos produtos
        context['custo_medio'] = estatisticas['custo_medio']
            
        return context

from .forms import ProdutoMateriaPrimaFormSet

class ProdutoCreateView(LoginRequiredMixin, LoggingMixin, CreateView):
    model = Produto
    form_class = ProdutoForm
    template_name = 'producao/cadastro_produto.html'
    success_url = reverse_lazy('producao:produto_list')
    
    # Configurações para o LoggingMixin
    log_module = 'Produção'
    log_create_message = "Cadastrou novo produto: {}"
    success_message = "Produto cadastrado com sucesso!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['materias_formset'] = ProdutoMateriaPrimaFormSet(self.request.POST)
        else:
            context['materias_formset'] = ProdutoMateriaPrimaFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        materias_formset = context['materias_formset']
        if materias_formset.is_valid():
            self.object = form.save()
            materias_formset.instance = self.object
            materias_formset.save()
            # O registro de log será feito pelo LoggingMixin
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

class ProdutoUpdateView(LoginRequiredMixin, LoggingMixin, UpdateView):
    model = Produto
    form_class = ProdutoForm
    template_name = 'producao/cadastro_produto.html'
    success_url = reverse_lazy('producao:produto_list')
    
    # Configurações para o LoggingMixin
    log_module = 'Produção'
    log_update_message = "Editou produto: {}"
    success_message = "Produto atualizado com sucesso!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['materias_formset'] = ProdutoMateriaPrimaFormSet(self.request.POST, instance=self.object)
        else:
            context['materias_formset'] = ProdutoMateriaPrimaFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        materias_formset = context['materias_formset']
        if materias_formset.is_valid():
            self.object = form.save()
            materias_formset.instance = self.object
            materias_formset.save()
            # O registro de log será feito pelo LoggingMixin
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

class ProdutoDeleteView(LoginRequiredMixin, LoggingMixin, DeleteView):
    model = Produto
    template_name = 'producao/confirmar_exclusao_produto.html'
    success_url = reverse_lazy('producao:produto_list')
    
    # Configurações para o LoggingMixin
    log_module = 'Produção'
    log_delete_message = "Excluiu produto: {}"
    success_message = "Produto excluído com sucesso!"

class MateriaPrimaListView(LoginRequiredMixin, ListView):
    model = MateriaPrima
    template_name = 'producao/materiaprima_list.html'
    context_object_name = 'materias_primas'
    ordering = ['nome']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Adiciona contagens por tipo
        context['total_materias'] = MateriaPrima.objects.count()
        context['materias_ativas'] = MateriaPrima.objects.filter(ativo=True).count()
        
        # Contagens por tipo
        context['materias_madeira'] = MateriaPrima.objects.filter(tipo='MADEIRA_BRUTA').count() + \
                                     MateriaPrima.objects.filter(tipo='VARETA_MADEIRA').count()
        context['materias_tecido'] = MateriaPrima.objects.filter(tipo='TECIDO_MALHA').count() + \
                                    MateriaPrima.objects.filter(tipo='TECIDO_PANO_CRU').count()
        context['materias_plastico'] = MateriaPrima.objects.filter(tipo='CABO_PLASTICO').count()
        
        # Estatísticas adicionais
        from django.db.models import Sum, Avg
        from django.utils import timezone
        
        # Custo total das matérias-primas
        context['custo_total'] = MateriaPrima.objects.aggregate(Sum('custo_unitario'))['custo_unitario__sum'] or 0
        
        # Verifica se há matérias-primas abaixo do estoque mínimo
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
    model = MateriaPrima
    form_class = MateriaPrimaForm
    template_name = 'producao/cadastro_materiaprima.html'
    success_url = reverse_lazy('producao:materiaprima_list')
    
    # Configurações para o LoggingMixin
    log_module = 'Produção'
    log_create_message = "Cadastrou nova matéria-prima: {}"
    success_message = "Matéria-prima cadastrada com sucesso!"

class MateriaPrimaUpdateView(LoginRequiredMixin, LoggingMixin, UpdateView):
    model = MateriaPrima
    form_class = MateriaPrimaForm
    template_name = 'producao/cadastro_materiaprima.html'
    success_url = reverse_lazy('producao:materiaprima_list')
    
    # Configurações para o LoggingMixin
    log_module = 'Produção'
    log_update_message = "Editou matéria-prima: {}"
    success_message = "Matéria-prima atualizada com sucesso!"

class MateriaPrimaDeleteView(LoginRequiredMixin, LoggingMixin, DeleteView):
    model = MateriaPrima
    template_name = 'producao/confirmar_exclusao_materiaprima.html'
    success_url = reverse_lazy('producao:materiaprima_list')
    
    # Configurações para o LoggingMixin
    log_module = 'Produção'
    log_delete_message = "Excluiu matéria-prima: {}"
    success_message = "Matéria-prima excluída com sucesso!"

class DashboardView(LoginRequiredMixin, ListView):
    template_name = 'producao/dashboard.html'
    model = OrdemProducao
    context_object_name = 'ordens_andamento'

    def get_queryset(self):
        return OrdemProducao.objects.filter(status__in=['EM_PRODUCAO', 'FINALIZADA'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Dados para o gráfico de produção mensal
        meses = []
        quantidades = []
        today = datetime.now()
        for i in range(6):
            month = today - timedelta(days=30*i)
            meses.insert(0, month.strftime('%b/%Y'))
            quantidades.insert(0, OrdemProducao.objects.filter(
                data_fim__month=month.month,
                data_fim__year=month.year,
                status='FINALIZADA'
            ).count())
        
        # Serializar os dados como JSON para o gráfico
        import json
        context['meses'] = json.dumps(meses)
        context['quantidades'] = json.dumps(quantidades)

        # Totais do mês atual
        now = datetime.now()
        # Considera apenas ordens com data preenchida
        context['total_ordens_mes'] = OrdemProducao.objects.filter(
            data_inicio__isnull=False,
            data_inicio__month=now.month,
            data_inicio__year=now.year
        ).count() or 0
        context['total_produzido_mes'] = OrdemProducao.objects.filter(
            data_fim__isnull=False,
            data_fim__month=now.month,
            data_fim__year=now.year,
            status='FINALIZADA'
        ).count() or 0

        # Alertas de estoque usando o serviço
        from .services import EstoqueService
        saldos_alerta = EstoqueService.obter_alertas_estoque()
        
        # Formata os dados para o template
        context['alertas_estoque'] = [
            {
                'materia_prima': saldo.materia_prima.nome,
                'quantidade_atual': saldo.quantidade_atual,
                'unidade_medida': saldo.materia_prima.unidade_medida,
                'estoque_minimo': round(
                    saldo.materia_prima.estoque_minimo 
                    if saldo.materia_prima.estoque_minimo > 0 
                    else saldo.calcular_estoque_minimo(), 
                    2
                )
            }
            for saldo in saldos_alerta
        ]
        
        return context

class OrdemProducaoListView(LoginRequiredMixin, ListView):
    model = OrdemProducao
    template_name = 'producao/ordemproducao_list.html'
    paginate_by = 10
    ordering = ['-data_inicio']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Adiciona contagens por status
        context['total_ordens'] = OrdemProducao.objects.count()
        context['ordens_planejadas'] = OrdemProducao.objects.filter(status='PLANEJADA').count()
        context['ordens_em_producao'] = OrdemProducao.objects.filter(status='EM_PRODUCAO').count()
        context['ordens_finalizadas'] = OrdemProducao.objects.filter(status='FINALIZADA').count()
        context['ordens_canceladas'] = OrdemProducao.objects.filter(status='CANCELADA').count()
        
        # Adiciona estatísticas adicionais
        from django.utils import timezone
        hoje = timezone.now().date()
        mes_atual = timezone.now().month
        ano_atual = timezone.now().year
        
        context['ordens_mes_atual'] = OrdemProducao.objects.filter(
            data_inicio__month=mes_atual,
            data_inicio__year=ano_atual
        ).count()
        
        context['ordens_finalizadas_mes'] = OrdemProducao.objects.filter(
            status='FINALIZADA',
            data_fim__month=mes_atual,
            data_fim__year=ano_atual
        ).count()
        
        return context

class OrdemProducaoCreateView(LoginRequiredMixin, LoggingMixin, CreateView):
    model = OrdemProducao
    form_class = OrdemProducaoForm
    template_name = 'producao/ordemproducao_form.html'
    success_url = reverse_lazy('producao:lista_ordens')
    
    # Configurações para o LoggingMixin
    log_module = 'Produção'
    log_create_message = "Criou ordem de produção: {}"
    success_message = "Ordem de produção criada com sucesso!"

    def form_valid(self, form):
        response = super().form_valid(form)
        logger.info(f"Nova ordem de produção criada: {self.object}")
        return response

class OrdemProducaoDetailView(LoginRequiredMixin, DetailView):
    model = OrdemProducao
    template_name = 'producao/ordemproducao_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from decimal import Decimal
        custo_unitario = self.object.produto.calcular_custo()
        if not isinstance(custo_unitario, Decimal):
            custo_unitario = Decimal(str(custo_unitario))
        quantidade = self.object.quantidade
        context['custo_total'] = custo_unitario * Decimal(quantidade)
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('format') == 'pdf':
            template = get_template('producao/ordemproducao_pdf.html')
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'filename=ordem_producao_{self.object.id}.pdf'
            
            pisa_status = pisa.CreatePDF(html, dest=response)
            if pisa_status.err:
                return HttpResponse('Erro ao gerar PDF')
            return response
        
        return super().render_to_response(context, **response_kwargs)

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

# Adicionar API para obter unidade de medida de uma matéria-prima
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
