from django.contrib import admin
from .models import Fornecedor, Cliente, Venda, ItemVenda

class ItemVendaInline(admin.TabularInline):
    model = ItemVenda
    extra = 1
    fields = ['produto', 'quantidade', 'preco_unitario']
    readonly_fields = ['preco_unitario']

@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cnpj', 'email', 'telefone', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome', 'cnpj', 'email']

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'cnpj_cpf', 'email', 'telefone', 'ativo']
    list_filter = ['tipo', 'ativo']
    search_fields = ['nome', 'cnpj_cpf', 'email']

@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'vendedor', 'data_venda', 'valor_total', 'status']
    list_filter = ['status', 'data_venda']
    search_fields = ['cliente__nome', 'vendedor__username']
    date_hierarchy = 'data_venda'
    inlines = [ItemVendaInline]
    readonly_fields = ['data_venda']
