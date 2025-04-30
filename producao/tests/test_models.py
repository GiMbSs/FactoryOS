from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model
from producao.models import (
    Categoria, UnidadeMedida, TipoMateriaPrima, MateriaPrima,
    TipoProduto, Produto, ProdutoMateriaPrima, OrdemProducao
)
from comercial.models import Fornecedor

User = get_user_model()

class CategoriaModelTest(TestCase):
    """Testes para o modelo Categoria"""
    
    def setUp(self):
        self.categoria = Categoria.objects.create(
            nome="Filtros de Café",
            descricao="Categoria de filtros para café",
            segmento="coadores",
            icone="bi-cup-hot",
            cor="primary",
            ordem=1,
            ativo=True
        )
    
    def test_categoria_criacao(self):
        """Testa se a categoria foi criada corretamente"""
        self.assertEqual(Categoria.objects.count(), 1)
        self.assertEqual(self.categoria.nome, "Filtros de Café")
    
    def test_categoria_str(self):
        """Testa a representação em string da categoria"""
        self.assertEqual(str(self.categoria), "Filtros de Café")
    
    def test_categoria_slug_auto(self):
        """Testa se o slug é gerado automaticamente"""
        self.assertEqual(self.categoria.slug, "filtros-de-cafe")
        
        # Criar uma categoria sem especificar o slug
        nova_categoria = Categoria.objects.create(
            nome="Cafeteiras Manuais",
            descricao="Categoria de cafeteiras manuais"
        )
        self.assertEqual(nova_categoria.slug, "cafeteiras-manuais")


class UnidadeMedidaModelTest(TestCase):
    """Testes para o modelo UnidadeMedida"""
    
    def setUp(self):
        self.unidade = UnidadeMedida.objects.create(
            nome="Quilograma",
            sigla="kg",
            descricao="Unidade de medida de massa"
        )
    
    def test_unidade_criacao(self):
        """Testa se a unidade foi criada corretamente"""
        self.assertEqual(UnidadeMedida.objects.count(), 1)
        self.assertEqual(self.unidade.nome, "Quilograma")
    
    def test_unidade_str(self):
        """Testa a representação em string da unidade"""
        self.assertEqual(str(self.unidade), "kg - Quilograma")


class TipoMateriaPrimaModelTest(TestCase):
    """Testes para o modelo TipoMateriaPrima"""
    
    def setUp(self):
        self.tipo = TipoMateriaPrima.objects.create(
            nome="Tecido Filtrante",
            descricao="Tecidos usados para filtrar café",
            icone="bi-cup",
            cor="info",
            ativo=True
        )
    
    def test_tipo_criacao(self):
        """Testa se o tipo foi criado corretamente"""
        self.assertEqual(TipoMateriaPrima.objects.count(), 1)
        self.assertEqual(self.tipo.nome, "Tecido Filtrante")
    
    def test_tipo_str(self):
        """Testa a representação em string do tipo"""
        self.assertEqual(str(self.tipo), "Tecido Filtrante")


class MateriaPrimaModelTest(TestCase):
    """Testes para o modelo MateriaPrima"""
    
    def setUp(self):
        # Criar objetos relacionados
        self.tipo_materia = TipoMateriaPrima.objects.create(
            nome="Tecido Filtrante",
            icone="bi-cup"
        )
        
        self.categoria = Categoria.objects.create(
            nome="Filtros de Café"
        )
        
        self.unidade = UnidadeMedida.objects.create(
            nome="Metro",
            sigla="m"
        )
        
        self.fornecedor = Fornecedor.objects.create(
            nome="Fornecedor de Tecidos",
            cnpj="12.345.678/0001-90",
            email="tecidos@teste.com",
            telefone="(11) 1234-5678"
        )
        
        # Criar a matéria-prima
        self.materia = MateriaPrima.objects.create(
            nome="Tecido 100% Algodão",
            descricao="Tecido ideal para filtros de café",
            tipo="TECIDO_PANO_CRU",
            tipo_materia_prima=self.tipo_materia,
            categoria=self.categoria,
            unidade_medida="METRO",
            unidade=self.unidade,
            codigo="TC-001",
            custo_unitario=12.50,
            estoque_minimo=10.0,
            fornecedor_padrao=self.fornecedor,
            ativo=True
        )
    
    def test_materia_criacao(self):
        """Testa se a matéria-prima foi criada corretamente"""
        self.assertEqual(MateriaPrima.objects.count(), 1)
        self.assertEqual(self.materia.nome, "Tecido 100% Algodão")
        self.assertEqual(self.materia.custo_unitario, 12.50)
    
    def test_materia_str(self):
        """Testa a representação em string da matéria-prima"""
        self.assertEqual(str(self.materia), "Tecido 100% Algodão (Tecido Filtrante)")


