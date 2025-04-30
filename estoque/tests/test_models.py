from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from estoque.models import MovimentacaoEstoque, SaldoEstoque, ProdutoEstoque
from producao.models import MateriaPrima, TipoMateriaPrima, Produto, TipoProduto, UnidadeMedida
import decimal

class MovimentacaoEstoqueTest(TestCase):
    """Testes para o modelo MovimentacaoEstoque"""
    
    def setUp(self):
        # Criar objetos necessários
        self.tipo_materia = TipoMateriaPrima.objects.create(nome="Tecido Filtrante")
        self.unidade = UnidadeMedida.objects.create(nome="Metro", sigla="m")
        
        # Criar matéria prima para testes
        self.materia_prima = MateriaPrima.objects.create(
            nome="Tecido 100% Algodão",
            tipo="TECIDO_PANO_CRU",
            tipo_materia_prima=self.tipo_materia,
            unidade_medida="METRO",
            unidade=self.unidade,
            custo_unitario=12.50
        )
        
        # Inicializar o saldo para a matéria-prima
        self.saldo = SaldoEstoque.objects.create(
            materia_prima=self.materia_prima,
            quantidade_atual=100.0  # Começar com um saldo de 100 metros
        )
    
    def test_criar_entrada_estoque(self):
        """Testa a criação de uma entrada de estoque"""
        # Situação inicial
        saldo_atual = SaldoEstoque.objects.get(materia_prima=self.materia_prima).quantidade_atual
        
        # Criar entrada de estoque
        entrada = MovimentacaoEstoque.objects.create(
            materia_prima=self.materia_prima,
            quantidade=50,
            tipo_movimento='ENTRADA',
            origem_destino='FORNECEDOR',
            lote='LOTE-2025-001'
        )
        
        # Verificar se a entrada foi registrada
        self.assertEqual(entrada.tipo_movimento, 'ENTRADA')
        self.assertEqual(entrada.quantidade, 50)
        
        # Verificar se o saldo foi atualizado pelo signal
        saldo_atualizado = SaldoEstoque.objects.get(materia_prima=self.materia_prima)
        self.assertEqual(float(saldo_atualizado.quantidade_atual), float(saldo_atual) + 50)
    
    def test_criar_saida_estoque(self):
        """Testa a criação de uma saída de estoque"""
        # Situação inicial
        saldo_atual = SaldoEstoque.objects.get(materia_prima=self.materia_prima).quantidade_atual
        
        # Criar saída de estoque
        saida = MovimentacaoEstoque.objects.create(
            materia_prima=self.materia_prima,
            quantidade=30,
            tipo_movimento='SAIDA',
            origem_destino='PRODUCAO',
            lote='LOTE-2025-002'
        )
        
        # Verificar se a saída foi registrada
        self.assertEqual(saida.tipo_movimento, 'SAIDA')
        self.assertEqual(saida.quantidade, 30)
        
        # Verificar se o saldo foi atualizado pelo signal
        saldo_atualizado = SaldoEstoque.objects.get(materia_prima=self.materia_prima)
        self.assertEqual(float(saldo_atualizado.quantidade_atual), float(saldo_atual) - 30)
    
    def test_saida_maior_que_saldo(self):
        """Testa a validação de saída maior que o saldo disponível"""
        # Tentar criar uma saída maior que o saldo
        with self.assertRaises(ValidationError):
            saida = MovimentacaoEstoque(
                materia_prima=self.materia_prima,
                quantidade=200,  # Saldo é de 100, tentando sacar 200
                tipo_movimento='SAIDA',
                origem_destino='PRODUCAO',
                lote='LOTE-2025-003'
            )
            saida.full_clean()  # Isso deve lançar uma ValidationError
    
    def test_quantidade_negativa(self):
        """Testa a validação de quantidade negativa"""
        # Tentar criar uma movimentação com quantidade negativa
        with self.assertRaises(ValidationError):
            movimentacao = MovimentacaoEstoque(
                materia_prima=self.materia_prima,
                quantidade=-10,  # Quantidade negativa não é permitida
                tipo_movimento='ENTRADA',
                origem_destino='FORNECEDOR',
                lote='LOTE-2025-004'
            )
            movimentacao.full_clean()  # Isso deve lançar uma ValidationError


