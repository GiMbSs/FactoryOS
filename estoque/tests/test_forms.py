from django.test import TestCase
from estoque.forms import SaldoEstoqueForm, MateriaPrimaForm
from estoque.models import SaldoEstoque
from producao.models import MateriaPrima, TipoMateriaPrima, UnidadeMedida

class SaldoEstoqueFormTest(TestCase):
    """Testes para o formulário de Saldo de Estoque"""
    
    def setUp(self):
        # Criar tipo de matéria prima para testes
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
        
        # Dados válidos para o formulário
        self.dados_validos = {
            'materia_prima': self.materia_prima.id,
            'quantidade_atual': 100.00,
        }
    
    def test_form_valido(self):
        """Testa se o formulário é válido com dados corretos"""
        form = SaldoEstoqueForm(self.dados_validos)
        self.assertTrue(form.is_valid())
    
    def test_form_invalido_sem_materia_prima(self):
        """Testa se o formulário é inválido sem matéria prima"""
        dados_invalidos = self.dados_validos.copy()
        dados_invalidos['materia_prima'] = None
        form = SaldoEstoqueForm(dados_invalidos)
        self.assertFalse(form.is_valid())
        self.assertIn('materia_prima', form.errors)
    
    def test_form_invalido_quantidade_negativa(self):
        """Testa se o formulário é inválido com quantidade negativa"""
        dados_invalidos = self.dados_validos.copy()
        dados_invalidos['quantidade_atual'] = -10.00
        form = SaldoEstoqueForm(dados_invalidos)
        self.assertFalse(form.is_valid())
        self.assertIn('quantidade_atual', form.errors)
    
    def test_atualizacao_saldo_existente(self):
        """Testa atualização de um saldo já existente"""
        # Criar um saldo inicial
        saldo = SaldoEstoque.objects.create(
            materia_prima=self.materia_prima,
            quantidade_atual=50.00
        )
        
        # Atualizar via formulário
        dados_atualizacao = {
            'materia_prima': self.materia_prima.id,
            'quantidade_atual': 150.00,
        }
        
        form = SaldoEstoqueForm(dados_atualizacao, instance=saldo)
        self.assertTrue(form.is_valid())
        
        # Salvar e verificar se o saldo foi atualizado
        form.save()
        saldo_atualizado = SaldoEstoque.objects.get(materia_prima=self.materia_prima)
        self.assertEqual(float(saldo_atualizado.quantidade_atual), 150.00)


class MateriaPrimaFormTest(TestCase):
    """Testes para o formulário de Matéria Prima com Estoque"""
    
    def setUp(self):
        # Criar tipo de matéria prima para testes
        self.tipo_materia = TipoMateriaPrima.objects.create(nome="Tecido Filtrante")
        self.unidade = UnidadeMedida.objects.create(nome="Metro", sigla="m")
        
        # Dados válidos para o formulário
        self.dados_validos = {
            'nome': "Tecido 100% Algodão",
            'descricao': "Tecido de alta qualidade para filtros de café",
            'tipo': "TECIDO_PANO_CRU",
            'unidade_medida': "METRO",
            'custo_unitario': 12.50,
            'estoque_minimo': 20.00,
            'ativo': True,
            'quantidade_estoque': 100.00  # Campo adicional do formulário
        }
    
    def test_form_valido(self):
        """Testa se o formulário é válido com dados corretos"""
        form = MateriaPrimaForm(self.dados_validos)
        self.assertTrue(form.is_valid())
    
    def test_form_valido_sem_estoque_inicial(self):
        """Testa se o formulário é válido sem informar estoque inicial"""
        dados_sem_estoque = self.dados_validos.copy()
        dados_sem_estoque.pop('quantidade_estoque')
        form = MateriaPrimaForm(dados_sem_estoque)
        self.assertTrue(form.is_valid())
    
    def test_form_invalido_sem_nome(self):
        """Testa se o formulário é inválido sem nome"""
        dados_invalidos = self.dados_validos.copy()
        dados_invalidos['nome'] = ''
        form = MateriaPrimaForm(dados_invalidos)
        self.assertFalse(form.is_valid())
        self.assertIn('nome', form.errors)
    
    def test_form_invalido_custo_negativo(self):
        """Testa se o formulário é inválido com custo negativo"""
        dados_invalidos = self.dados_validos.copy()
        dados_invalidos['custo_unitario'] = -5.00
        form = MateriaPrimaForm(dados_invalidos)
        self.assertFalse(form.is_valid())
        self.assertIn('custo_unitario', form.errors)
    
    def test_form_invalido_estoque_negativo(self):
        """Testa se o formulário é inválido com estoque negativo"""
        dados_invalidos = self.dados_validos.copy()
        dados_invalidos['quantidade_estoque'] = -10.00
        form = MateriaPrimaForm(dados_invalidos)
        self.assertFalse(form.is_valid())
        self.assertIn('quantidade_estoque', form.errors)