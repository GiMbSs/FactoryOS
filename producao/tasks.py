from celery import shared_task
from django.utils import timezone
from .models import Produto
from estoque.models import SaldoEstoque
import logging

logger = logging.getLogger(__name__)

@shared_task
def recalcular_custos_produtos():
    """Task para recalcular custos de todos os produtos"""
    try:
        for produto in Produto.objects.all():
            custo = produto.calcular_custo()
            logger.info(f"Custo atualizado para {produto}: R${custo:.2f}")
        return "Custos recalculados com sucesso"
    except Exception as e:
        logger.error(f"Erro ao recalcular custos: {str(e)}")
        raise

@shared_task
def verificar_estoque_minimo():
    """Task para verificar e alertar estoques abaixo do mínimo"""
    try:
        alertas = []
        for saldo in SaldoEstoque.objects.all():
            estoque_minimo = saldo.calcular_estoque_minimo()
            if saldo.quantidade_atual < estoque_minimo:
                alertas.append({
                    'materia_prima': saldo.materia_prima.nome,
                    'quantidade_atual': saldo.quantidade_atual,
                    'estoque_minimo': estoque_minimo
                })
                logger.warning(
                    f"Estoque baixo: {saldo.materia_prima} - "
                    f"Atual: {saldo.quantidade_atual}, Mínimo: {estoque_minimo}"
                )
        
        return alertas or "Nenhum estoque abaixo do mínimo"
    except Exception as e:
        logger.error(f"Erro ao verificar estoques: {str(e)}")
        raise
