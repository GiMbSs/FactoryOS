from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import DeleteView
from .models import Cliente

class ClienteDeleteView(DeleteView):
    model = Cliente
    template_name = 'comercial/cliente_delete.html'
    success_url = reverse_lazy('comercial:lista_clientes')
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Cliente excluído com sucesso!')
        return super().delete(request, *args, **kwargs)
