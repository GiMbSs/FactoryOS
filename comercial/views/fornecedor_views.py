"""
Views para gerenciamento de fornecedores no sistema.
"""
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone

from core.views import registrar_log
from comercial.models import Fornecedor
from comercial.forms import FornecedorForm


class FornecedorListView(ListView):
    """
    View para listar fornecedores cadastrados no sistema.
    """
    model = Fornecedor
    template_name = 'comercial/fornecedor_list.html'
    context_object_name = 'fornecedores'
    paginate_by = 10
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from producao.models import MateriaPrima
        
        # Contar total de matérias-primas
        context['materias_primas_count'] = MateriaPrima.objects.count()
        
        # Contar novos fornecedores no mês atual
        context['novos_fornecedores_mes'] = Fornecedor.objects.filter(
            data_cadastro__month=timezone.now().month,
            data_cadastro__year=timezone.now().year
        ).count()
        
        return context


class FornecedorCreateView(CreateView):
    """
    View para criar novos fornecedores.
    """
    model = Fornecedor
    form_class = FornecedorForm
    template_name = 'comercial/cadastro_fornecedor.html'
    success_url = reverse_lazy('comercial:lista_fornecedores')

    def form_valid(self, form):
        response = super().form_valid(form)
        registrar_log(self.request, 'Comercial', f'Cadastrou fornecedor: {self.object.nome}')
        return response


class FornecedorUpdateView(UpdateView):
    """
    View para atualizar dados de fornecedores existentes.
    """
    model = Fornecedor
    form_class = FornecedorForm
    template_name = 'comercial/cadastro_fornecedor.html'
    success_url = reverse_lazy('comercial:lista_fornecedores')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        registrar_log(self.request, 'Comercial', f'Editou fornecedor: {self.object.nome}')
        return response


class FornecedorDeleteView(DeleteView):
    """
    View para excluir fornecedores.
    """
    model = Fornecedor
    template_name = 'comercial/confirmar_exclusao_fornecedor.html'
    success_url = reverse_lazy('comercial:lista_fornecedores')
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        response = super().delete(request, *args, **kwargs)
        registrar_log(request, 'Comercial', f'Excluiu fornecedor: {obj.nome}')
        return response