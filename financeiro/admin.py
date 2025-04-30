from django.contrib import admin
from .models import ContaPagar, ContaReceber, Transacao

@admin.register(ContaPagar)
class ContaPagarAdmin(admin.ModelAdmin):
    list_display = ['fornecedor', 'valor', 'data_vencimento', 'status', 'data_pagamento']
    list_filter = ['status', 'data_vencimento', 'data_pagamento']
    search_fields = ['fornecedor__nome', 'observacoes']
    date_hierarchy = 'data_vencimento'
    readonly_fields = []

@admin.register(ContaReceber)
class ContaReceberAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'valor', 'data_vencimento', 'status', 'data_recebimento']
    list_filter = ['status', 'data_vencimento', 'data_recebimento']
    search_fields = ['cliente__nome', 'observacoes']
    date_hierarchy = 'data_vencimento'
    readonly_fields = []

@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = ['descricao', 'valor', 'tipo', 'data', 'categoria', 'responsavel']
    list_filter = ['tipo', 'categoria', 'data', 'responsavel']
    search_fields = ['descricao', 'categoria']
    date_hierarchy = 'data'
    readonly_fields = []
