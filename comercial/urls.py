from django.urls import path
from .views import DashboardView, ClienteListView, ClienteCreateView, ClienteUpdateView, VendaCreateView, VendaUpdateView, VendaListView, VendaDeleteView, FornecedorListView, FornecedorCreateView, ToggleClienteView, VendaUpdateStatusView

app_name = 'comercial'

urlpatterns = [
    path('fornecedores/', FornecedorListView.as_view(), name='lista_fornecedores'),
    path('fornecedores/novo/', FornecedorCreateView.as_view(), name='cadastro_fornecedor'),
    path('fornecedores/<int:pk>/editar/', __import__('comercial.views_fornecedor_editdelete').views_fornecedor_editdelete.FornecedorUpdateView.as_view(), name='editar_fornecedor'),
    path('fornecedores/<int:pk>/excluir/', __import__('comercial.views_fornecedor_editdelete').views_fornecedor_editdelete.FornecedorDeleteView.as_view(), name='excluir_fornecedor'),
    path('', DashboardView.as_view(), name='dashboard'),
    path('clientes/', ClienteListView.as_view(), name='lista_clientes'),
    path('clientes/<int:pk>/editar/', ClienteUpdateView.as_view(), name='editar_cliente'),
    path('clientes/<int:pk>/excluir/', __import__('comercial.views_cliente_delete').views_cliente_delete.ClienteDeleteView.as_view(), name='excluir_cliente'),
    path('clientes/<int:pk>/toggle/', ToggleClienteView.as_view(), name='toggle_cliente'),
    path('clientes/novo/', ClienteCreateView.as_view(), name='cadastro_cliente'),
    path('pedidos/', VendaListView.as_view(), name='pedido_list'),
    path('pedidos/novo/', VendaCreateView.as_view(), name='pedido_create'),
    path('pedidos/<int:pk>/editar/', VendaUpdateView.as_view(), name='pedido_edit'),
    path('pedidos/<int:pk>/excluir/', VendaDeleteView.as_view(), name='pedido_delete'),
    path('pedidos/<int:pk>/update-status/', VendaUpdateStatusView.as_view(), name='pedido_update_status'),
]
