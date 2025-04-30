from django.views.generic import TemplateView
from datetime import datetime, timedelta
from django.db.models import Sum
from django.utils import timezone
from producao.models import OrdemProducao
from estoque.models import SaldoEstoque
from comercial.models import Venda, Cliente, Fornecedor
from financeiro.models import ContaPagar, ContaReceber
import json

class HomeView(TemplateView):
    """
    Dashboard principal do sistema. 
    Apresenta visão geral de todas as áreas: produção, estoque, financeiro e comercial.
    """
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Data para referência nas consultas
        context['today'] = timezone.now().date()
        
        # Painel de Produção - Ordens em andamento
        context['ordens_andamento'] = OrdemProducao.objects.filter(status='EM_PRODUCAO')
        
        # Resumo de ordens finalizadas no mês atual
        hoje = timezone.now().date()
        ordens_finalizadas = OrdemProducao.objects.filter(
            status='FINALIZADA',
            data_fim__month=hoje.month,
            data_fim__year=hoje.year
        )
        context['ordens_finalizadas_mes'] = ordens_finalizadas.count()
        
        # Dados para o gráfico de produção dos últimos 6 meses
        meses = []
        quantidades = []
        today = datetime.now().date()
        for i in range(6):
            month = today - timedelta(days=30*i)
            meses.insert(0, month.strftime('%b/%Y'))
            
            # Busca ordens finalizadas em cada mês
            qs = OrdemProducao.objects.filter(
                status='FINALIZADA',
                data_fim__isnull=False,
                data_fim__month=month.month,
                data_fim__year=month.year
            )
            quantidades.insert(0, qs.count())
            
        # Prepara dados para o gráfico em JavaScript
        context['meses'] = json.dumps(meses)
        context['quantidades'] = json.dumps(quantidades)
        
        # Alertas de estoque abaixo do mínimo
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

        # Vendas em aberto (não finalizadas nem canceladas)
        context['vendas_nao_finalizadas'] = Venda.objects.exclude(status__in=['FECHADA', 'CANCELADA'])

        # Contas vencidas no financeiro
        hoje = timezone.now().date()
        context['contas_pagar_vencidas'] = ContaPagar.objects.filter(status='PENDENTE', data_vencimento__lt=hoje)
        context['contas_receber_vencidas'] = ContaReceber.objects.filter(status='PENDENTE', data_vencimento__lt=hoje)

        # Indicadores financeiros do mês atual
        mes_atual = hoje.month
        ano_atual = hoje.year
        
        # Receita do mês atual
        receita_mensal = Venda.objects.filter(
            status='FECHADA',
            data_venda__month=mes_atual,
            data_venda__year=ano_atual
        ).aggregate(total=Sum('valor_total'))['total'] or 0
        context['receita_mensal'] = f"{receita_mensal:,.2f}"

        # Estatísticas gerais do sistema
        context['vendas_finalizadas_count'] = Venda.objects.filter(status='FECHADA').count()
        context['clientes_count'] = Cliente.objects.count()
        context['fornecedores_count'] = Fornecedor.objects.count()

        return context

class DashboardView(TemplateView):
    """
    Dashboard interno do sistema, acessível após o login.
    Ponto de entrada principal para usuários autenticados.
    """
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Adicionar dados do usuário ao contexto
        context['user'] = self.request.user
        today = timezone.now().date()
        
        # Resumo de estatísticas para o dashboard
        context['stats'] = {
            'ordens_em_producao': OrdemProducao.objects.filter(status='EM_PRODUCAO').count(),
            'alertas_estoque': SaldoEstoque.objects.filter(
                quantidade_atual__lt=SaldoEstoque.objects.values('materia_prima__estoque_minimo')
            ).count(),
            'vendas_hoje': Venda.objects.filter(
                data_venda__date=today
            ).count(),
            'contas_vencidas': ContaPagar.objects.filter(
                status='PENDENTE', 
                data_vencimento__lt=today
            ).count()
        }
        
        # Lista de atividades recentes
        context['ordens_recentes'] = OrdemProducao.objects.all().order_by('-id')[:5]
        context['vendas_recentes'] = Venda.objects.all().order_by('-data_venda')[:5]
        
        return context