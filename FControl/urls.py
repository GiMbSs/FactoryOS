"""
Configuração de URLs do projeto FControl.
Este arquivo define os caminhos principais da aplicação e direciona 
para as diferentes áreas do sistema.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from core.views.dashboard import HomeView
from django.shortcuts import redirect

# Redirecionamento para a página principal quando o usuário acessa a raiz
def redirect_to_home(request):
    return redirect('core:login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_home, name='index'),
    path('home/', login_required(HomeView.as_view()), name='home'),
    path('producao/', include('producao.urls')),
    path('estoque/', include('estoque.urls')),
    path('comercial/', include('comercial.urls')),
    path('financeiro/', include('financeiro.urls')),
    path('core/', include('core.urls')),
]

# Serve arquivos estáticos em modo de desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Configurações do site admin
admin.site.site_header = 'FControl - Administração'
admin.site.site_title = 'FControl Admin'
admin.site.index_title = 'Painel de Administração'
