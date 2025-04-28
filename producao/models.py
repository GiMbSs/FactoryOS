from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify

class Categoria(models.Model):
    nome = models.CharField('Nome', max_length=100)
    descricao = models.TextField('Descrição', blank=True)
    slug = models.SlugField('Slug', max_length=100, unique=True)
    segmento = models.CharField('Segmento', max_length=50, default='coadores')
    icone = models.CharField('Ícone', max_length=50, blank=True, help_text='Nome do ícone Bootstrap, ex: bi-box')
    cor = models.CharField('Cor', max_length=20, default='primary', help_text='Nome da cor Bootstrap: primary, success, etc')
    ordem = models.PositiveSmallIntegerField('Ordem', default=0)
    ativo = models.BooleanField('Ativo', default=True)
    
    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['ordem', 'nome']
    
    def __str__(self):
        return self.nome
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)


class UnidadeMedida(models.Model):
    nome = models.CharField('Nome', max_length=50)
    sigla = models.CharField('Sigla', max_length=10)
    descricao = models.TextField('Descrição', blank=True)
    
    class Meta:
        verbose_name = 'Unidade de Medida'
        verbose_name_plural = 'Unidades de Medida'
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.sigla} - {self.nome}"


class MateriaPrima(models.Model):
    # Mantemos os TIPO_CHOICES para compatibilidade com código existente
    TIPO_CHOICES = [
        ('MADEIRA_BRUTA', 'Madeira Bruta'),
        ('VARETA_MADEIRA', 'Vareta de Madeira'),
        ('TECIDO_MALHA', 'Tecido Malha'),
        ('TECIDO_PANO_CRU', 'Tecido Pano Cru'),
        ('CABO_PLASTICO', 'Cabo Plástico'),
    ]
    
    # Mantemos os UNIDADE_CHOICES para compatibilidade com código existente
    UNIDADE_CHOICES = [
        ('KG', 'Quilograma'),
        ('METRO', 'Metro'),
        ('UNIDADE', 'Unidade'),
    ]

    nome = models.CharField('Nome', max_length=100)
    descricao = models.TextField('Descrição', blank=True)
    # Mantemos o campo tipo para compatibilidade, mas adicionamos categoria
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES)
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Categoria'
    )
    # Mantemos o campo unidade_medida para compatibilidade, mas adicionamos unidade
    unidade_medida = models.CharField('Unidade de Medida', max_length=10, choices=UNIDADE_CHOICES)
    unidade = models.ForeignKey(
        UnidadeMedida, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Unidade'
    )
    codigo = models.CharField('Código', max_length=20, blank=True, help_text='Código interno ou SKU do fornecedor')
    custo_unitario = models.DecimalField(
        'Custo Unitário', 
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0.00
    )
    estoque_minimo = models.DecimalField(
        'Estoque Mínimo', 
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    imagem = models.ImageField('Imagem', upload_to='materias_primas/', blank=True, null=True)
    fornecedor_padrao = models.ForeignKey(
        'comercial.Fornecedor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Fornecedor Padrão',
        related_name='materias_primas'
    )
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Matéria Prima'
        verbose_name_plural = 'Matérias Primas'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"

class TipoProduto(models.Model):
    nome = models.CharField('Nome', max_length=50)
    descricao = models.TextField('Descrição', blank=True)
    icone = models.CharField('Ícone', max_length=50, blank=True, help_text='Nome do ícone Bootstrap, ex: bi-box')
    cor = models.CharField('Cor', max_length=20, default='primary', help_text='Nome da cor Bootstrap: primary, success, etc')
    ativo = models.BooleanField('Ativo', default=True)
    
    class Meta:
        verbose_name = 'Tipo de Produto'
        verbose_name_plural = 'Tipos de Produto'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome

class Produto(models.Model):
    # Mantemos os TIPO_CHOICES para compatibilidade com código existente
    TIPO_CHOICES = [
        ('PLASTICO', 'Plástico'),
        ('MADEIRA', 'Madeira'),
        ('TECIDO', 'Tecido'),
        ('MISTO', 'Misto'),
    ]

    nome = models.CharField('Nome', max_length=100)
    descricao = models.TextField('Descrição', blank=True)
    codigo_sku = models.CharField('SKU', max_length=20, unique=True)
    
    # Adicionamos um campo ForeignKey para o novo modelo TipoProduto
    tipo_produto = models.ForeignKey(
        TipoProduto,
        on_delete=models.PROTECT,
        verbose_name='Tipo de Produto',
        null=True,
        blank=True
    )
    
    # Mantemos o campo tipo para compatibilidade com código existente
    tipo = models.CharField('Tipo', max_length=10, choices=TIPO_CHOICES)
    
    materias_primas = models.ManyToManyField(
        MateriaPrima,
        through='ProdutoMateriaPrima',
        verbose_name='Matérias Primas'
    )

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['nome']

    def __str__(self):
        if self.tipo_produto:
            return f"{self.nome} ({self.tipo_produto.nome})"
        return f"{self.nome} ({self.get_tipo_display()})"

    def calcular_custo(self):
        # Delegamos a lógica para o service
        from .services import ProdutoService
        return ProdutoService.calcular_custo(self)

class ProdutoMateriaPrima(models.Model):
    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        verbose_name='Produto'
    )
    materia_prima = models.ForeignKey(
        MateriaPrima,
        on_delete=models.CASCADE,
        verbose_name='Matéria Prima'
    )
    quantidade_utilizada = models.DecimalField(
        'Quantidade Utilizada',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    observacoes = models.TextField('Observações', blank=True)

    class Meta:
        verbose_name = 'Relação Produto-Matéria Prima'
        verbose_name_plural = 'Relações Produto-Matéria Prima'
        unique_together = ('produto', 'materia_prima')

    def __str__(self):
        return f"{self.produto} - {self.materia_prima}"

from estoque.models import ProdutoEstoque

class OrdemProducao(models.Model):
    STATUS_CHOICES = [
        ('PLANEJADA', 'Planejada'),
        ('EM_PRODUCAO', 'Em Produção'),
        ('FINALIZADA', 'Finalizada'),
        ('CANCELADA', 'Cancelada'),
    ]

    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        verbose_name='Produto'
    )
    quantidade = models.PositiveIntegerField('Quantidade')
    status = models.CharField(
        'Status',
        max_length=15,
        choices=STATUS_CHOICES,
        default='PLANEJADA'
    )
    data_inicio = models.DateField('Data de Início', null=True, blank=True)
    data_fim = models.DateField('Data de Término', null=True, blank=True)
    responsavel = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Responsável'
    )

    class Meta:
        verbose_name = 'Ordem de Produção'
        verbose_name_plural = 'Ordens de Produção'
        ordering = ['-data_inicio']

    def __str__(self):
        return f"OP-{self.id} - {self.produto} ({self.get_status_display()})"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('producao:ordem_detail', kwargs={'pk': self.pk})
