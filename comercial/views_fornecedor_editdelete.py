from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import UpdateView, DeleteView
from .models import Fornecedor
from .forms import FornecedorForm

class FornecedorUpdateView(UpdateView):
    model = Fornecedor
    form_class = FornecedorForm
    template_name = 'comercial/fornecedor_edit.html'
    success_url = reverse_lazy('comercial:lista_fornecedores')

    def form_valid(self, form):
        messages.success(self.request, 'Fornecedor atualizado com sucesso!')
        return super().form_valid(form)

class FornecedorDeleteView(DeleteView):
    model = Fornecedor
    template_name = 'comercial/fornecedor_delete.html'
    success_url = reverse_lazy('comercial:lista_fornecedores')
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Fornecedor excluído com sucesso!')
        return super().delete(request, *args, **kwargs)
