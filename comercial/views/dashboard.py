"""
Views para o dashboard do módulo comercial.
"""
from django.views.generic import TemplateView
from django.db import models
from comercial.models import Venda, Cliente, Fornecedor
from django.utils import timezone
import json
from datetime import timedelta
from django.core.serializers.json import DjangoJSONEncoder

class DashboardView(TemplateView):
    """
    View para exibição do dashboard comercial com indicadores e métricas avançadas.
    """
    template_name = 'comercial/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = timezone.now().date()
        
        try:
            # Estatísticas gerais de vendas
            todas_vendas = Venda.objects.all()
            context['vendas_count'] = todas_vendas.count()
            
            # Vendas recentes (limitado a 8)
            context['vendas_recentes'] = todas_vendas.order_by('-data_venda')[:8]
            
            # Financeiro: vendas finalizadas
            vendas_finalizadas = todas_vendas.filter(status='FECHADA')
            context['vendas_finalizadas_count'] = vendas_finalizadas.count()
            context['vendas_finalizadas_valor'] = vendas_finalizadas.aggregate(
                total=models.Sum('valor_total')
            )['total'] or 0
            
            # Estatísticas de clientes
            todos_clientes = Cliente.objects.all()
            context['clientes_count'] = todos_clientes.count()
            
            # Clientes fiéis (com mais de 3 compras)
            clientes_fieis = 0
            top_clientes = []
            
            for cliente in todos_clientes[:20]:  # Limitando para performance
                compras = Venda.objects.filter(cliente=cliente, status='FECHADA')
                compras_count = compras.count()
                
                if compras_count >= 3:
                    clientes_fieis += 1
                
                if compras_count > 0:
                    compras_valor = compras.aggregate(total=models.Sum('valor_total'))['total'] or 0
                    ultima_compra = compras.order_by('-data_venda').first()
                    
                    top_clientes.append({
                        'nome': cliente.nome,
                        'compras_count': compras_count,
                        'compras_valor': compras_valor,
                        'ultima_compra': ultima_compra.data_venda if ultima_compra else None
                    })
            
            # Ordenar clientes pelo valor total de compras
            top_clientes.sort(key=lambda x: x['compras_valor'], reverse=True)
            context['clientes_fieis'] = clientes_fieis
            context['top_clientes'] = top_clientes[:5]  # Top 5 clientes
            
            # Fornecedores
            fornecedores = Fornecedor.objects.all()[:5]
            context['fornecedores'] = [
                {
                    'nome': f.nome, 
                    'categoria': f.categoria if hasattr(f, 'categoria') else 'Geral',
                    'produtos_count': 0,  # Em um sistema real, seria o count de produtos relacionados
                    'ultimo_pedido': None  # Em um sistema real, seria a data do último pedido
                } for f in fornecedores
            ]
            
            # Calculando ticket médio
            if vendas_finalizadas.count() > 0:
                context['ticket_medio'] = round(context['vendas_finalizadas_valor'] / vendas_finalizadas.count(), 2)
            else:
                context['ticket_medio'] = 0
                
            # Comparação entre meses para gráfico
            # Gerando dados dos últimos 6 meses para o gráfico
            meses = []
            valores_vendas = []
            qtds_vendas = []
            
            for i in range(5, -1, -1):
                # Calculando o mês
                mes_atual = hoje.replace(day=1) - timedelta(days=i*30)
                ultimo_dia = (mes_atual.replace(month=mes_atual.month % 12 + 1, day=1) if mes_atual.month < 12 
                              else mes_atual.replace(year=mes_atual.year + 1, month=1, day=1)) - timedelta(days=1)
                
                # Formatando o nome do mês
                nome_mes = mes_atual.strftime('%b/%y')
                meses.append(nome_mes)
                
                # Buscando vendas do período
                vendas_periodo = todas_vendas.filter(
                    data_venda__gte=mes_atual,
                    data_venda__lte=ultimo_dia,
                    status='FECHADA'
                )
                
                # Valor total vendido no período
                valor_total = vendas_periodo.aggregate(total=models.Sum('valor_total'))['total'] or 0
                valores_vendas.append(float(valor_total))
                
                # Quantidade de vendas no período
                qtd_vendas = vendas_periodo.count()
                qtds_vendas.append(qtd_vendas)
            
            # Preparando os dados para o gráfico em JSON de forma mais segura
            context['meses'] = json.dumps(meses, cls=DjangoJSONEncoder)
            context['valores_vendas'] = json.dumps(valores_vendas, cls=DjangoJSONEncoder)
            context['qtds_vendas'] = json.dumps(qtds_vendas, cls=DjangoJSONEncoder)
            
            # Calculando percentual de mudança nas vendas
            mes_atual = hoje.month
            ano_atual = hoje.year
            
            # Vendas do mês atual
            vendas_mes_atual = todas_vendas.filter(
                data_venda__month=mes_atual,
                data_venda__year=ano_atual
            ).count()
            
            # Vendas do mês anterior
            mes_anterior = mes_atual - 1 if mes_atual > 1 else 12
            ano_anterior = ano_atual if mes_atual > 1 else ano_atual - 1
            
            vendas_mes_anterior = todas_vendas.filter(
                data_venda__month=mes_anterior,
                data_venda__year=ano_anterior
            ).count()
            
            context['vendas_mes_atual'] = vendas_mes_atual
            context['vendas_mes_anterior'] = vendas_mes_anterior
            
            # Calculando o percentual de mudança
            if vendas_mes_anterior > 0:
                percent_change = ((vendas_mes_atual - vendas_mes_anterior) / vendas_mes_anterior) * 100
                context['vendas_percent_change'] = round(percent_change, 1)
            else:
                context['vendas_percent_change'] = 100
            
        except Exception as e:
            # Em caso de erro, inicializar com valores vazios
            context['vendas_count'] = 0
            context['vendas_recentes'] = []
            context['clientes_count'] = 0
            context['vendas_finalizadas_count'] = 0
            context['vendas_finalizadas_valor'] = 0
            context['clientes_fieis'] = 0
            context['top_clientes'] = []
            context['fornecedores'] = []
            context['ticket_medio'] = 0
            context['meses'] = json.dumps(['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'], cls=DjangoJSONEncoder)
            context['valores_vendas'] = json.dumps([0, 0, 0, 0, 0, 0], cls=DjangoJSONEncoder)
            context['qtds_vendas'] = json.dumps([0, 0, 0, 0, 0, 0], cls=DjangoJSONEncoder)
            context['vendas_mes_atual'] = 0
            context['vendas_mes_anterior'] = 0
            context['vendas_percent_change'] = 0
            
        return context