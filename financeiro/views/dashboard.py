"""
Views para o dashboard do módulo financeiro.
"""
from django.views.generic import ListView
from django.utils import timezone
import datetime

from financeiro.models import ContaPagar, ContaReceber
from django.db import models


class DashboardView(ListView):
    """
    View para exibição do dashboard financeiro com indicadores e métricas.
    """
    template_name = 'financeiro/dashboard.html'
    model = ContaPagar

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        timezone_now = timezone.localtime(timezone.now())
        hoje = timezone_now.date()
        mes_atual = hoje.month
        ano_atual = hoje.year
        
        context['contas_pagar_pendentes'] = ContaPagar.objects.filter(status='PENDENTE').count()
        context['contas_pagar_pagas'] = ContaPagar.objects.filter(status='PAGO').count()
        context['contas_receber_pendentes'] = ContaReceber.objects.filter(status='PENDENTE').count()
        context['contas_receber_recebidas'] = ContaReceber.objects.filter(status='RECEBIDO').count()
        context['valor_pagar_pendente'] = ContaPagar.objects.filter(status='PENDENTE').aggregate(total=models.Sum('valor'))['total'] or 0
        context['valor_pagar_pago'] = ContaPagar.objects.filter(status='PAGO').aggregate(total=models.Sum('valor'))['total'] or 0
        context['valor_receber_pendente'] = ContaReceber.objects.filter(status='PENDENTE').aggregate(total=models.Sum('valor'))['total'] or 0
        context['valor_receber_recebido'] = ContaReceber.objects.filter(status='RECEBIDO').aggregate(total=models.Sum('valor'))['total'] or 0
        
        from comercial.models import Venda
        
        context['vendas_finalizadas'] = Venda.objects.filter(status='FECHADA').count()
        context['valor_vendas_finalizadas'] = Venda.objects.filter(status='FECHADA').aggregate(total=models.Sum('valor_total'))['total'] or 0
        
        total_entradas = (context['valor_receber_recebido'] or 0) + (context['valor_vendas_finalizadas'] or 0)
        total_saidas = (context['valor_pagar_pago'] or 0)
        context['saldo'] = total_entradas - total_saidas
        
        # Cálculo do saldo previsto: saldo atual + contas a receber pendentes - contas a pagar pendentes
        context['saldo_previsto'] = context['saldo'] + context['valor_receber_pendente'] - context['valor_pagar_pendente']
        
        context['vendas_finalizadas_mes'] = Venda.objects.filter(
            status='FECHADA',
            data_venda__month=mes_atual,
            data_venda__year=ano_atual
        ).count()
        
        context['valor_vendas_finalizadas_mes'] = Venda.objects.filter(
            status='FECHADA',
            data_venda__month=mes_atual,
            data_venda__year=ano_atual
        ).aggregate(total=models.Sum('valor_total'))['total'] or 0
        
        context['grafico_pagar'] = {
            'labels': ['Pendente', 'Pago', 'Cancelado'],
            'data': [
                ContaPagar.objects.filter(status='PENDENTE').count(),
                ContaPagar.objects.filter(status='PAGO').count(),
                ContaPagar.objects.filter(status='CANCELADO').count(),
            ]
        }
        context['grafico_receber'] = {
            'labels': ['Pendente', 'Recebido', 'Cancelado'],
            'data': [
                ContaReceber.objects.filter(status='PENDENTE').count(),
                ContaReceber.objects.filter(status='RECEBIDO').count(),
                ContaReceber.objects.filter(status='CANCELADO').count(),
            ]
        }
        
        meses = []
        dados_vendas = []
        
        for i in range(5, -1, -1):
            mes = mes_atual - i
            ano = ano_atual
            
            while mes <= 0:
                mes += 12
                ano -= 1
            
            nome_mes = datetime.date(ano, mes, 1).strftime('%b')
            meses.append(f'{nome_mes}/{str(ano)[2:]}')
            
            valor_vendas = Venda.objects.filter(
                status='FECHADA',
                data_venda__month=mes,
                data_venda__year=ano
            ).aggregate(total=models.Sum('valor_total'))['total'] or 0
            
            dados_vendas.append(float(valor_vendas))
        
        context['grafico_vendas_mensal'] = {
            'labels': meses,
            'data': dados_vendas
        }
        return context