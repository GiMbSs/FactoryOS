"""
Views para o módulo de produção.
Este arquivo agora serve como um redirecionamento para os módulos reorganizados,
mantendo compatibilidade com código existente.
"""
# Importar todas as views dos módulos reorganizados
from producao.views import *

# Logger para compatibilidade com código existente
import logging
logger = logging.getLogger(__name__)
