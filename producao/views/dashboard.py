"""
Views para o dashboard do módulo de produção.
"""
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from datetime import datetime, timedelta

from producao.models import OrdemProducao


class DashboardView(LoginRequiredMixin, ListView):
    """
    View principal para dashboard de produção.
    Mostra indicadores, gráficos e alertas relacionados à produção.
    """
    template_name = 'producao/dashboard.html'
    model = OrdemProducao
    context_object_name = 'ordens_andamento'

    def get_queryset(self):
        return OrdemProducao.objects.filter(status__in=['EM_PRODUCAO', 'FINALIZADA'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
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
        
        context['meses'] = json.dumps(meses)
        context['quantidades'] = json.dumps(quantidades)

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

        from producao.services import EstoqueService
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