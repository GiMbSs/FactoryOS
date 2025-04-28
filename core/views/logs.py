from django.views.generic import ListView
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone

from core.models import LogEntry

class LogListView(ListView):
    template_name = 'core/log_list.html'
    model = LogEntry
    context_object_name = 'logs'
    ordering = ['-data']


def registrar_log(request, modulo, descricao):
    """
    Registra ações realizadas por usuários no sistema.
    Cada log contém informações sobre qual usuário fez o quê e em qual módulo.
    """
    if request.user.is_authenticated:
        LogEntry.objects.create(
            usuario=request.user,
            modulo=modulo,
            acao=descricao
        )

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class LoggingMixin:
    """
    Automatiza o registro de logs para operações de criação, edição e exclusão.
    
    Como usar este mixin:
    1. Adicione-o como herança na sua classe de view
    2. Defina log_module com o nome do módulo (ex: 'Produção')
    3. Personalize as mensagens de log se necessário
    """
    log_module = None  # Nome do módulo que a view pertence
    log_create_message = "Cadastrou {}"
    log_update_message = "Editou {}"
    log_delete_message = "Excluiu {}"
    success_message = None  # Mensagem de sucesso mostrada ao usuário
    
    def get_log_object_name(self):
        """Obtém um nome descritivo do objeto para usar nos logs"""
        if hasattr(self, 'object') and self.object:
            if hasattr(self.object, 'nome'):
                return f"{self.object.nome}"
            return str(self.object)
        return "objeto"
    
    def form_valid(self, form):
        """Processa o formulário e registra o log da ação"""
        response = super().form_valid(form)
        
        if hasattr(self, 'object') and self.object:
            if self.object.pk and hasattr(self, 'log_update_message'):
                message = self.log_update_message.format(self.get_log_object_name())
            else:
                message = self.log_create_message.format(self.get_log_object_name())
                
            registrar_log(self.request, self.log_module, message)
            
            if self.success_message:
                messages.success(self.request, self.success_message)
                
        return response
    
    def delete(self, request, *args, **kwargs):
        """Exclui o objeto e registra a ação no log"""
        obj_name = self.get_log_object_name()
        response = super().delete(request, *args, **kwargs)
        
        message = self.log_delete_message.format(obj_name)
        registrar_log(request, self.log_module, message)
        
        if self.success_message:
            messages.success(request, self.success_message)
            
        return response

@user_passes_test(lambda u: u.is_superuser)
def limpar_log(request):
    """Apaga todos os logs do sistema (somente superusuários)"""
    LogEntry.objects.all().delete()
    return redirect('core:log_list')