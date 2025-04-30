# Importar views específicas de cada módulo
from .dashboard import DashboardView
from .saldos import SaldoEstoqueUpdateView, SaldoEstoqueDeleteView
from .materias_primas import MateriaPrimaCreateView, MateriaPrimaUpdateView, MateriaPrimaDeleteView
from .estoque_list import EstoqueListView