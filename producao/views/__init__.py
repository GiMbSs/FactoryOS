# Importar views específicas de cada módulo
from .produtos import *
from .materias_primas import *
from .ordens import *
from .dashboard import DashboardView
from .home import HomeView
from .auxiliar import (
    tipo_produto_modal,
    tipo_materia_prima_modal,
    get_materia_prima_info,
)
from .api_views import (
    MateriaPrimaViewSet,
    ProdutoViewSet,
    OrdemProducaoViewSet,
)