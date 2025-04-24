from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ContaPagar(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('PAGO', 'Pago'),
        ('CANCELADO', 'Cancelado')
    ]
    
    fornecedor = models.ForeignKey('comercial.Fornecedor', on_delete=models.PROTECT)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_vencimento = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDENTE')
    data_pagamento = models.DateField(null=True, blank=True)
    observacoes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Conta a Pagar'
        verbose_name_plural = 'Contas a Pagar'
        ordering = ['data_vencimento']

    def __str__(self):
        return f"{self.fornecedor} - R${self.valor}"

class ContaReceber(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('RECEBIDO', 'Recebido'),
        ('CANCELADO', 'Cancelado')
    ]
    
    cliente = models.ForeignKey('comercial.Cliente', on_delete=models.PROTECT)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_vencimento = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDENTE')
    data_recebimento = models.DateField(null=True, blank=True)
    observacoes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Conta a Receber'
        verbose_name_plural = 'Contas a Receber'
        ordering = ['data_vencimento']

    def __str__(self):
        return f"{self.cliente} - R${self.valor}"

class Transacao(models.Model):
    TIPO_CHOICES = [
        ('RECEITA', 'Receita'),
        ('DESPESA', 'Despesa')
    ]

    descricao = models.CharField(max_length=100)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=7, choices=TIPO_CHOICES)
    data = models.DateField()
    categoria = models.CharField(max_length=50)
    responsavel = models.ForeignKey(User, on_delete=models.PROTECT)
    observacoes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Transação'
        verbose_name_plural = 'Transações'
        ordering = ['-data']

    def __str__(self):
        return f"{self.descricao} - R${self.valor}"

    @classmethod
    def get_saldo(cls):
        receitas = cls.objects.filter(tipo='RECEITA').aggregate(models.Sum('valor'))['valor__sum'] or 0
        despesas = cls.objects.filter(tipo='DESPESA').aggregate(models.Sum('valor'))['valor__sum'] or 0
        return receitas - despesas
