from rest_framework import serializers
from .models import MateriaPrima, Produto, OrdemProducao
from estoque.models import SaldoEstoque

class MateriaPrimaSerializer(serializers.ModelSerializer):
    saldo = serializers.SerializerMethodField()
    custo_total = serializers.SerializerMethodField()

    class Meta:
        model = MateriaPrima
        fields = ['id', 'nome', 'tipo', 'unidade_medida', 
                 'custo_unitario', 'saldo', 'custo_total']

    def get_saldo(self, obj):
        try:
            saldo = SaldoEstoque.objects.get(materia_prima=obj)
            return saldo.quantidade_atual
        except SaldoEstoque.DoesNotExist:
            return 0

    def get_custo_total(self, obj):
        try:
            saldo = SaldoEstoque.objects.get(materia_prima=obj)
            return saldo.quantidade_atual * obj.custo_unitario
        except SaldoEstoque.DoesNotExist:
            return 0

from .models import ProdutoMateriaPrima

class ProdutoMateriaPrimaSerializer(serializers.ModelSerializer):
    materia_prima = MateriaPrimaSerializer()
    class Meta:
        model = ProdutoMateriaPrima
        fields = ['materia_prima', 'quantidade_utilizada']

class ProdutoSerializer(serializers.ModelSerializer):
    custo_producao = serializers.SerializerMethodField()
    materias_primas = serializers.SerializerMethodField()
    tipo_produto_nome = serializers.CharField(source='tipo_produto.nome', read_only=True)

    class Meta:
        model = Produto
        fields = ['id', 'nome', 'descricao', 'tipo', 'tipo_produto', 'tipo_produto_nome', 'codigo_sku', 'custo_producao', 'materias_primas']

    def get_custo_producao(self, obj):
        return obj.calcular_custo()

    def get_materias_primas(self, obj):
        qs = obj.produtomateriaprima_set.select_related('materia_prima').all()
        return ProdutoMateriaPrimaSerializer(qs, many=True).data

class OrdemProducaoSerializer(serializers.ModelSerializer):
    produto_nome = serializers.CharField(source='produto.nome', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = OrdemProducao
        fields = ['id', 'produto', 'produto_nome', 'quantidade', 
                 'status', 'status_display', 'data_inicio', 'data_fim']
