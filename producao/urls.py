from django.urls import path, include

from producao.views.dashboard import DashboardView
from producao.views.produtos import (
    ProdutoListView, 
    ProdutoCreateView, 
    ProdutoUpdateView, 
    ProdutoDeleteView
)
from producao.views.materias_primas import (
    MateriaPrimaListView, 
    MateriaPrimaCreateView, 
    MateriaPrimaUpdateView, 
    MateriaPrimaDeleteView
)
from producao.views.ordens import (
    OrdemProducaoListView,
    OrdemProducaoCreateView,
    OrdemProducaoDetailView,
    OrdemProducaoUpdateView,
    OrdemProducaoDeleteView
)
from producao.views.auxiliar import (
    tipo_produto_modal,
    tipo_materia_prima_modal,
    get_materia_prima_info
)

app_name = 'producao'

urlpatterns = [
    # API - agora usa o módulo API reorganizado
    path('api/', include('producao.api.urls')),
    
    # Dashboard
    path('', DashboardView.as_view(), name='dashboard'),
    
    # Produtos
    path('produtos/', ProdutoListView.as_view(), name='produto_list'),
    path('produtos/novo/', ProdutoCreateView.as_view(), name='produto_create'),
    path('produtos/<int:pk>/editar/', ProdutoUpdateView.as_view(), name='produto_update'),
    path('produtos/<int:pk>/excluir/', ProdutoDeleteView.as_view(), name='produto_delete'),
    
    # Tipos de Produto (Modal)
    path('produtos/tipos/modal/', tipo_produto_modal, name='tipo_produto_modal'),
    
    # Matérias-Primas
    path('materias-primas/', MateriaPrimaListView.as_view(), name='materiaprima_list'),
    path('materias-primas/nova/', MateriaPrimaCreateView.as_view(), name='materiaprima_create'),
    path('materias-primas/<int:pk>/editar/', MateriaPrimaUpdateView.as_view(), name='materiaprima_update'),
    path('materias-primas/<int:pk>/excluir/', MateriaPrimaDeleteView.as_view(), name='materiaprima_delete'),
    
    # Tipos de Matéria Prima (Modal)
    path('materias-primas/tipos/modal/', tipo_materia_prima_modal, name='tipo_materia_prima_modal'),
    
    # API para obter informações da matéria-prima
    path('materias-primas/<int:materia_prima_id>/info/', get_materia_prima_info, name='get_materia_prima_info'),
    
    # Ordens de Produção
    path('ordens/', OrdemProducaoListView.as_view(), name='lista_ordens'),
    path('ordens/nova/', OrdemProducaoCreateView.as_view(), name='nova_ordem'),
    path('ordens/<int:pk>/', OrdemProducaoDetailView.as_view(), name='ordem_detail'),
    path('ordens/<int:pk>/editar/', OrdemProducaoUpdateView.as_view(), name='ordem_edit'),
    path('ordens/<int:pk>/excluir/', OrdemProducaoDeleteView.as_view(), name='ordem_delete'),
]
