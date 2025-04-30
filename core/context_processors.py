from django.conf import settings

def system_settings(request):
    """
    Adiciona variáveis de configuração do sistema ao contexto dos templates.
    """
    return {
        'system_title': settings.SYSTEM_TITLE,
    }