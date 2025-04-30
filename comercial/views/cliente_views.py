"""
Views para gerenciamento de clientes no sistema.
"""
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages

from core.views import registrar_log
from comercial.models import Cliente
from comercial.forms import ClienteForm


class ClienteListView(ListView):
    """
    View para listar clientes cadastrados no sistema.
    """
    model = Cliente
    template_name = 'comercial/cliente_list.html'
    context_object_name = 'clientes'
    paginate_by = 10
    ordering = ['nome']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adicionar contagem de clientes ativos
        context['clientes_ativos'] = Cliente.objects.filter(ativo=True).count()
        # Adicionar outras estatísticas úteis
        # Contar total de vendas (usando o nome do relacionamento reverso correto)
        from comercial.models import Venda
        context['total_vendas'] = Venda.objects.count()
        # Contar novos clientes do mês atual
        context['novos_clientes_mes'] = Cliente.objects.filter(
            data_cadastro__month=timezone.now().month,
            data_cadastro__year=timezone.now().year
        ).count()
        return context


class ClienteCreateView(CreateView):
    """
    View para criar novos clientes.
    """
    model = Cliente
    form_class = ClienteForm
    template_name = 'comercial/cadastro_cliente.html'
    success_url = reverse_lazy('comercial:lista_clientes')

    def form_valid(self, form):
        response = super().form_valid(form)
        registrar_log(self.request, 'Comercial', f'Cadastrou cliente: {self.object.nome}')
        return response


class ClienteUpdateView(UpdateView):
    """
    View para atualizar dados de clientes existentes.
    """
    model = Cliente
    form_class = ClienteForm
    template_name = 'comercial/cadastro_cliente.html'
    success_url = reverse_lazy('comercial:lista_clientes')

    def form_valid(self, form):
        response = super().form_valid(form)
        registrar_log(self.request, 'Comercial', f'Editou cliente: {self.object.nome}')
        return response


class ClienteDeleteView(DeleteView):
    """
    View para excluir clientes.
    """
    model = Cliente
    template_name = 'comercial/confirmar_exclusao_cliente.html'
    success_url = reverse_lazy('comercial:lista_clientes')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        response = super().delete(request, *args, **kwargs)
        registrar_log(request, 'Comercial', f'Excluiu cliente: {obj.nome}')
        return response


class ToggleClienteView(View):
    """
    View para ativar/desativar clientes.
    """
    def post(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk)
        cliente.ativo = not cliente.ativo
        cliente.save()
        return redirect('comercial:lista_clientes')