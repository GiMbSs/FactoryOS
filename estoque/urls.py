from django.urls import path
from .views import DashboardView, EstoqueListView, SaldoEstoqueUpdateView, SaldoEstoqueDeleteView, MateriaPrimaCreateView, MateriaPrimaUpdateView, MateriaPrimaDeleteView

app_name = 'estoque'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('estoque/', EstoqueListView.as_view(), name='estoque_list'),

    path('estoque/<int:pk>/editar/', SaldoEstoqueUpdateView.as_view(), name='material_edit'),
    path('estoque/<int:pk>/excluir/', SaldoEstoqueDeleteView.as_view(), name='material_delete'),
    path('materiaprima/nova/', MateriaPrimaCreateView.as_view(), name='materiaprima_create'),
    path('materiaprima/<int:pk>/editar/', MateriaPrimaUpdateView.as_view(), name='materiaprima_edit'),
    path('materiaprima/<int:pk>/excluir/', MateriaPrimaDeleteView.as_view(), name='materiaprima_delete'),
]
