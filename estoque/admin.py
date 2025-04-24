from django.contrib import admin
from .models import MovimentacaoEstoque, SaldoEstoque

@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = ('materia_prima', 'quantidade', 'tipo_movimento', 'origem_destino', 'data')
    list_filter = ('tipo_movimento', 'origem_destino', 'data')
    search_fields = ('materia_prima__nome', 'lote')
    date_hierarchy = 'data'
    ordering = ('-data',)
    fieldsets = (
        (None, {
            'fields': ('materia_prima', 'quantidade', 'tipo_movimento')
        }),
        ('Detalhes', {
            'fields': ('origem_destino', 'lote', 'observacao'),
            'classes': ('collapse',)
        }),
    )

@admin.register(SaldoEstoque)
class SaldoEstoqueAdmin(admin.ModelAdmin):
    list_display = ('materia_prima', 'quantidade_atual', 'ultima_atualizacao')
    search_fields = ('materia_prima__nome',)
    list_filter = ('ultima_atualizacao',)
    readonly_fields = ('ultima_atualizacao',)
    ordering = ('materia_prima',)
