from django.shortcuts import render

from django.views.generic import ListView
from .models import LogEntry

from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.shortcuts import redirect

class LogListView(ListView):
    template_name = 'core/log_list.html'
    model = LogEntry
    context_object_name = 'logs'
    ordering = ['-data']


def registrar_log(request, modulo, acao):
    from .models import LogEntry
    LogEntry.objects.create(
        modulo=modulo,
        acao=acao,
        usuario=request.user if hasattr(request, 'user') and request.user.is_authenticated else None
    )

@user_passes_test(lambda u: u.is_superuser)
def limpar_log(request):
    LogEntry.objects.all().delete()
    return redirect('core:log_list')
