# Este arquivo apenas exporta os serializers originais do módulo producao
# para manter a compatibilidade com a nova estrutura de organização

from ..serializers import (
    ProdutoSerializer,
    MateriaPrimaSerializer,
    OrdemProducaoSerializer
)

# Exportar explicitamente os serializers para manter controle sobre o que é exposto
__all__ = [
    'ProdutoSerializer',
    'MateriaPrimaSerializer',
    'OrdemProducaoSerializer'
]