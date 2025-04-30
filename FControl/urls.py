"""
Configuração de URLs do projeto Coffee Filter Factory.
Este arquivo define os caminhos principais da aplicação e direciona 
para as diferentes áreas do sistema.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views.dashboard import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='index'),
    path('producao/', include('producao.urls')),
    path('estoque/', include('estoque.urls')),
    path('comercial/', include('comercial.urls')),
    path('financeiro/', include('financeiro.urls')),
    path('core/', include('core.urls')),
]

# Serve arquivos estáticos em modo de desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
