from django.urls import path, include
from rest_framework import routers
from .views import MateriaPrimaViewSet, ProdutoViewSet, OrdemProducaoViewSet, ProdutoMateriasPrimasAPIView

# API Router
router = routers.DefaultRouter()
router.register(r'materias-primas', MateriaPrimaViewSet)
router.register(r'produtos', ProdutoViewSet)
router.register(r'ordens', OrdemProducaoViewSet)

urlpatterns = [
    # API
    path('', include(router.urls)),
    path('produtos/<int:produto_id>/materias-primas/', ProdutoMateriasPrimasAPIView.as_view(), name='api_produto_materias_primas'),
]