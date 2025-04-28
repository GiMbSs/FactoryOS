from django.urls import path, include
from . import views
from .views.ordens import OrdemProducaoUpdateView, OrdemProducaoDeleteView

app_name = 'producao'

urlpatterns = [
    # API - agora usa o módulo API reorganizado
    path('api/', include('producao.api.urls')),
    
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Produtos
    path('produtos/', views.ProdutoListView.as_view(), name='produto_list'),
    path('produtos/novo/', views.ProdutoCreateView.as_view(), name='produto_create'),
    path('produtos/<int:pk>/editar/', views.ProdutoUpdateView.as_view(), name='produto_update'),
    path('produtos/<int:pk>/excluir/', views.ProdutoDeleteView.as_view(), name='produto_delete'),
    
    # Tipos de Produto (Modal)
    path('produtos/tipos/modal/', views.tipo_produto_modal, name='tipo_produto_modal'),
    
    # Matérias-Primas
    path('materias-primas/', views.MateriaPrimaListView.as_view(), name='materiaprima_list'),
    path('materias-primas/nova/', views.MateriaPrimaCreateView.as_view(), name='materiaprima_create'),
    path('materias-primas/<int:pk>/editar/', views.MateriaPrimaUpdateView.as_view(), name='materiaprima_update'),
    path('materias-primas/<int:pk>/excluir/', views.MateriaPrimaDeleteView.as_view(), name='materiaprima_delete'),
    
    # API para obter informações da matéria-prima
    path('materias-primas/<int:materia_prima_id>/info/', views.get_materia_prima_info, name='get_materia_prima_info'),
    
    # Ordens de Produção
    path('ordens/', views.OrdemProducaoListView.as_view(), name='lista_ordens'),
    path('ordens/nova/', views.OrdemProducaoCreateView.as_view(), name='nova_ordem'),
    path('ordens/<int:pk>/', views.OrdemProducaoDetailView.as_view(), name='ordem_detail'),
    path('ordens/<int:pk>/editar/', OrdemProducaoUpdateView.as_view(), name='ordem_edit'),
    path('ordens/<int:pk>/excluir/', OrdemProducaoDeleteView.as_view(), name='ordem_delete'),
]
