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


class TipoMateriaPrima(models.Model):
    nome = models.CharField('Nome', max_length=50)
    descricao = models.TextField('Descrição', blank=True)
    icone = models.CharField('Ícone', max_length=50, default='bi-box', blank=True, help_text='Nome do ícone Bootstrap, ex: bi-box')
    cor = models.CharField('Cor', max_length=20, default='primary', blank=True, help_text='Nome da cor Bootstrap: primary, success, etc')
    ativo = models.BooleanField('Ativo', default=True)
    
    class Meta:
        verbose_name = 'Tipo de Matéria Prima'
        verbose_name_plural = 'Tipos de Matéria Prima'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


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
    
    # Mantemos o campo tipo para compatibilidade, mas adicionamos tipo_materia_prima
    tipo = models.CharField('Tipo (Legado)', max_length=20, choices=TIPO_CHOICES, blank=True, null=True)
    
    # Novo campo para o tipo de matéria prima
    tipo_materia_prima = models.ForeignKey(
        TipoMateriaPrima,
        on_delete=models.PROTECT,
        verbose_name='Tipo de Matéria Prima',
        null=True,
        blank=True
    )
    
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
        tipo_display = self.tipo_materia_prima.nome if self.tipo_materia_prima else self.get_tipo_display()
        return f"{self.nome} ({tipo_display})"

    @staticmethod
    def migrar_tipos_existentes():
        """
        Migra os tipos antigos para os novos tipos de matéria-prima.
        Deve ser executado após a criação do modelo TipoMateriaPrima.
        """
        from django.db import transaction
        
        # Mapeamento dos tipos antigos para novos
        mapeamento_tipos = {
            'MADEIRA_BRUTA': {'nome': 'Madeira Bruta', 'icone': 'bi-tree', 'cor': 'success'},
            'VARETA_MADEIRA': {'nome': 'Vareta de Madeira', 'icone': 'bi-rulers', 'cor': 'success'},
            'TECIDO_MALHA': {'nome': 'Tecido Malha', 'icone': 'bi-basket', 'cor': 'info'},
            'TECIDO_PANO_CRU': {'nome': 'Tecido Pano Cru', 'icone': 'bi-basket', 'cor': 'info'},
            'CABO_PLASTICO': {'nome': 'Cabo Plástico', 'icone': 'bi-box', 'cor': 'warning'},
        }
        
        try:
            with transaction.atomic():
                tipos_criados = {}
                
                # Para cada tipo antigo, cria um novo tipo
                for tipo_key, tipo_data in mapeamento_tipos.items():
                    novo_tipo, criado = TipoMateriaPrima.objects.get_or_create(
                        nome=tipo_data['nome'],
                        defaults={
                            'icone': tipo_data['icone'],
                            'cor': tipo_data['cor'],
                            'descricao': f'Migrado automaticamente do tipo antigo: {tipo_key}'
                        }
                    )
                    tipos_criados[tipo_key] = novo_tipo
                
                # Atualiza todas as matérias-primas para usar os novos tipos
                for material in MateriaPrima.objects.all():
                    if material.tipo in tipos_criados and not material.tipo_materia_prima:
                        material.tipo_materia_prima = tipos_criados[material.tipo]
                        material.save(update_fields=['tipo_materia_prima'])
                
                return len(tipos_criados), MateriaPrima.objects.filter(tipo_materia_prima__isnull=False).count()
        except Exception as e:
            print(f"Erro ao migrar tipos de matéria-prima: {e}")
            return 0, 0

class TipoProduto(models.Model):
    nome = models.CharField('Nome', max_length=50)
    descricao = models.TextField('Descrição', blank=True)
    icone = models.CharField('Ícone', max_length=50, default='bi-box', blank=True, help_text='Nome do ícone Bootstrap, ex: bi-box')
    cor = models.CharField('Cor', max_length=20, default='primary', blank=True, help_text='Nome da cor Bootstrap: primary, success, etc')
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

class ConfiguracaoCustoMaoObra(models.Model):
    TIPO_CHOICES = [
        ('PLASTICO', 'Plástico'),
        ('MADEIRA', 'Madeira'),
        ('TECIDO', 'Tecido'),
        ('MISTO', 'Misto'),
    ]
    
    tipo_produto = models.CharField(
        'Tipo de Produto', 
        max_length=10, 
        choices=TIPO_CHOICES,
        unique=True
    )
    custo_mao_obra = models.DecimalField(
        'Custo da Mão de Obra', 
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text='Valor do custo da mão de obra por unidade produzida'
    )
    descricao = models.TextField('Descrição', blank=True, help_text='Informações adicionais sobre este custo')
    ultima_atualizacao = models.DateTimeField('Última Atualização', auto_now=True)
    
    class Meta:
        verbose_name = 'Configuração de Custo de Mão de Obra'
        verbose_name_plural = 'Configurações de Custo de Mão de Obra'
        ordering = ['tipo_produto']
    
    def __str__(self):
        return f"Custo de Mão de Obra - {self.get_tipo_produto_display()}"
    
    @classmethod
    def get_custo(cls, tipo_produto, valor_padrao=None):
        """
        Retorna o custo da mão de obra para um tipo de produto específico
        
        Args:
            tipo_produto: String representando o tipo de produto (PLASTICO, MADEIRA, etc)
            valor_padrao: Valor padrão caso não exista configuração para o tipo
            
        Returns:
            Decimal: Custo da mão de obra para o tipo de produto
        """
        try:
            config = cls.objects.get(tipo_produto=tipo_produto)
            return config.custo_mao_obra
        except cls.DoesNotExist:
            if valor_padrao is not None:
                return valor_padrao
            return 0.80  # Valor padrão caso não haja configuração
