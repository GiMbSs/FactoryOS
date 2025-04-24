from django.views.generic import TemplateView
from datetime import datetime, timedelta
from producao.models import OrdemProducao
from estoque.models import SaldoEstoque
from comercial.models import Venda
from financeiro.models import ContaPagar, ContaReceber

class HomeView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Produção
        context['ordens_andamento'] = OrdemProducao.objects.filter(status='EM_ANDAMENTO')
        # Gráfico produção mensal
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
        # Estoque
        context['alertas_estoque'] = [
            {
                'materia_prima': saldo.materia_prima.nome,
                'quantidade_atual': saldo.quantidade_atual,
                'unidade_medida': saldo.materia_prima.unidade_medida,
                'estoque_minimo': round(saldo.materia_prima.estoque_minimo if saldo.materia_prima.estoque_minimo > 0 else saldo.calcular_estoque_minimo(), 2)
            }
            for saldo in SaldoEstoque.objects.all()
            if saldo.quantidade_atual < (saldo.materia_prima.estoque_minimo if saldo.materia_prima.estoque_minimo > 0 else saldo.calcular_estoque_minimo())
        ]

        # Alerta de vendas não finalizadas
        context['vendas_nao_finalizadas'] = Venda.objects.exclude(status__in=['FECHADA', 'CANCELADA'])

        # Alertas financeiro - contas vencidas
        from django.utils import timezone
        hoje = timezone.now().date()
        context['contas_pagar_vencidas'] = ContaPagar.objects.filter(status='PENDENTE', data_vencimento__lt=hoje)
        context['contas_receber_vencidas'] = ContaReceber.objects.filter(status='PENDENTE', data_vencimento__lt=hoje)
        return context
