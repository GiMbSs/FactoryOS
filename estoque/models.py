from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class MovimentacaoEstoque(models.Model):
    TIPO_MOVIMENTO = [
        ('ENTRADA', 'Entrada'),
        ('SAIDA', 'Saída')
    ]
    
    ORIGEM_DESTINO = [
        ('FORNECEDOR', 'Fornecedor'),
        ('PRODUCAO', 'Produção'), 
        ('CLIENTE', 'Cliente')
    ]

    materia_prima = models.ForeignKey('producao.MateriaPrima', on_delete=models.PROTECT)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_movimento = models.CharField(max_length=7, choices=TIPO_MOVIMENTO)
    origem_destino = models.CharField(max_length=10, choices=ORIGEM_DESTINO)
    lote = models.CharField(max_length=20)
    data = models.DateTimeField(default=timezone.now)
    observacao = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Movimentação de Estoque'
        verbose_name_plural = 'Movimentações de Estoque'
        indexes = [
            models.Index(fields=['materia_prima']),
            models.Index(fields=['tipo_movimento']),
            models.Index(fields=['data']),
        ]

    def __str__(self):
        return f"{self.tipo_movimento} - {self.materia_prima} ({self.quantidade})"

    def clean(self):
        if self.quantidade <= 0:
            raise ValidationError("A quantidade deve ser maior que zero")
        
        if self.tipo_movimento == 'SAIDA':
            from .models import SaldoEstoque
            produto = Produto.objects.get(materia_prima=self.materia_prima)
            saldo = SaldoEstoque.objects.get(materia_prima=self.materia_prima)
            if self.quantidade > saldo.quantidade_atual:
                raise ValidationError("Quantidade em estoque insuficiente")

class SaldoEstoque(models.Model):
    materia_prima = models.OneToOneField(
        'producao.MateriaPrima', 
        on_delete=models.CASCADE,
        primary_key=True
    )
    quantidade_atual = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ultima_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Saldo de Estoque'
        verbose_name_plural = 'Saldos de Estoque'

    def __str__(self):
        return f"{self.materia_prima} - {self.quantidade_atual}"

    def verificar_disponibilidade(self, quantidade):
        return self.quantidade_atual >= quantidade

    def calcular_estoque_minimo(self):
        """Calcula estoque mínimo baseado em média de consumo dos últimos 30 dias"""
        from django.db.models import Avg
        from datetime import timedelta
        
        movimentacoes = MovimentacaoEstoque.objects.filter(
            materia_prima=self.materia_prima,
            data__gte=timezone.now() - timedelta(days=30),
            tipo_movimento='SAIDA'
        ).aggregate(avg=Avg('quantidade'))
        
        avg_saidas = movimentacoes['avg'] or 0
        return avg_saidas * 7  # Estoque para 7 dias de consumo

from producao.models import Produto

class ProdutoEstoque(models.Model):
    produto = models.OneToOneField(Produto, on_delete=models.CASCADE, primary_key=True)
    quantidade_atual = models.PositiveIntegerField(default=0)
    ultima_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Saldo de Produto Acabado'
        verbose_name_plural = 'Saldos de Produtos Acabados'

    def __str__(self):
        return f"{self.produto} - {self.quantidade_atual}"

@receiver(post_save, sender=MovimentacaoEstoque)
def atualizar_saldo(sender, instance, created, **kwargs):
    if created:
        saldo, _ = SaldoEstoque.objects.get_or_create(
            materia_prima=instance.materia_prima
        )
        
        if instance.tipo_movimento == 'ENTRADA':
            saldo.quantidade_atual += instance.quantidade
        else:
            saldo.quantidade_atual -= instance.quantidade
            
        saldo.save()
