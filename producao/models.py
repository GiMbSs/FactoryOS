from django.db import models
from django.core.validators import MinValueValidator

class MateriaPrima(models.Model):
    TIPO_CHOICES = [
        ('MADEIRA_BRUTA', 'Madeira Bruta'),
        ('VARETA_MADEIRA', 'Vareta de Madeira'),
        ('TECIDO_MALHA', 'Tecido Malha'),
        ('TECIDO_PANO_CRU', 'Tecido Pano Cru'),
        ('CABO_PLASTICO', 'Cabo Plástico'),
    ]
    
    UNIDADE_CHOICES = [
        ('KG', 'Quilograma'),
        ('METRO', 'Metro'),
        ('UNIDADE', 'Unidade'),
    ]

    nome = models.CharField('Nome', max_length=100)
    descricao = models.TextField('Descrição', blank=True)
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES)
    unidade_medida = models.CharField('Unidade de Medida', max_length=10, choices=UNIDADE_CHOICES)
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
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Matéria Prima'
        verbose_name_plural = 'Matérias Primas'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"

class Produto(models.Model):
    TIPO_CHOICES = [
        ('PLASTICO', 'Plástico'),
        ('MADEIRA', 'Madeira'),
    ]

    nome = models.CharField('Nome', max_length=100)
    descricao = models.TextField('Descrição', blank=True)
    codigo_sku = models.CharField('SKU', max_length=20, unique=True)
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
        return f"{self.nome} ({self.get_tipo_display()})"

    def calcular_custo(self):
        from decimal import Decimal, ROUND_HALF_UP
        custo_materias = sum(
            pm.quantidade_utilizada * pm.materia_prima.custo_unitario
            for pm in self.produtomateriaprima_set.all()
        )
        if not isinstance(custo_materias, Decimal):
            custo_materias = Decimal(str(custo_materias))
        mao_obra = Decimal('2.50') if self.tipo == 'PLASTICO' else Decimal('4.00')
        custo_total = custo_materias + mao_obra
        custo_indireto = custo_total * Decimal('0.10')
        total = custo_total + custo_indireto
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

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