class SaldoEstoqueTest(TestCase):
    """Testes para o modelo SaldoEstoque"""
    
    def setUp(self):
        # Criar objetos necessários
        self.tipo_materia = TipoMateriaPrima.objects.create(nome="Tecido Filtrante")
        self.unidade = UnidadeMedida.objects.create(nome="Metro", sigla="m")
        
        # Criar matéria prima para testes
        self.materia_prima = MateriaPrima.objects.create(
            nome="Tecido 100% Algodão",
            tipo="TECIDO_PANO_CRU",
            tipo_materia_prima=self.tipo_materia,
            unidade_medida="METRO",
            unidade=self.unidade,
            custo_unitario=12.50,
            estoque_minimo=20.0
        )
        
        # Criar um saldo de estoque
        self.saldo = SaldoEstoque.objects.create(
            materia_prima=self.materia_prima,
            quantidade_atual=50.0
        )
    
    def test_verificar_disponibilidade(self):
        """Testa o método de verificação de disponibilidade"""
        # Verificar quantidade disponível
        self.assertTrue(self.saldo.verificar_disponibilidade(30.0))  # Temos 50, queremos 30
        self.assertTrue(self.saldo.verificar_disponibilidade(50.0))  # Temos 50, queremos 50
        self.assertFalse(self.saldo.verificar_disponibilidade(60.0))  # Temos 50, queremos 60
    
    def test_calcular_estoque_minimo(self):
        """Testa o cálculo de estoque mínimo baseado no consumo médio"""
        # Criar algumas movimentações para o cálculo do estoque mínimo
        # Simula o consumo dos últimos 30 dias
        for i in range(5):  # Criar 5 saídas
            MovimentacaoEstoque.objects.create(
                materia_prima=self.materia_prima,
                quantidade=10.0,  # 10 unidades por saída
                tipo_movimento='SAIDA',
                origem_destino='PRODUCAO',
                lote=f'LOTE-TESTE-{i}',
                # Simular datas dentro dos últimos 30 dias
                data=timezone.now() - timezone.timedelta(days=i*3)
            )
        
        # O consumo médio é 10 unidades, o estoque mínimo deve ser 70 (7 dias * 10)
        estoque_minimo = self.saldo.calcular_estoque_minimo()
        self.assertEqual(estoque_minimo, 70.0)


class ProdutoEstoqueTest(TestCase):
    """Testes para o modelo ProdutoEstoque"""
    
    def setUp(self):
        # Criar tipo de produto
        self.tipo_produto = TipoProduto.objects.create(nome="Filtro de Café")
        
        # Criar o produto
        self.produto = Produto.objects.create(
            nome="Filtro de Café Premium",
            descricao="Filtro de alta qualidade",
            codigo_sku="FC-PREMIUM-01",
            tipo_produto=self.tipo_produto,
            tipo="MISTO"
        )
        
        # Criar um saldo de produto
        self.produto_estoque = ProdutoEstoque.objects.create(
            produto=self.produto,
            quantidade_atual=100
        )
    
    def test_produto_estoque_str(self):
        """Testa a representação em string do saldo de produto"""
        self.assertEqual(str(self.produto_estoque), f"{self.produto} - 100")
    
    def test_atualizar_quantidade_produto(self):
        """Testa a atualização da quantidade de produto em estoque"""
        # Atualizar a quantidade
        self.produto_estoque.quantidade_atual += 50
        self.produto_estoque.save()
        
        # Verificar se a quantidade foi atualizada corretamente
        produto_atualizado = ProdutoEstoque.objects.get(produto=self.produto)
        self.assertEqual(produto_atualizado.quantidade_atual, 150)