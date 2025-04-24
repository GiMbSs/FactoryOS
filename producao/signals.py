from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
import logging
from .models import OrdemProducao, ProdutoMateriaPrima
from estoque.models import MovimentacaoEstoque, SaldoEstoque, ProdutoEstoque

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=OrdemProducao)
def salvar_status_anterior(sender, instance, **kwargs):
    if instance.pk:
        try:
            original = OrdemProducao.objects.get(pk=instance.pk)
            instance._status_anterior = original.status
            
        except OrdemProducao.DoesNotExist:
            instance._status_anterior = None
            
    else:
        instance._status_anterior = None
        

@receiver(pre_save, sender=OrdemProducao)
def validar_estoque_antes_producao(sender, instance, **kwargs):
    if instance.status == 'EM_PRODUCAO' and instance.pk:
        original = OrdemProducao.objects.get(pk=instance.pk)
        if original.status != 'EM_PRODUCAO':
            # Verificar estoque para cada matéria-prima
            for pm in ProdutoMateriaPrima.objects.filter(produto=instance.produto):
                saldo = SaldoEstoque.objects.get(materia_prima=pm.materia_prima)
                if not saldo.verificar_disponibilidade(pm.quantidade_utilizada * instance.quantidade):
                    raise ValidationError(
                        f"Estoque insuficiente de {pm.materia_prima} "
                        f"(necessário: {pm.quantidade_utilizada * instance.quantidade}, "
                        f"disponível: {saldo.quantidade_atual})"
                    )

@receiver(post_save, sender=OrdemProducao)
def atualizar_estoque_apos_producao(sender, instance, created, **kwargs):
    
    # Detectar mudança de status
    try:
        # Buscar ordem anterior para saber o status antes da alteração
        original = None
        status_anterior = getattr(instance, '_status_anterior', None)
        
        # LOG ESPECIAL PARA DEPURAÇÃO DE DEDUÇÃO DE MATÉRIA-PRIMA
        if (
            (created and instance.status in ['EM_PRODUCAO', 'FINALIZADA']) or
            (not created and status_anterior != 'EM_PRODUCAO' and instance.status == 'EM_PRODUCAO')
        ):
            for pm in ProdutoMateriaPrima.objects.filter(produto=instance.produto):
                quantidade_deduzir = pm.quantidade_utilizada * instance.quantidade
                ja_deduzido = MovimentacaoEstoque.objects.filter(
                    materia_prima=pm.materia_prima,
                    lote=f"OP-{instance.id}",
                    tipo_movimento='SAIDA',
                    origem_destino='PRODUCAO'
                ).exists()
                if not ja_deduzido:
                    MovimentacaoEstoque.objects.create(
                        materia_prima=pm.materia_prima,
                        quantidade=quantidade_deduzir,
                        tipo_movimento='SAIDA',
                        origem_destino='PRODUCAO',
                        lote=f"OP-{instance.id}",
                        observacao=f"Ordem de produção #{instance.id} (lançada)"
                    )
                else:
                    pass
        # Devolver estoque ao cancelar
        if original and original.status == 'EM_PRODUCAO' and instance.status == 'CANCELADA':
            for pm in ProdutoMateriaPrima.objects.filter(produto=instance.produto):
                MovimentacaoEstoque.objects.create(
                    materia_prima=pm.materia_prima,
                    quantidade=pm.quantidade_utilizada * instance.quantidade,
                    tipo_movimento='ENTRADA',
                    origem_destino='PRODUCAO',
                    lote=f"OP-{instance.id}",
                    observacao=f"Ordem de produção #{instance.id} (cancelada, devolução)"
                )
            logger.info(f"Estoque devolvido para Ordem de Produção #{instance.id} (CANCELADA)")
        # Corrigir dedução de matéria-prima ao criar ordem já como FINALIZADA
        if (created and instance.status == 'FINALIZADA') or (original and original.status != 'FINALIZADA' and instance.status == 'FINALIZADA'):
            # Checar se já houve saída para evitar duplicidade
            for pm in ProdutoMateriaPrima.objects.filter(produto=instance.produto):
                ja_deduzido = MovimentacaoEstoque.objects.filter(
                    materia_prima=pm.materia_prima,
                    lote=f"OP-{instance.id}",
                    tipo_movimento='SAIDA',
                    origem_destino='PRODUCAO'
                ).exists()
                if not ja_deduzido:
                    MovimentacaoEstoque.objects.create(
                        materia_prima=pm.materia_prima,
                        quantidade=pm.quantidade_utilizada * instance.quantidade,
                        tipo_movimento='SAIDA',
                        origem_destino='PRODUCAO',
                        lote=f"OP-{instance.id}",
                        observacao=f"Ordem de produção #{instance.id} (finalizada)"
                    )
        # Adicionar produto acabado ao estoque sempre que finalizar
        if (created and instance.status == 'FINALIZADA') or (status_anterior != 'FINALIZADA' and instance.status == 'FINALIZADA'):
            
            produto = instance.produto
            quantidade = instance.quantidade
            saldo_produto, criado = ProdutoEstoque.objects.get_or_create(produto=produto)
            quantidade_antes = saldo_produto.quantidade_atual
            
            saldo_produto.quantidade_atual = (saldo_produto.quantidade_atual or 0) + quantidade
            saldo_produto.save()
            
            logger.info(f"Produto acabado lançado em estoque para Ordem de Produção #{instance.id} (FINALIZADA). Produto: {produto} | Antes: {quantidade_antes} | Adicionado: {quantidade} | Depois: {saldo_produto.quantidade_atual}")
    except Exception as e:
        
        logger.error(f"Erro ao atualizar estoque: {str(e)}")
        raise
