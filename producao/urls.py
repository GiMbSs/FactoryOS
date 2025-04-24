from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DashboardView,
    OrdemProducaoListView,
    OrdemProducaoCreateView,
    OrdemProducaoDetailView,
    MateriaPrimaViewSet,
    ProdutoViewSet,
    OrdemProducaoViewSet,
    ProdutoListView,
    ProdutoCreateView,
    ProdutoUpdateView,
    ProdutoDeleteView,
    MateriaPrimaListView,
    MateriaPrimaCreateView,
    MateriaPrimaUpdateView,
    MateriaPrimaDeleteView
)
from .views_api import ProdutoMateriasPrimasAPIView

app_name = 'producao'

router = DefaultRouter()
router.register(r'api/materias-primas', MateriaPrimaViewSet)
router.register(r'api/produtos', ProdutoViewSet)
router.register(r'api/ordens-producao', OrdemProducaoViewSet)

urlpatterns = [
    path('api/produtos/<int:produto_id>/materias-primas/', ProdutoMateriasPrimasAPIView.as_view(), name='api_produto_materias_primas'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('ordens/', OrdemProducaoListView.as_view(), name='lista_ordens'),
    path('ordens/nova/', OrdemProducaoCreateView.as_view(), name='ordem_create'),
    path('ordens/<int:pk>/', OrdemProducaoDetailView.as_view(), name='ordem_detail'),
    path('ordens/<int:pk>/editar/', __import__('producao.views_ordemproducao_editdelete').views_ordemproducao_editdelete.OrdemProducaoUpdateView.as_view(), name='ordem_edit'),
    path('ordens/<int:pk>/excluir/', __import__('producao.views_ordemproducao_editdelete').views_ordemproducao_editdelete.OrdemProducaoDeleteView.as_view(), name='ordem_delete'),

    path('produtos/', ProdutoListView.as_view(), name='produto_list'),
    path('produtos/novo/', ProdutoCreateView.as_view(), name='produto_create'),
    path('produtos/<int:pk>/editar/', ProdutoUpdateView.as_view(), name='produto_edit'),
    path('produtos/<int:pk>/excluir/', ProdutoDeleteView.as_view(), name='produto_delete'),

    path('materias-primas/', MateriaPrimaListView.as_view(), name='materiaprima_list'),
    path('materias-primas/nova/', MateriaPrimaCreateView.as_view(), name='materiaprima_create'),
    path('materias-primas/<int:pk>/editar/', MateriaPrimaUpdateView.as_view(), name='materiaprima_edit'),
    path('materias-primas/<int:pk>/excluir/', MateriaPrimaDeleteView.as_view(), name='materiaprima_delete'),

    path('api/', include(router.urls)),
]
