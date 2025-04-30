"""
Views para gerenciar saldos de estoque.
"""
from django.views.generic import UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages

from core.views import registrar_log
from estoque.models import SaldoEstoque
from estoque.forms import SaldoEstoqueForm


class SaldoEstoqueUpdateView(UpdateView):
    """
    View para atualizar saldos de estoque de materiais.
    """
    model = SaldoEstoque
    form_class = SaldoEstoqueForm
    template_name = 'estoque/cadastro_material.html'
    success_url = reverse_lazy('estoque:estoque_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        registrar_log(self.request, 'Estoque', f'Atualizou saldo de material: {self.object.materia_prima}')
        messages.success(self.request, f'Saldo de {self.object.materia_prima.nome} atualizado com sucesso!')
        return response


class SaldoEstoqueDeleteView(DeleteView):
    """
    View para excluir saldos de estoque de materiais.
    """
    model = SaldoEstoque
    template_name = 'estoque/confirmar_exclusao_material.html'
    success_url = reverse_lazy('estoque:estoque_list')
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        response = super().delete(request, *args, **kwargs)
        registrar_log(request, 'Estoque', f'Excluiu saldo de material: {obj.materia_prima}')
        messages.success(self.request, f'Saldo de {obj.materia_prima.nome} excluído com sucesso!')
        return response