class ProdutoModelTest(TestCase):
    """Testes para o modelo Produto"""
    
    def setUp(self):
        # Criar objetos relacionados
        self.tipo_produto = TipoProduto.objects.create(
            nome="Filtro de Café",
            descricao="Filtros para coar café"
        )
        
        # Criar o produto
        self.produto = Produto.objects.create(
            nome="Filtro de Café Premium",
            descricao="Filtro de alta qualidade",
            codigo_sku="FC-PREMIUM-01",
            tipo_produto=self.tipo_produto,
            tipo="MISTO"
        )
        
        # Criar matéria-prima para associar ao produto
        self.tipo_materia = TipoMateriaPrima.objects.create(nome="Tecido Filtrante")
        self.unidade = UnidadeMedida.objects.create(nome="Metro", sigla="m")
        
        self.materia = MateriaPrima.objects.create(
            nome="Tecido 100% Algodão",
            tipo="TECIDO_PANO_CRU",
            tipo_materia_prima=self.tipo_materia,
            unidade_medida="METRO",
            unidade=self.unidade,
            custo_unitario=12.50
        )
        
        # Associar matéria-prima ao produto
        self.produto_materia = ProdutoMateriaPrima.objects.create(
            produto=self.produto,
            materia_prima=self.materia,
            quantidade_utilizada=0.5
        )
    
    def test_produto_criacao(self):
        """Testa se o produto foi criado corretamente"""
        self.assertEqual(Produto.objects.count(), 1)
        self.assertEqual(self.produto.nome, "Filtro de Café Premium")
    
    def test_produto_str(self):
        """Testa a representação em string do produto"""
        self.assertEqual(str(self.produto), "Filtro de Café Premium (Filtro de Café)")
    
    def test_produto_materias_primas(self):
        """Testa se as matérias-primas estão associadas ao produto"""
        materias = self.produto.materias_primas.all()
        self.assertEqual(materias.count(), 1)
        self.assertEqual(materias.first().nome, "Tecido 100% Algodão")
        
        # Testar a relação através do modelo intermediário
        relacao = ProdutoMateriaPrima.objects.get(produto=self.produto)
        self.assertEqual(relacao.quantidade_utilizada, 0.5)


class OrdemProducaoModelTest(TestCase):
    """Testes para o modelo OrdemProducao"""
    
    def setUp(self):
        # Criar usuário responsável
        self.usuario = User.objects.create_user(
            username="producao",
            password="senha123"
        )
        
        # Criar produto
        self.tipo_produto = TipoProduto.objects.create(nome="Filtro de Café")
        self.produto = Produto.objects.create(
            nome="Filtro de Café Premium",
            codigo_sku="FC-PREMIUM-01",
            tipo_produto=self.tipo_produto,
            tipo="MISTO"
        )
        
        # Criar ordem de produção
        self.ordem = OrdemProducao.objects.create(
            produto=self.produto,
            quantidade=100,
            status="PLANEJADA",
            data_inicio=timezone.now().date(),
            responsavel=self.usuario
        )
    
    def test_ordem_criacao(self):
        """Testa se a ordem de produção foi criada corretamente"""
        self.assertEqual(OrdemProducao.objects.count(), 1)
        self.assertEqual(self.ordem.quantidade, 100)
        self.assertEqual(self.ordem.status, "PLANEJADA")
    
    def test_ordem_str(self):
        """Testa a representação em string da ordem de produção"""
        self.assertEqual(str(self.ordem), f"OP-{self.ordem.id} - Filtro de Café Premium (Filtro de Café) (Planejada)")
    
    def test_ordem_alterar_status(self):
        """Testa a alteração de status da ordem de produção"""
        self.ordem.status = "EM_PRODUCAO"
        self.ordem.save()
        
        ordem_atualizada = OrdemProducao.objects.get(id=self.ordem.id)
        self.assertEqual(ordem_atualizada.status, "EM_PRODUCAO")
        
        # Finalizar a ordem
        ordem_atualizada.status = "FINALIZADA"
        ordem_atualizada.data_fim = timezone.now().date()
        ordem_atualizada.save()
        
        ordem_finalizada = OrdemProducao.objects.get(id=self.ordem.id)
        self.assertEqual(ordem_finalizada.status, "FINALIZADA")
        self.assertIsNotNone(ordem_finalizada.data_fim)