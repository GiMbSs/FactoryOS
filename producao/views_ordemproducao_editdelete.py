from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import UpdateView, DeleteView
from .models import OrdemProducao
from .forms import OrdemProducaoForm

class OrdemProducaoUpdateView(UpdateView):
    model = OrdemProducao
    form_class = OrdemProducaoForm
    template_name = 'producao/ordemproducao_edit.html'
    success_url = reverse_lazy('producao:lista_ordens')

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'Ordem de produção atualizada com sucesso!')
            return response
        except Exception as e:
            from django.core.exceptions import ValidationError
            if isinstance(e, ValidationError):
                for msg in e.messages:
                    messages.error(self.request, msg)
                return self.form_invalid(form)
            raise

    def form_invalid(self, form):
        # Garante que mensagens de erro do Django messages framework apareçam
        messages.error(self.request, 'Erro ao atualizar a ordem de produção. Verifique os dados informados.')
        return super().form_invalid(form)

class OrdemProducaoDeleteView(DeleteView):
    model = OrdemProducao
    template_name = 'producao/ordemproducao_delete.html'
    success_url = reverse_lazy('producao:lista_ordens')
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Ordem de produção excluída com sucesso!')
        return super().delete(request, *args, **kwargs)
