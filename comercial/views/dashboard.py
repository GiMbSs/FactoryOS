"""
Views para o dashboard do módulo comercial.
"""
from django.views.generic import TemplateView
from django.db import models
from comercial.models import Venda, Cliente


class DashboardView(TemplateView):
    """
    View para exibição do dashboard comercial com indicadores e métricas.
    """
    template_name = 'comercial/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            # Buscar as vendas mais recentes (limitado a 5)
            vendas = Venda.objects.all()[:5] if Venda.objects.exists() else []
            
            # Buscar os clientes mais recentes (limitado a 10)
            clientes = Cliente.objects.all()[:10] if Cliente.objects.exists() else []
            
            context['vendas'] = vendas
            context['clientes'] = clientes
            context['vendas_count'] = len(vendas)
            context['clientes_count'] = len(clientes)

            # Financeiro: vendas finalizadas
            vendas_finalizadas = Venda.objects.filter(status='FECHADA')
            context['vendas_finalizadas_count'] = vendas_finalizadas.count()
            context['vendas_finalizadas_valor'] = vendas_finalizadas.aggregate(
                total=models.Sum('valor_total')
            )['total'] or 0
            
        except Exception as e:
            # Em caso de erro, inicializar com valores vazios
            context['vendas'] = []
            context['clientes'] = []
            context['vendas_count'] = 0
            context['clientes_count'] = 0
            context['vendas_finalizadas_count'] = 0
            context['vendas_finalizadas_valor'] = 0
            
        return context