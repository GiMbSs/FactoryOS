from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages

class CustomLoginView(LoginView):
    """
    View personalizada para autenticação de usuários.
    Estende a LoginView padrão do Django, adicionando funcionalidades extras.
    """
    template_name = 'core/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """Retorna a URL para redirecionamento após login bem-sucedido."""
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('core:dashboard')
    
    def form_valid(self, form):
        """Processa o formulário válido e adiciona funcionalidade de 'lembrar-me'."""
        remember_me = self.request.POST.get('remember_me')
        if not remember_me:
            # Configurar a sessão para expirar quando o navegador for fechado
            self.request.session.set_expiry(0)
        
        return super().form_valid(form)

class CustomLogoutView(LogoutView):
    """
    View personalizada para logout de usuários.
    Implementação simplificada seguindo as diretrizes do Django.
    """
    # Usando reverse_lazy para uma resolução segura da URL
    next_page = reverse_lazy('core:login')

    # Não sobrescrevemos o método dispatch para garantir comportamento padrão