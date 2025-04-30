from django.urls import path

from estoque.views.dashboard import DashboardView
from estoque.views.estoque_list import EstoqueListView
from estoque.views.saldos import SaldoEstoqueUpdateView, SaldoEstoqueDeleteView
from estoque.views.materias_primas import (
    MateriaPrimaCreateView,
    MateriaPrimaUpdateView,
    MateriaPrimaDeleteView
)
from estoque.views.movimentacoes import (
    MovimentacaoCreateView,
    MovimentacaoListView
)

app_name = 'estoque'

urlpatterns = [
    # Dashboard
    path('', DashboardView.as_view(), name='dashboard'),
    
    # Estoque
    path('estoque/', EstoqueListView.as_view(), name='estoque_list'),
    path('estoque/<int:pk>/editar/', SaldoEstoqueUpdateView.as_view(), name='material_edit'),
    path('estoque/<int:pk>/excluir/', SaldoEstoqueDeleteView.as_view(), name='material_delete'),
    
    # Matérias-primas
    path('materiaprima/nova/', MateriaPrimaCreateView.as_view(), name='materiaprima_create'),
    path('materiaprima/<int:pk>/editar/', MateriaPrimaUpdateView.as_view(), name='materiaprima_edit'),
    path('materiaprima/<int:pk>/excluir/', MateriaPrimaDeleteView.as_view(), name='materiaprima_delete'),
    
    # Movimentações de estoque
    path('movimentacoes/', MovimentacaoListView.as_view(), name='movimentacoes_list'),
    path('movimentacoes/nova/', MovimentacaoCreateView.as_view(), name='movimentacao_create'),
]
