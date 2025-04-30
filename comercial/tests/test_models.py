from django.test import TestCase
from django.core.exceptions import ValidationError
from comercial.models import Cliente, Fornecedor, Venda, ItemVenda
from django.contrib.auth import get_user_model
from producao.models import Produto, TipoProduto

User = get_user_model()

class ClienteModelTest(TestCase):
    """Testes para o modelo Cliente"""
    
    def setUp(self):
        # Configuração inicial executada antes de cada teste
        self.cliente_pf = Cliente.objects.create(
            nome="João Silva",
            tipo="PF",
            cnpj_cpf="123.456.789-00",
            email="joao@example.com",
            telefone="(11) 98765-4321",
            endereco="Rua das Flores, 123",
            ativo=True
        )
        
        self.cliente_pj = Cliente.objects.create(
            nome="Empresa ABC Ltda",
            tipo="PJ",
            cnpj_cpf="12.345.678/0001-90",
            email="contato@abc.com",
            telefone="(11) 3333-4444",
            endereco="Av Paulista, 1000",
            ativo=True
        )

    def test_cliente_criacao(self):
        """Testa se os clientes foram criados corretamente"""
        self.assertEqual(Cliente.objects.count(), 2)
        
    def test_cliente_str(self):
        """Testa a representação em string do cliente"""
        self.assertEqual(str(self.cliente_pf), "João Silva")
        self.assertEqual(str(self.cliente_pj), "Empresa ABC Ltda")

    def test_cliente_ordering(self):
        """Testa se a ordenação de clientes está por nome"""
        clientes = list(Cliente.objects.all())
        self.assertEqual(clientes[0].nome, "Empresa ABC Ltda")  # Ordenado por nome
        self.assertEqual(clientes[1].nome, "João Silva")

    def test_cliente_tipo_opcoes(self):
        """Testa se os tipos de cliente são válidos"""
        self.assertIn(self.cliente_pf.tipo, [choice[0] for choice in Cliente.TIPO_CHOICES])
        self.assertIn(self.cliente_pj.tipo, [choice[0] for choice in Cliente.TIPO_CHOICES])

    def test_cliente_desativar(self):
        """Testa a desativação de um cliente"""
        self.cliente_pf.ativo = False
        self.cliente_pf.save()
        cliente_atualizado = Cliente.objects.get(id=self.cliente_pf.id)
        self.assertFalse(cliente_atualizado.ativo)


class FornecedorModelTest(TestCase):
    """Testes para o modelo Fornecedor"""
    
    def setUp(self):
        # Configuração inicial executada antes de cada teste
        self.fornecedor = Fornecedor.objects.create(
            nome="Fornecedor XYZ",
            cnpj="12.345.678/0001-90",
            email="contato@xyz.com",
            telefone="(11) 5555-6666",
            ativo=True
        )

    def test_fornecedor_criacao(self):
        """Testa se o fornecedor foi criado corretamente"""
        self.assertEqual(Fornecedor.objects.count(), 1)
        
    def test_fornecedor_str(self):
        """Testa a representação em string do fornecedor"""
        self.assertEqual(str(self.fornecedor), "Fornecedor XYZ")

    def test_fornecedor_desativar(self):
        """Testa a desativação de um fornecedor"""
        self.fornecedor.ativo = False
        self.fornecedor.save()
        fornecedor_atualizado = Fornecedor.objects.get(id=self.fornecedor.id)
        self.assertFalse(fornecedor_atualizado.ativo)

    def test_fornecedor_campos_obrigatorios(self):
        """Testa se os campos obrigatórios são validados"""
        # Criando um fornecedor sem nome deve falhar
        fornecedor_invalido = Fornecedor(
            cnpj="98.765.432/0001-10",
            email="teste@teste.com",
            telefone="(11) 1111-2222"
        )
        with self.assertRaises(ValidationError):
            fornecedor_invalido.full_clean()  # Valida o modelo


class VendaItemVendaModelTest(TestCase):
    """Testes para os modelos Venda e ItemVenda"""
    
    def setUp(self):
        # Criar usuário
        self.user = User.objects.create_user(username='testuser', password='password')
        
        # Criar cliente
        self.cliente = Cliente.objects.create(
            nome="Cliente Teste",
            email="cliente@teste.com",
            telefone="(11) 9876-5432"
        )
        
        # Criar tipo de produto
        self.tipo_produto = TipoProduto.objects.create(nome="Filtro")
        
        # Criar produto - removendo o preco_venda que não existe mais no modelo
        self.produto = Produto.objects.create(
            nome="Filtro de Café Premium",
            descricao="Filtro de alta qualidade",
            codigo_sku="FC-PREMIUM-01",
            tipo_produto=self.tipo_produto,
            tipo="MISTO"
        )
        
        # Criar venda
        self.venda = Venda.objects.create(
            cliente=self.cliente,
            vendedor=self.user,
            valor_total=105.00,
            status='ABERTA',
            observacoes="Venda para teste"
        )
        
        # Criar item de venda
        self.item_venda = ItemVenda.objects.create(
            venda=self.venda,
            produto=self.produto,
            quantidade=10,
            preco_unitario=10.50
        )

    def test_venda_criacao(self):
        """Testa se a venda foi criada corretamente"""
        self.assertEqual(Venda.objects.count(), 1)
        
    def test_venda_str(self):
        """Testa a representação em string da venda"""
        self.assertEqual(str(self.venda), f"Venda #{self.venda.id} - Cliente Teste")
        
    def test_item_venda_str(self):
        """Testa a representação em string do item de venda"""
        self.assertEqual(str(self.item_venda), "Filtro de Café Premium x 10")
        
    def test_venda_status_choices(self):
        """Testa se os status da venda são válidos"""
        self.assertIn(self.venda.status, [choice[0] for choice in Venda.STATUS_CHOICES])
        
    def test_venda_fechar(self):
        """Testa o fechamento de uma venda"""
        # Este teste seria mais completo se pudéssemos verificar a integração com o estoque
        self.venda.status = 'FECHADA'
        self.venda.save()
        venda_atualizada = Venda.objects.get(id=self.venda.id)
        self.assertEqual(venda_atualizada.status, 'FECHADA')