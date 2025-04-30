from django.contrib import admin
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from .models import (
    Produto, MateriaPrima, OrdemProducao, ProdutoMateriaPrima, 
    ConfiguracaoCustoMaoObra, Categoria, UnidadeMedida, 
    TipoMateriaPrima, TipoProduto
)

class ProdutoMateriaPrimaInline(admin.TabularInline):
    model = ProdutoMateriaPrima
    extra = 1
    fields = ['materia_prima', 'quantidade_utilizada', 'observacoes']
    autocomplete_fields = ['materia_prima']

@admin.register(Produto)
class ProdutoAdmin(ImportExportModelAdmin):
    list_display = ['nome', 'tipo', 'codigo_sku', 'custo_producao']
    list_filter = ['tipo']
    search_fields = ['nome', 'codigo_sku']
    inlines = [ProdutoMateriaPrimaInline]

    def custo_producao(self, obj):
        return f"R$ {obj.calcular_custo():.2f}"
    custo_producao.short_description = "Custo de Produção"

@admin.register(MateriaPrima)
class MateriaPrimaAdmin(ImportExportModelAdmin):
    list_display = ['nome', 'tipo', 'unidade_medida', 'custo_unitario', 'estoque_status']
    list_filter = ['tipo', 'unidade_medida']
    search_fields = ['nome']

    def estoque_status(self, obj):
        from estoque.models import SaldoEstoque
        try:
            saldo = SaldoEstoque.objects.get(materia_prima=obj)
            if saldo.quantidade_atual < obj.estoque_minimo:
                return format_html('<span style="color: red;">{} (baixo)</span>', saldo.quantidade_atual)
            return saldo.quantidade_atual
        except SaldoEstoque.DoesNotExist:
            return 0
    estoque_status.short_description = "Estoque Atual"

@admin.register(OrdemProducao)
class OrdemProducaoAdmin(admin.ModelAdmin):
    list_display = ['id', 'produto', 'quantidade', 'status', 'data_inicio', 'data_fim']
    list_filter = ['status', 'produto']
    search_fields = ['produto__nome']
    date_hierarchy = 'data_inicio'
    readonly_fields = ['custo_total']

    def custo_total(self, obj):
        return f"R$ {obj.produto.calcular_custo() * obj.quantidade:.2f}"
    custo_total.short_description = "Custo Total Estimado"

@admin.register(ConfiguracaoCustoMaoObra)
class ConfiguracaoCustoMaoObraAdmin(admin.ModelAdmin):
    list_display = ['tipo_produto', 'get_tipo_display', 'custo_mao_obra', 'ultima_atualizacao']
    list_filter = ['tipo_produto']
    search_fields = ['tipo_produto', 'descricao']
    readonly_fields = ['ultima_atualizacao']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('tipo_produto', 'custo_mao_obra')
        }),
        ('Informações Adicionais', {
            'fields': ('descricao', 'ultima_atualizacao'),
            'classes': ('collapse',)
        })
    )
    
    def get_tipo_display(self, obj):
        return obj.get_tipo_produto_display()
    get_tipo_display.short_description = 'Tipo de Produto'
    
    def save_model(self, request, obj, form, change):
        # Adiciona informações sobre quem fez a alteração
        if obj.descricao and not obj.descricao.endswith('.'):
            obj.descricao += '.'
        if change:  # Se estiver editando um registro existente
            obj.descricao += f' Atualizado por {request.user.username}.'
        else:  # Se estiver criando um novo registro
            obj.descricao += f' Criado por {request.user.username}.'
        super().save_model(request, obj, form, change)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug', 'segmento', 'ordem', 'ativo']
    list_filter = ['segmento', 'ativo']
    search_fields = ['nome', 'descricao']
    prepopulated_fields = {'slug': ('nome',)}

@admin.register(UnidadeMedida)
class UnidadeMedidaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'sigla']
    search_fields = ['nome', 'sigla']

@admin.register(TipoMateriaPrima)
class TipoMateriaPrimaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'icone', 'cor', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome', 'descricao']

@admin.register(TipoProduto)
class TipoProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'icone', 'cor', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome', 'descricao']
