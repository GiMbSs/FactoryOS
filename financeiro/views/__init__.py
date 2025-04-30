# Importar views específicas de cada módulo
from .dashboard import DashboardView
from .contas_pagar import (
    ContaPagarListView,
    ContaPagarCreateView,
    ContaPagarUpdateView,
    ContaPagarDeleteView,
    RegistrarPagamentoView
)
from .contas_receber import (
    ContaReceberListView,
    ContaReceberCreateView,
    ContaReceberUpdateView,
    ContaReceberDeleteView,
    RegistrarRecebimentoView
)