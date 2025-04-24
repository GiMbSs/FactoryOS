from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Fornecedor(models.Model):
    nome = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=18, unique=True)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Fornecedor'
        verbose_name_plural = 'Fornecedores'
        ordering = ['nome']

    def __str__(self):
        return self.nome

class Cliente(models.Model):
    TIPO_CHOICES = [
        ('PF', 'Pessoa Física'),
        ('PJ', 'Pessoa Jurídica')
    ]
    
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=2, choices=TIPO_CHOICES, default='PJ')
    cnpj_cpf = models.CharField(max_length=18, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)
    endereco = models.TextField(blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nome']

    def __str__(self):
        return self.nome

from estoque.models import ProdutoEstoque
from producao.models import Produto

class ItemVenda(models.Model):
    venda = models.ForeignKey('Venda', related_name='itens', on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Item de Venda'
        verbose_name_plural = 'Itens de Venda'

    def __str__(self):
        return f"{self.produto} x {self.quantidade}"

class Venda(models.Model):
    STATUS_CHOICES = [
        ('ABERTA', 'Aberta'),
        ('FECHADA', 'Fechada'),
        ('CANCELADA', 'Cancelada')
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    vendedor = models.ForeignKey(User, on_delete=models.PROTECT)
    data_venda = models.DateTimeField(auto_now_add=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ABERTA')
    observacoes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Venda'
        verbose_name_plural = 'Vendas'
        ordering = ['-data_venda']

    def __str__(self):
        return f"Venda #{self.id} - {self.cliente.nome}"

    def save(self, *args, **kwargs):
        status_anterior = None
        if self.pk:
            status_anterior = Venda.objects.get(pk=self.pk).status
        super().save(*args, **kwargs)
        # Lançar saída do estoque de produtos acabados ao fechar venda
        if self.status == 'FECHADA' and status_anterior != 'FECHADA':
            # Suporte para múltiplos itens por venda
            for item in self.itens.all():
                saldo, _ = ProdutoEstoque.objects.get_or_create(produto=item.produto)
                saldo.quantidade_atual = max(0, saldo.quantidade_atual - item.quantidade)
                saldo.save()
        # Se reabrir/cancelar venda, opcionalmente pode-se devolver ao estoque
