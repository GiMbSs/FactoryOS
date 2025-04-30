"""
Views para o dashboard do módulo de estoque.
"""
from django.views.generic import TemplateView
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.utils import timezone
from datetime import timedelta

from core.views import registrar_log
from producao.models import MateriaPrima
from estoque.models import SaldoEstoque, MovimentacaoEstoque


class DashboardView(TemplateView):
    """
    View para exibição do dashboard de estoque com indicadores e métricas.
    """
    template_name = 'estoque/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Todas as matérias-primas
        materias_primas = MateriaPrima.objects.all()
        context['materias_primas'] = materias_primas
        
        # Calcular valor total em estoque
        valor_total = SaldoEstoque.objects.annotate(
            valor_item=ExpressionWrapper(
                F('quantidade_atual') * F('materia_prima__custo_unitario'),
                output_field=DecimalField()
            )
        ).aggregate(total=Sum('valor_item'))['total'] or 0
        context['valor_total_estoque'] = valor_total
        
        # Itens abaixo do estoque mínimo
        itens_criticos = []
        itens_abaixo_minimo = 0
        itens_sem_estoque = 0
        
        for materia in materias_primas:
            try:
                saldo = SaldoEstoque.objects.get(materia_prima=materia)
                quantidade_atual = saldo.quantidade_atual
            except SaldoEstoque.DoesNotExist:
                quantidade_atual = 0
                
            if quantidade_atual <= 0:
                itens_sem_estoque += 1
                itens_criticos.append(materia)
            elif quantidade_atual <= materia.estoque_minimo:
                itens_abaixo_minimo += 1
                itens_criticos.append(materia)
        
        context['itens_abaixo_minimo'] = itens_abaixo_minimo
        context['itens_sem_estoque'] = itens_sem_estoque
        context['materias_criticas'] = itens_criticos
        
        # Dados para gráficos (movimentações recentes - 6 meses)
        meses = []
        entradas = []
        saidas = []
        
        for i in range(5, -1, -1):
            data_inicio = timezone.now() - timedelta(days=30 * i + 30)
            data_fim = timezone.now() - timedelta(days=30 * i)
            mes = data_fim.strftime('%b')
            meses.append(mes)
            
            entrada = MovimentacaoEstoque.objects.filter(
                data__gte=data_inicio,
                data__lt=data_fim,
                tipo_movimento='ENTRADA'
            ).count()
            
            saida = MovimentacaoEstoque.objects.filter(
                data__gte=data_inicio,
                data__lt=data_fim,
                tipo_movimento='SAIDA'
            ).count()
            
            entradas.append(entrada)
            saidas.append(saida)
        
        context['dados_movimentacoes'] = {
            'meses': meses,
            'entradas': entradas,
            'saidas': saidas
        }
        
        # Registrar acesso ao dashboard no log
        registrar_log(self.request, 'Estoque', 'Acessou o dashboard de estoque')
        
        return context