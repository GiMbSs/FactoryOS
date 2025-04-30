from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from comercial.models import Cliente, Fornecedor, Venda
from comercial.views.cliente_views import ClienteListView, ClienteCreateView, ClienteUpdateView

User = get_user_model()

class ClienteViewsTest(TestCase):
    """Testes para as views de Cliente"""
    
    def setUp(self):
        # Criar um usuário para testes de autenticação
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Criar alguns clientes para testes
        self.cliente1 = Cliente.objects.create(
            nome="Cliente Test 1",
            tipo="PF",
            email="cliente1@test.com",
            telefone="(11) 1111-1111",
            ativo=True
        )
        
        self.cliente2 = Cliente.objects.create(
            nome="Cliente Test 2",
            tipo="PJ",
            email="cliente2@test.com",
            telefone="(11) 2222-2222",
            ativo=False
        )
        
        # Cliente para uso em testes de edição
        self.cliente_para_editar = Cliente.objects.create(
            nome="Cliente Para Editar",
            tipo="PJ",
            email="editar@test.com",
            telefone="(11) 3333-3333",
            ativo=True
        )
        
        # Cliente para uso em testes de exclusão
        self.cliente_para_excluir = Cliente.objects.create(
            nome="Cliente Para Excluir",
            tipo="PF",
            email="excluir@test.com",
            telefone="(11) 4444-4444",
            ativo=True
        )
        
        # Criar um cliente para testes
        self.client = Client()

    def test_cliente_list_view(self):
        """Testa se a view de listagem de clientes funciona corretamente"""
        # Fazer login
        self.client.login(username='testuser', password='testpassword')
        
        # Acessar a página de listagem
        url = reverse('comercial:lista_clientes')
        response = self.client.get(url)
        
        # Verificar se a página foi carregada com sucesso
        self.assertEqual(response.status_code, 200)
        
        # Verificar se os clientes estão presentes no contexto
        self.assertIn('clientes', response.context)
        
        # Verificar se os dois clientes criados estão presentes
        clientes = list(response.context['clientes'])
        self.assertEqual(len(clientes), 4)
        
        # Verificar se as estatísticas estão presentes
        self.assertIn('clientes_ativos', response.context)
        self.assertEqual(response.context['clientes_ativos'], 3)  # 3 ativos, 1 inativo

    def test_cliente_create_view(self):
        """Testa se a view de criação de cliente funciona corretamente"""
        # Fazer login
        self.client.login(username='testuser', password='testpassword')
        
        # Dados para criação de cliente
        dados_cliente = {
            'nome': 'Novo Cliente',
            'tipo': 'PJ',
            'email': 'novo@cliente.com',
            'telefone': '(11) 5555-5555',
            'endereco': 'Rua Nova, 123',
            'ativo': True
        }
        
        # Enviar o formulário para a view de criação (corrigindo o nome da URL)
        url = reverse('comercial:cadastro_cliente')
        response = self.client.post(url, dados_cliente)
        
        # Verificar se houve redirecionamento (sucesso)
        self.assertEqual(response.status_code, 302)
        
        # Verificar se o cliente foi criado no banco de dados
        self.assertTrue(Cliente.objects.filter(nome='Novo Cliente').exists())

    def test_cliente_update_view(self):
        """Testa se a view de atualização de cliente funciona corretamente"""
        # Fazer login
        self.client.login(username='testuser', password='testpassword')
        
        # Dados para atualização do cliente
        dados_atualizados = {
            'nome': 'Cliente Editado',
            'tipo': 'PF',
            'email': 'editado@test.com',
            'telefone': '(11) 6666-6666',
            'endereco': 'Rua Editada, 456',
            'ativo': True
        }
        
        # Enviar o formulário para a view de atualização
        url = reverse('comercial:editar_cliente', kwargs={'pk': self.cliente_para_editar.pk})
        response = self.client.post(url, dados_atualizados)
        
        # Verificar se houve redirecionamento (sucesso)
        self.assertEqual(response.status_code, 302)
        
        # Verificar se o cliente foi atualizado no banco de dados
        cliente_atualizado = Cliente.objects.get(pk=self.cliente_para_editar.pk)
        self.assertEqual(cliente_atualizado.nome, 'Cliente Editado')
        self.assertEqual(cliente_atualizado.email, 'editado@test.com')

    def test_cliente_delete_view(self):
        """Testa se a view de exclusão de cliente funciona corretamente"""
        # Fazer login
        self.client.login(username='testuser', password='testpassword')
        
        # Verificar que o cliente existe antes da exclusão
        self.assertTrue(Cliente.objects.filter(pk=self.cliente_para_excluir.pk).exists())
        
        # Enviar o formulário para a view de exclusão
        url = reverse('comercial:excluir_cliente', kwargs={'pk': self.cliente_para_excluir.pk})
        response = self.client.post(url)
        
        # Verificar se houve redirecionamento (sucesso)
        self.assertEqual(response.status_code, 302)
        
        # Verificar se o cliente foi excluído do banco de dados
        self.assertFalse(Cliente.objects.filter(pk=self.cliente_para_excluir.pk).exists())

    def test_toggle_cliente_view(self):
        """Testa se a view de ativar/desativar cliente funciona corretamente"""
        # Fazer login
        self.client.login(username='testuser', password='testpassword')
        
        # Verificar status inicial (ativo)
        self.assertTrue(self.cliente1.ativo)
        
        # Enviar requisição para desativar o cliente
        url = reverse('comercial:toggle_cliente', kwargs={'pk': self.cliente1.pk})
        response = self.client.post(url)
        
        # Verificar se houve redirecionamento (sucesso)
        self.assertEqual(response.status_code, 302)
        
        # Verificar se o status do cliente foi alterado
        cliente_atualizado = Cliente.objects.get(pk=self.cliente1.pk)
        self.assertFalse(cliente_atualizado.ativo)