from django.contrib import admin
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from .models import Produto, MateriaPrima, OrdemProducao, ProdutoMateriaPrima

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
