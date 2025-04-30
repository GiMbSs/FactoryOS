from django.urls import path
from comercial.views.dashboard import DashboardView
from comercial.views.cliente_views import (
    ClienteListView, 
    ClienteCreateView, 
    ClienteUpdateView, 
    ClienteDeleteView, 
    ToggleClienteView
)
from comercial.views.fornecedor_views import (
    FornecedorListView, 
    FornecedorCreateView,
    FornecedorUpdateView,
    FornecedorDeleteView
)
from comercial.views.venda_views import (
    VendaListView,
    VendaCreateView,
    VendaUpdateView,
    VendaDeleteView,
    VendaUpdateStatusView
)

app_name = 'comercial'

urlpatterns = [
    # Dashboard
    path('', DashboardView.as_view(), name='dashboard'),
    
    # Fornecedores
    path('fornecedores/', FornecedorListView.as_view(), name='lista_fornecedores'),
    path('fornecedores/novo/', FornecedorCreateView.as_view(), name='cadastro_fornecedor'),
    path('fornecedores/<int:pk>/editar/', FornecedorUpdateView.as_view(), name='editar_fornecedor'),
    path('fornecedores/<int:pk>/excluir/', FornecedorDeleteView.as_view(), name='excluir_fornecedor'),
    
    # Clientes
    path('clientes/', ClienteListView.as_view(), name='lista_clientes'),
    path('clientes/novo/', ClienteCreateView.as_view(), name='cadastro_cliente'),
    path('clientes/<int:pk>/editar/', ClienteUpdateView.as_view(), name='editar_cliente'),
    path('clientes/<int:pk>/excluir/', ClienteDeleteView.as_view(), name='excluir_cliente'),
    path('clientes/<int:pk>/toggle/', ToggleClienteView.as_view(), name='toggle_cliente'),
    
    # Pedidos/Vendas
    path('pedidos/', VendaListView.as_view(), name='pedido_list'),
    path('pedidos/novo/', VendaCreateView.as_view(), name='pedido_create'),
    path('pedidos/<int:pk>/editar/', VendaUpdateView.as_view(), name='pedido_edit'),
    path('pedidos/<int:pk>/excluir/', VendaDeleteView.as_view(), name='pedido_delete'),
    path('pedidos/<int:pk>/update-status/', VendaUpdateStatusView.as_view(), name='pedido_update_status'),
]
