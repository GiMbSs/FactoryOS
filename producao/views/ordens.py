from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from rest_framework import viewsets
from datetime import datetime, timedelta
import logging

from core.views import LoggingMixin, registrar_log
from ..models import OrdemProducao
from ..forms import OrdemProducaoForm
from ..serializers import OrdemProducaoSerializer

logger = logging.getLogger(__name__)


class OrdemProducaoViewSet(viewsets.ModelViewSet):
    """API REST para gerenciamento de ordens de produção"""
    queryset = OrdemProducao.objects.all()
    serializer_class = OrdemProducaoSerializer


class DashboardView(LoginRequiredMixin, ListView):
    """
    Dashboard específico do módulo de produção.
    Apresenta gráficos, indicadores e alertas de estoque.
    """
    template_name = 'producao/dashboard.html'
    model = OrdemProducao
    context_object_name = 'ordens_andamento'

    def get_queryset(self):
        return OrdemProducao.objects.filter(status__in=['EM_PRODUCAO', 'FINALIZADA'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Gráfico de produção dos últimos 6 meses
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
        
        context['meses'] = meses
        context['quantidades'] = quantidades

        # Indicadores do mês atual
        now = datetime.now()
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

        # Alertas de matérias-primas com estoque baixo
        from ..services import EstoqueService
        saldos_alerta = EstoqueService.obter_alertas_estoque()
        
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
    """
    Lista todas as ordens de produção do sistema com filtros por status.
    Inclui estatísticas sobre as ordens cadastradas.
    """
    model = OrdemProducao
    template_name = 'producao/ordemproducao_list.html'
    paginate_by = 10
    ordering = ['-data_inicio']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estatísticas por status das ordens
        context['total_ordens'] = OrdemProducao.objects.count()
        context['ordens_planejadas'] = OrdemProducao.objects.filter(status='PLANEJADA').count()
        context['ordens_em_producao'] = OrdemProducao.objects.filter(status='EM_PRODUCAO').count()
        context['ordens_finalizadas'] = OrdemProducao.objects.filter(status='FINALIZADA').count()
        context['ordens_canceladas'] = OrdemProducao.objects.filter(status='CANCELADA').count()
        
        # Estatísticas do mês atual
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
    """
    Criação de novas ordens de produção.
    """
    model = OrdemProducao
    form_class = OrdemProducaoForm
    template_name = 'producao/ordemproducao_form.html'
    success_url = reverse_lazy('producao:lista_ordens')
    
    log_module = 'Produção'
    log_create_message = "Criou ordem de produção: {}"
    success_message = "Ordem de produção criada com sucesso!"

    def form_valid(self, form):
        response = super().form_valid(form)
        logger.info(f"Nova ordem de produção criada: {self.object}")
        return response


class OrdemProducaoUpdateView(LoginRequiredMixin, UpdateView):
    """
    Edição de ordens de produção existentes.
    Inclui tratamento de erros de validação.
    """
    model = OrdemProducao
    form_class = OrdemProducaoForm
    template_name = 'producao/ordemproducao_edit.html'
    success_url = reverse_lazy('producao:lista_ordens')

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            registrar_log(self.request, 'Produção', f"Editou ordem de produção: {self.object}")
            messages.success(self.request, 'Ordem de produção atualizada com sucesso!')
            return response
        except Exception as e:
            from django.core.exceptions import ValidationError
            if isinstance(e, ValidationError):
                for msg in e.messages:
                    messages.error(self.request, msg)
                return self.form_invalid(form)
            raise

    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao atualizar a ordem de produção. Verifique os dados informados.')
        return super().form_invalid(form)


class OrdemProducaoDeleteView(LoginRequiredMixin, DeleteView):
    """
    Exclusão de ordens de produção.
    """
    model = OrdemProducao
    template_name = 'producao/ordemproducao_delete.html'
    success_url = reverse_lazy('producao:lista_ordens')
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        response = super().delete(request, *args, **kwargs)
        registrar_log(request, 'Produção', f"Excluiu ordem de produção: {obj}")
        messages.success(self.request, 'Ordem de produção excluída com sucesso!')
        return response


class OrdemProducaoDetailView(LoginRequiredMixin, DetailView):
    """
    Visualização detalhada de uma ordem de produção.
    Permite também exportar para PDF.
    """
    model = OrdemProducao
    template_name = 'producao/ordemproducao_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from decimal import Decimal
        
        # Calcula o custo total da ordem baseado nas matérias-primas
        custo_unitario = self.object.produto.calcular_custo()
        if not isinstance(custo_unitario, Decimal):
            custo_unitario = Decimal(str(custo_unitario))
        quantidade = self.object.quantidade
        context['custo_total'] = custo_unitario * Decimal(quantidade)
        return context

    def render_to_response(self, context, **response_kwargs):
        # Exportação para PDF quando solicitado
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