from django.test import TestCase
from comercial.forms import ClienteForm, FornecedorForm, VendaForm, ItemVendaForm
from comercial.models import Cliente, Fornecedor, Venda, ItemVenda
from django.contrib.auth import get_user_model
from producao.models import Produto, TipoProduto

User = get_user_model()

class ClienteFormTest(TestCase):
    """Testes para o formulário de Cliente"""
    
    def test_cliente_form_valido(self):
        """Testa se o formulário de cliente é válido com dados corretos"""
        form_data = {
            'nome': 'Cliente Teste Form',
            'tipo': 'PJ',
            'cnpj_cpf': '12.345.678/0001-90',
            'email': 'cliente@teste.com',
            'telefone': '(11) 99999-8888',
            'endereco': 'Av. Teste, 123'
        }
        form = ClienteForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_cliente_form_invalido_email(self):
        """Testa se o formulário de cliente é inválido com email incorreto"""
        form_data = {
            'nome': 'Cliente Teste Form',
            'tipo': 'PJ',
            'cnpj_cpf': '12.345.678/0001-90',
            'email': 'email-invalido',  # Email inválido
            'telefone': '(11) 99999-8888',
            'endereco': 'Av. Teste, 123'
        }
        form = ClienteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_cliente_form_campos_obrigatorios(self):
        """Testa se os campos obrigatórios são validados"""
        # Formulário vazio
        form = ClienteForm(data={})
        self.assertFalse(form.is_valid())
        # Verificar campos obrigatórios
        self.assertIn('nome', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('telefone', form.errors)


class FornecedorFormTest(TestCase):
    """Testes para o formulário de Fornecedor"""
    
    def test_fornecedor_form_valido(self):
        """Testa se o formulário de fornecedor é válido com dados corretos"""
        form_data = {
            'nome': 'Fornecedor Teste Form',
            'cnpj': '12.345.678/0001-90',
            'email': 'fornecedor@teste.com',
            'telefone': '(11) 99999-7777'
        }
        form = FornecedorForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_fornecedor_form_invalido_email(self):
        """Testa se o formulário de fornecedor é inválido com email incorreto"""
        form_data = {
            'nome': 'Fornecedor Teste Form',
            'cnpj': '12.345.678/0001-90',
            'email': 'email-invalido',  # Email inválido
            'telefone': '(11) 99999-7777'
        }
        form = FornecedorForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_fornecedor_form_campos_obrigatorios(self):
        """Testa se os campos obrigatórios são validados"""
        # Formulário vazio
        form = FornecedorForm(data={})
        self.assertFalse(form.is_valid())
        # Verificar campos obrigatórios
        self.assertIn('nome', form.errors)
        self.assertIn('cnpj', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('telefone', form.errors)


class VendaFormTest(TestCase):
    """Testes para o formulário de Venda"""
    
    def setUp(self):
        # Criar um usuário para testes
        self.user = User.objects.create_user(username='testuser', password='password')
        
        # Criar um cliente para testes
        self.cliente = Cliente.objects.create(
            nome="Cliente Teste",
            email="cliente@teste.com",
            telefone="(11) 99999-6666"
        )
    
    def test_venda_form_valido(self):
        """Testa se o formulário de venda é válido com dados corretos"""
        form_data = {
            'cliente': self.cliente.id,
            'vendedor': self.user.id,
            'valor_total': '150.50',
            'status': 'ABERTA',
            'observacoes': 'Venda de teste'
        }
        form = VendaForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_venda_form_campos_obrigatorios(self):
        """Testa se os campos obrigatórios são validados"""
        # Formulário vazio
        form = VendaForm(data={})
        self.assertFalse(form.is_valid())
        # Verificar campos obrigatórios
        self.assertIn('cliente', form.errors)
        self.assertIn('vendedor', form.errors)
        self.assertIn('valor_total', form.errors)


class ItemVendaFormTest(TestCase):
    """Testes para o formulário de Item de Venda"""
    
    def setUp(self):
        # Criar um tipo de produto
        self.tipo_produto = TipoProduto.objects.create(nome="Filtro")
        
        # Criar um produto para testes - removendo preco_venda que não existe mais
        self.produto = Produto.objects.create(
            nome="Filtro de Café Premium",
            descricao="Filtro de alta qualidade",
            codigo_sku="FC-PREMIUM-01",
            tipo_produto=self.tipo_produto,
            tipo="TECIDO"
        )
    
    def test_item_venda_form_valido(self):
        """Testa se o formulário de item de venda é válido com dados corretos"""
        form_data = {
            'produto': self.produto.id,
            'quantidade': 5,
            'preco_unitario': '10.50'
        }
        form = ItemVendaForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_item_venda_form_campos_obrigatorios(self):
        """Testa se os campos obrigatórios são validados"""
        # Formulário vazio
        form = ItemVendaForm(data={})
        self.assertFalse(form.is_valid())
        # Verificar campos obrigatórios
        self.assertIn('produto', form.errors)
        self.assertIn('quantidade', form.errors)
        self.assertIn('preco_unitario', form.errors)