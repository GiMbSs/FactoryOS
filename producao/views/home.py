"""
View para a página inicial (home) do sistema.
"""
from django.views.generic import TemplateView
from datetime import timedelta
from django.db.models import Sum
from django.utils import timezone
import json

from producao.models import OrdemProducao
from estoque.models import SaldoEstoque
from comercial.models import Venda, Cliente, Fornecedor
from financeiro.models import ContaPagar, ContaReceber


class HomeView(TemplateView):
    """
    View principal para a página inicial do sistema.
    Integra informações de todos os módulos: Produção, Estoque, Comercial e Financeiro.
    """
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Adicionar a data atual usando timezone.localtime para obter a data local correta
        timezone_now = timezone.localtime(timezone.now())
        hoje = timezone_now.date()
        context['today'] = hoje
        
        # Produção
        context['ordens_andamento'] = OrdemProducao.objects.filter(status='EM_PRODUCAO')
        
        # Ordens finalizadas no mês atual (usando data_fim que é preenchida automaticamente)
        mes_atual = hoje.month
        ano_atual = hoje.year
        
        ordens_finalizadas = OrdemProducao.objects.filter(
            status='FINALIZADA',
            data_fim__month=mes_atual,
            data_fim__year=ano_atual
        )
        context['ordens_finalizadas_mes'] = ordens_finalizadas.count()
        
        # Gráfico produção mensal - usar timezone.localtime().date() para obter a data local correta
        meses = []
        quantidades = []
        today = timezone.localtime(timezone.now()).date()
        
        for i in range(6):
            month = today - timedelta(days=30*i)
            meses.insert(0, month.strftime('%b/%Y'))
            # Conta ordens finalizadas no mês, garantindo que data_fim existe
            qs = OrdemProducao.objects.filter(
                status='FINALIZADA',
                data_fim__isnull=False,
                data_fim__month=month.month,
                data_fim__year=month.year
            )
            quantidades.insert(0, qs.count())
            
        # Serializar os dados como JSON para o gráfico
        context['meses'] = json.dumps(meses)
        context['quantidades'] = json.dumps(quantidades)
        
        # Estoque
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
            for saldo in SaldoEstoque.objects.all()
            if saldo.quantidade_atual < (
                saldo.materia_prima.estoque_minimo 
                if saldo.materia_prima.estoque_minimo > 0 
                else saldo.calcular_estoque_minimo()
            )
        ]

        # Alerta de vendas não finalizadas
        context['vendas_nao_finalizadas'] = Venda.objects.exclude(status__in=['FECHADA', 'CANCELADA'])

        # Alertas financeiro - contas vencidas
        context['contas_pagar_vencidas'] = ContaPagar.objects.filter(
            status='PENDENTE', 
            data_vencimento__lt=hoje
        )
        context['contas_receber_vencidas'] = ContaReceber.objects.filter(
            status='PENDENTE', 
            data_vencimento__lt=hoje
        )

        # Dados financeiros
        # Receita mensal (vendas finalizadas no mês)
        receita_mensal = Venda.objects.filter(
            status='FECHADA',
            data_venda__month=mes_atual,
            data_venda__year=ano_atual
        ).aggregate(total=Sum('valor_total'))['total'] or 0
        context['receita_mensal'] = f"{receita_mensal:,.2f}"

        # Contagem de vendas finalizadas
        context['vendas_finalizadas_count'] = Venda.objects.filter(status='FECHADA').count()

        # Contagem de clientes e fornecedores
        context['clientes_count'] = Cliente.objects.count()
        context['fornecedores_count'] = Fornecedor.objects.count()

        return context