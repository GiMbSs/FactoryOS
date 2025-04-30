from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.utils import timezone
from datetime import timedelta

from producao.models import MateriaPrima, TipoMateriaPrima, Produto, TipoProduto, UnidadeMedida, ProdutoMateriaPrima
from estoque.models import MovimentacaoEstoque, SaldoEstoque, ProdutoEstoque
from estoque.forms import MateriaPrimaForm


class DashboardViewTest(TestCase):
    """Testes para a view de dashboard do estoque"""
    
    def setUp(self):
        # Criar usuário para autenticação
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpassword123')
        
        # Criar tipos necessários
        self.tipo_materia = TipoMateriaPrima.objects.create(nome="Tecido Filtrante")
        self.unidade = UnidadeMedida.objects.create(nome="Metro", sigla="m")
        
        # Criar matérias primas para testes
        self.materia_prima1 = MateriaPrima.objects.create(
            nome="Tecido 100% Algodão",
            tipo="TECIDO_PANO_CRU",
            tipo_materia_prima=self.tipo_materia,
            unidade_medida="METRO",
            unidade=self.unidade,
            custo_unitario=12.50,
            estoque_minimo=20.0
        )
        
        self.materia_prima2 = MateriaPrima.objects.create(
            nome="Tecido Sintético",
            tipo="TECIDO_SINTETICO",
            tipo_materia_prima=self.tipo_materia,
            unidade_medida="METRO",
            unidade=self.unidade,
            custo_unitario=8.75,
            estoque_minimo=15.0
        )
        
        # Inicializar saldos para as matérias-primas
        self.saldo1 = SaldoEstoque.objects.create(
            materia_prima=self.materia_prima1,
            quantidade_atual=30.0  # Acima do mínimo
        )
        
        self.saldo2 = SaldoEstoque.objects.create(
            materia_prima=self.materia_prima2,
            quantidade_atual=10.0  # Abaixo do mínimo
        )
        
        # Criar movimentações para testes
        # Últimos 6 meses
        for i in range(5, -1, -1):
            data = timezone.now() - timedelta(days=30 * i + 15)
            
            # Criar entradas
            MovimentacaoEstoque.objects.create(
                materia_prima=self.materia_prima1,
                quantidade=10.0,
                tipo_movimento='ENTRADA',
                origem_destino='FORNECEDOR',
                lote=f'LOTE-ENTRADA-{i}',
                data=data
            )
            
            # Criar saídas
            MovimentacaoEstoque.objects.create(
                materia_prima=self.materia_prima2,
                quantidade=5.0,
                tipo_movimento='SAIDA',
                origem_destino='PRODUCAO',
                lote=f'LOTE-SAIDA-{i}',
                data=data
            )
    
    def test_dashboard_acesso(self):
        """Testa o acesso à view de dashboard"""
        url = reverse('estoque:dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'estoque/dashboard.html')
    
    def test_dashboard_context(self):
        """Testa se o contexto do dashboard contém as informações corretas"""
        url = reverse('estoque:dashboard')
        response = self.client.get(url)
        
        # Verificar se o contexto contém as matérias-primas
        self.assertIn('materias_primas', response.context)
        self.assertEqual(response.context['materias_primas'].count(), 2)
        
        # Verificar se o valor total do estoque está sendo calculado
        self.assertIn('valor_total_estoque', response.context)
        
        # Verificar se os itens abaixo do estoque mínimo estão sendo contabilizados
        self.assertIn('itens_abaixo_minimo', response.context)
        self.assertEqual(response.context['itens_abaixo_minimo'], 1)  # materia_prima2 está abaixo
        
        # Verificar se os dados para gráficos estão presentes
        self.assertIn('dados_movimentacoes', response.context)
        self.assertIn('meses', response.context['dados_movimentacoes'])
        self.assertIn('entradas', response.context['dados_movimentacoes'])
        self.assertIn('saidas', response.context['dados_movimentacoes'])
        
        # Verificar se há 6 meses de dados
        self.assertEqual(len(response.context['dados_movimentacoes']['meses']), 6)


class MateriaPrimaViewsTest(TestCase):
    """Testes para as views de matéria-prima"""
    
    def setUp(self):
        # Criar usuário para autenticação
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpassword123')
        
        # Criar tipos necessários
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
        
        # Dados para criar uma nova matéria prima
        self.novos_dados = {
            'nome': "Papel Filtro",
            'descricao': "Papel especial para filtros",
            'tipo': "TECIDO_PANO_CRU",  # Alterado para usar um tipo válido
            'tipo_materia_prima': self.tipo_materia.id,  # Adicionado o tipo_materia_prima
            'unidade_medida': "METRO",
            'unidade': self.unidade.id,  # Adicionado a unidade
            'custo_unitario': 5.50,
            'estoque_minimo': 30.0,
            'ativo': True,
            'quantidade_estoque': 50.0
        }
    
    def test_materia_prima_create_view_get(self):
        """Testa o GET para a view de criação de matéria-prima"""
        url = reverse('estoque:materiaprima_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'estoque/cadastro_materiaprima.html')
        self.assertIsInstance(response.context['form'], MateriaPrimaForm)
    
    def test_materia_prima_create_view_post(self):
        """Testa o POST para a view de criação de matéria-prima"""
        url = reverse('estoque:materiaprima_create')
        response = self.client.post(url, self.novos_dados, follow=True)
        
        # Verificar se a matéria prima foi criada
        self.assertTrue(MateriaPrima.objects.filter(nome="Papel Filtro").exists())
        
        # Verificar se o saldo foi criado corretamente
        materia_nova = MateriaPrima.objects.get(nome="Papel Filtro")
        self.assertTrue(SaldoEstoque.objects.filter(materia_prima=materia_nova).exists())
        
        saldo = SaldoEstoque.objects.get(materia_prima=materia_nova)
        self.assertEqual(float(saldo.quantidade_atual), 50.0)
        
        # Verificar mensagem de sucesso
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('sucesso', str(messages[0]).lower())
    
    def test_materia_prima_update_view_get(self):
        """Testa o GET para a view de atualização de matéria-prima"""
        url = reverse('estoque:materiaprima_edit', args=[self.materia_prima.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'estoque/cadastro_materiaprima.html')
        self.assertIsInstance(response.context['form'], MateriaPrimaForm)
    
    def test_materia_prima_update_view_post(self):
        """Testa o POST para a view de atualização de matéria-prima"""
        # Criar saldo inicial
        SaldoEstoque.objects.create(
            materia_prima=self.materia_prima,
            quantidade_atual=25.0
        )
        
        # Dados para atualização
        dados_atualizados = {
            'nome': "Tecido 100% Algodão Premium",
            'descricao': "Tecido premium para filtros",
            'tipo': "TECIDO_PANO_CRU",
            'unidade_medida': "METRO",
            'custo_unitario': 15.75,
            'estoque_minimo': 25.0,
            'ativo': True,
            'quantidade_estoque': 40.0
        }
        
        url = reverse('estoque:materiaprima_edit', args=[self.materia_prima.id])
        response = self.client.post(url, dados_atualizados, follow=True)
        
        # Verificar se a matéria prima foi atualizada
        self.materia_prima.refresh_from_db()
        self.assertEqual(self.materia_prima.nome, "Tecido 100% Algodão Premium")
        self.assertEqual(float(self.materia_prima.custo_unitario), 15.75)
        
        # Verificar se o saldo foi atualizado corretamente
        saldo = SaldoEstoque.objects.get(materia_prima=self.materia_prima)
        self.assertEqual(float(saldo.quantidade_atual), 40.0)
        
        # Verificar mensagem de sucesso
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('sucesso', str(messages[0]).lower())
    
    def test_materia_prima_delete_view_get(self):
        """Testa o GET para a view de exclusão de matéria-prima"""
        url = reverse('estoque:materiaprima_delete', args=[self.materia_prima.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'estoque/confirmar_exclusao_materiaprima.html')
    
    def test_materia_prima_delete_view_post_sucesso(self):
        """Testa o POST para a view de exclusão de matéria-prima com sucesso"""
        url = reverse('estoque:materiaprima_delete', args=[self.materia_prima.id])
        response = self.client.post(url, follow=True)
        
        # Verificar se a matéria prima foi excluída
        self.assertFalse(MateriaPrima.objects.filter(id=self.materia_prima.id).exists())
        
        # Verificar mensagem de sucesso
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('sucesso', str(messages[0]).lower())
    
    def test_materia_prima_delete_view_post_com_movimentacoes(self):
        """Testa o POST para a view de exclusão de matéria-prima com movimentações"""
        # Criar uma movimentação para a matéria prima
        MovimentacaoEstoque.objects.create(
            materia_prima=self.materia_prima,
            quantidade=10.0,
            tipo_movimento='ENTRADA',
            origem_destino='FORNECEDOR',
            lote='LOTE-TEST-001'
        )
        
        url = reverse('estoque:materiaprima_delete', args=[self.materia_prima.id])
        response = self.client.post(url, follow=True)
        
        # Verificar se a matéria prima não foi excluída
        self.assertTrue(MateriaPrima.objects.filter(id=self.materia_prima.id).exists())
        
        # Verificar mensagem de erro
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('não é possível excluir', str(messages[0]).lower())
    
    def test_materia_prima_delete_view_post_com_produtos(self):
        """Testa o POST para a view de exclusão de matéria-prima usada em produtos"""
        # Criar tipo de produto
        tipo_produto = TipoProduto.objects.create(nome="Filtro de Café")
        
        # Criar produto
        produto = Produto.objects.create(
            nome="Filtro de Café Premium",
            descricao="Filtro de alta qualidade",
            codigo_sku="FC-PREMIUM-01", 
            tipo_produto=tipo_produto,
            tipo="MISTO"
        )
        
        # Associar a matéria prima ao produto - usando quantidade_utilizada em vez de quantidade
        ProdutoMateriaPrima.objects.create(
            produto=produto,
            materia_prima=self.materia_prima,
            quantidade_utilizada=0.5
        )
        
        url = reverse('estoque:materiaprima_delete', args=[self.materia_prima.id])
        response = self.client.post(url, follow=True)
        
        # Verificar se a matéria prima não foi excluída
        self.assertTrue(MateriaPrima.objects.filter(id=self.materia_prima.id).exists())
        
        # Verificar mensagem de erro
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('não é possível excluir', str(messages[0]).lower())


class EstoqueListViewTest(TestCase):
    """Testes para a view de listagem de estoque"""
    
    def setUp(self):
        # Criar usuário para autenticação
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpassword123')
        
        # Criar tipos necessários
        self.tipo_materia = TipoMateriaPrima.objects.create(nome="Tecido Filtrante")
        self.unidade = UnidadeMedida.objects.create(nome="Metro", sigla="m")
        
        # Criar matérias primas para testes
        self.materia_prima1 = MateriaPrima.objects.create(
            nome="Tecido 100% Algodão",
            tipo="TECIDO_PANO_CRU",
            tipo_materia_prima=self.tipo_materia,
            unidade_medida="METRO",
            unidade=self.unidade,
            custo_unitario=12.50,
            estoque_minimo=20.0
        )
        
        self.materia_prima2 = MateriaPrima.objects.create(
            nome="Tecido Sintético",
            tipo="TECIDO_SINTETICO",
            tipo_materia_prima=self.tipo_materia,
            unidade_medida="METRO",
            unidade=self.unidade,
            custo_unitario=8.75,
            estoque_minimo=15.0
        )
        
        # Inicializar saldos para as matérias-primas
        self.saldo1 = SaldoEstoque.objects.create(
            materia_prima=self.materia_prima1,
            quantidade_atual=30.0  # Acima do mínimo
        )
        
        self.saldo2 = SaldoEstoque.objects.create(
            materia_prima=self.materia_prima2,
            quantidade_atual=10.0  # Abaixo do mínimo
        )
    
    def test_estoque_list_view_acesso(self):
        """Testa o acesso à view de listagem de estoque"""
        url = reverse('estoque:estoque_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'estoque/estoque_list.html')
    
    def test_estoque_list_view_context(self):
        """Testa se o contexto da listagem contém as informações corretas"""
        url = reverse('estoque:estoque_list')
        response = self.client.get(url)
        
        # Verificar se o contexto contém as matérias-primas
        self.assertIn('materias_primas', response.context)
        self.assertEqual(response.context['materias_primas'].count(), 2)
        
        # Verificar se o contexto tem os produtos acabados
        self.assertIn('produtos_acabados', response.context)
        # Os produtos_acabados devem ser uma lista (possivelmente vazia no teste)
        self.assertIsInstance(response.context['produtos_acabados'], list)


class MovimentacaoViewTest(TestCase):
    """Testes para as views de movimentação de estoque"""
    
    def setUp(self):
        # Criar usuário para autenticação
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpassword123')
        
        # Criar tipos necessários
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
        
        # Inicializar saldo para a matéria-prima
        self.saldo = SaldoEstoque.objects.create(
            materia_prima=self.materia_prima,
            quantidade_atual=100.0
        )
        
        # Dados para criar uma nova movimentação
        self.dados_movimentacao = {
            'materia_prima': self.materia_prima.id,
            'quantidade': 50.0,
            'tipo_movimento': 'ENTRADA',
            'origem_destino': 'FORNECEDOR',
            'lote': 'LOTE-TEST-001',
            'observacao': 'Teste de movimentação'
        }
    
    def test_movimentacao_create_view_get(self):
        """Testa o GET para a view de criação de movimentação"""
        url = reverse('estoque:movimentacao_create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'estoque/movimentacao_form.html')
    
    def test_movimentacao_create_view_post(self):
        """Testa o POST para a view de criação de movimentação"""
        url = reverse('estoque:movimentacao_create')
        response = self.client.post(url, self.dados_movimentacao, follow=True)
        
        # Verificar se a movimentação foi criada
        self.assertTrue(MovimentacaoEstoque.objects.filter(lote='LOTE-TEST-001').exists())
        
        # Verificar se o saldo foi atualizado corretamente
        self.saldo.refresh_from_db()
        self.assertEqual(float(self.saldo.quantidade_atual), 150.0)  # 100 + 50
        
        # Verificar mensagem de sucesso
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('sucesso', str(messages[0]).lower())
    
    def test_movimentacao_list_view(self):
        """Testa a view de listagem de movimentações"""
        # Criar algumas movimentações para listar
        for i in range(3):
            MovimentacaoEstoque.objects.create(
                materia_prima=self.materia_prima,
                quantidade=10.0,
                tipo_movimento='ENTRADA',
                origem_destino='FORNECEDOR',
                lote=f'LOTE-TEST-{i+1}'
            )
        
        url = reverse('estoque:movimentacoes_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'estoque/movimentacoes_list.html')
        
        # Verificar se as movimentações estão no contexto
        self.assertIn('movimentacoes', response.context)
        self.assertEqual(len(response.context['movimentacoes']), 3)