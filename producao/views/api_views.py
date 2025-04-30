"""
Views para a API REST do módulo de produção.
"""
from rest_framework import viewsets

from producao.models import MateriaPrima, Produto, OrdemProducao
from producao.serializers import (
    MateriaPrimaSerializer,
    ProdutoSerializer,
    OrdemProducaoSerializer
)


class MateriaPrimaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para visualizar e editar matérias-primas.
    """
    queryset = MateriaPrima.objects.all()
    serializer_class = MateriaPrimaSerializer


class ProdutoViewSet(viewsets.ModelViewSet):
    """
    API endpoint para visualizar e editar produtos.
    """
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer


class OrdemProducaoViewSet(viewsets.ModelViewSet):
    """
    API endpoint para visualizar e editar ordens de produção.
    """
    queryset = OrdemProducao.objects.all()
    serializer_class = OrdemProducaoSerializer