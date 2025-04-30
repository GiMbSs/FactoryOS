from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from producao.models import Produto, TipoProduto
import json

User = get_user_model()

class ProdutoAPITest(TestCase):
    """Testes para a API REST de Produtos"""
    
    def setUp(self):
        # Criar um usuário para autenticação
        self.user = User.objects.create_user(
            username='apiuser',
            password='apipassword',
            email='api@test.com'
        )
        
        # Inicializar o cliente da API
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Criar um tipo de produto
        self.tipo_produto = TipoProduto.objects.create(
            nome="Filtro de Café",
            descricao="Filtros para coar café"
        )
        
        # Criar alguns produtos para testar a API
        self.produto1 = Produto.objects.create(
            nome="Filtro de Café Premium",
            descricao="Filtro de alta qualidade",
            codigo_sku="FC-PREMIUM-01",
            tipo_produto=self.tipo_produto,
            tipo="TECIDO"
        )
        
        self.produto2 = Produto.objects.create(
            nome="Filtro de Café Básico",
            descricao="Filtro de uso diário",
            codigo_sku="FC-BASIC-01",
            tipo_produto=self.tipo_produto,
            tipo="PLASTICO"
        )
        
        # URL para a API de produtos (nome correto da URL)
        self.url_lista = '/producao/api/produtos/'
    
    def test_listar_produtos_api(self):
        """Testa a listagem de produtos via API"""
        response = self.client.get(self.url_lista)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar se a resposta contém os produtos criados
        data = response.json()
        self.assertEqual(len(data), 2)  # Devem existir os 2 produtos que criamos
        
        # Verificar se os produtos estão na resposta
        nomes_produtos = [item['nome'] for item in data]
        self.assertIn("Filtro de Café Premium", nomes_produtos)
        self.assertIn("Filtro de Café Básico", nomes_produtos)
    
    def test_detalhar_produto_api(self):
        """Testa o detalhamento de um produto via API"""
        url_detalhe = f'/producao/api/produtos/{self.produto1.pk}/'
        response = self.client.get(url_detalhe)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar se os dados estão corretos
        data = response.json()
        self.assertEqual(data['nome'], "Filtro de Café Premium")
        self.assertEqual(data['codigo_sku'], "FC-PREMIUM-01")
        self.assertEqual(data['tipo'], "TECIDO")
    
    def test_criar_produto_api(self):
        """Testa a criação de um produto via API"""
        dados_produto = {
            'nome': 'Filtro de Café Descartável',
            'descricao': 'Filtro descartável para uso único',
            'codigo_sku': 'FC-DESCARTAVEL-01',
            'tipo_produto': self.tipo_produto.id,
            'tipo': 'MISTO'  # Alterado de 'PAPEL' para 'MISTO' que é um valor válido
        }
        
        response = self.client.post(self.url_lista, dados_produto, format='json')
        
        # Verificar se a criação foi bem-sucedida
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar se o produto foi realmente criado no banco
        self.assertTrue(Produto.objects.filter(codigo_sku='FC-DESCARTAVEL-01').exists())
    
    def test_atualizar_produto_api(self):
        """Testa a atualização de um produto via API"""
        url_detalhe = f'/producao/api/produtos/{self.produto1.pk}/'
        
        dados_atualizados = {
            'nome': 'Filtro de Café Premium V2',
            'descricao': 'Versão atualizada do filtro premium',
            'codigo_sku': 'FC-PREMIUM-01',  # Mantém o SKU para não violar a restrição unique
            'tipo_produto': self.tipo_produto.id,
            'tipo': 'TECIDO'
        }
        
        response = self.client.put(url_detalhe, dados_atualizados, format='json')
        
        # Verificar se a atualização foi bem-sucedida
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar se o produto foi realmente atualizado no banco
        produto_atualizado = Produto.objects.get(pk=self.produto1.pk)
        self.assertEqual(produto_atualizado.nome, 'Filtro de Café Premium V2')
        self.assertEqual(produto_atualizado.descricao, 'Versão atualizada do filtro premium')
    
    def test_deletar_produto_api(self):
        """Testa a exclusão de um produto via API"""
        url_detalhe = f'/producao/api/produtos/{self.produto2.pk}/'
        
        response = self.client.delete(url_detalhe)
        
        # Verificar se a exclusão foi bem-sucedida
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verificar se o produto foi realmente excluído do banco
        self.assertFalse(Produto.objects.filter(pk=self.produto2.pk).exists())