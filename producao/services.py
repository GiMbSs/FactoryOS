from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.conf import settings

# Valores configuráveis que poderiam estar no settings.py
CUSTO_MAO_OBRA = getattr(settings, 'CUSTO_MAO_OBRA', {
    'PLASTICO': Decimal('2.50'),
    'MADEIRA': Decimal('4.00'),
    'TECIDO': Decimal('3.50'),
    'MISTO': Decimal('3.75'),
})
PERCENTUAL_CUSTO_INDIRETO = getattr(settings, 'PERCENTUAL_CUSTO_INDIRETO', Decimal('0.10'))

class ProdutoService:
    @staticmethod
    def calcular_custo(produto):
        """
        Calcula o custo total de um produto com base em suas matérias-primas,
        mão de obra e custos indiretos.
        
        Args:
            produto: Instância do modelo Produto
        
        Returns:
            Decimal: Custo total calculado do produto
        """
        custo_materias = sum(
            pm.quantidade_utilizada * pm.materia_prima.custo_unitario
            for pm in produto.produtomateriaprima_set.all()
        )
        
        if not isinstance(custo_materias, Decimal):
            custo_materias = Decimal(str(custo_materias))
            
        # Usa o mapeamento de custos de mão de obra ou um valor padrão
        mao_obra = CUSTO_MAO_OBRA.get(produto.tipo, Decimal('3.50'))
        
        custo_total = custo_materias + mao_obra
        custo_indireto = custo_total * PERCENTUAL_CUSTO_INDIRETO
        total = custo_total + custo_indireto
        
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calcular_custo_agregado(produtos):
        """
        Calcula o custo total para uma queryset de produtos sem loops Python.
        
        Args:
            produtos: Queryset de produtos
            
        Returns:
            Decimal: Soma dos custos de todos os produtos
        """
        # Implementação futura usando agregações do Django
        return sum(ProdutoService.calcular_custo(produto) for produto in produtos)

class EstatisticasService:
    @staticmethod
    def obter_estatisticas_produto():
        """
        Retorna estatísticas sobre produtos para dashboards e listagens
        """
        from .models import Produto
        
        resultado = {
            'total_produtos': Produto.objects.count(),
            'produtos_por_tipo': {
                'madeira': Produto.objects.filter(tipo='MADEIRA').count(),
                'plastico': Produto.objects.filter(tipo='PLASTICO').count(),
                'tecido': Produto.objects.filter(tipo='TECIDO').count(),
                'misto': Produto.objects.filter(tipo='MISTO').count(),
            }
        }
        
        # Cálculo do custo médio
        produtos = Produto.objects.all()
        if produtos.exists():
            custo_total = ProdutoService.calcular_custo_agregado(produtos)
            resultado['custo_medio'] = custo_total / produtos.count()
        else:
            resultado['custo_medio'] = Decimal('0')
            
        return resultado
        
class EstoqueService:
    @staticmethod
    def obter_alertas_estoque():
        """
        Retorna matérias-primas com estoque abaixo do mínimo
        """
        try:
            from estoque.models import SaldoEstoque
            from django.db.models import F
            
            return SaldoEstoque.objects.filter(
                quantidade_atual__lt=F('materia_prima__estoque_minimo'),
                materia_prima__estoque_minimo__gt=0
            ).select_related('materia_prima')
            
        except ImportError:
            return []