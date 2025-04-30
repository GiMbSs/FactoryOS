"""
Views para gerenciar matérias-primas no estoque.
"""
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect

from core.views import registrar_log
from producao.models import MateriaPrima, ProdutoMateriaPrima
from estoque.models import SaldoEstoque, MovimentacaoEstoque
from estoque.forms import MateriaPrimaForm


class MateriaPrimaCreateView(CreateView):
    """
    View para criar novas matérias-primas.
    """
    model = MateriaPrima
    form_class = MateriaPrimaForm
    template_name = 'estoque/cadastro_materiaprima.html'
    success_url = reverse_lazy('estoque:estoque_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        quantidade = form.cleaned_data.get('quantidade_estoque')
        
        if quantidade is not None and quantidade > 0:
            saldo, created = SaldoEstoque.objects.get_or_create(materia_prima=self.object)
            saldo.quantidade_atual = quantidade
            saldo.save()
            
        registrar_log(self.request, 'Estoque', f'Cadastrou matéria-prima: {self.object.nome}')
        messages.success(self.request, f'Matéria-prima "{self.object.nome}" cadastrada com sucesso!')
        return response


class MateriaPrimaUpdateView(UpdateView):
    """
    View para atualizar matérias-primas.
    """
    model = MateriaPrima
    form_class = MateriaPrimaForm
    template_name = 'estoque/cadastro_materiaprima.html'
    success_url = reverse_lazy('estoque:estoque_list')

    def get_initial(self):
        initial = super().get_initial()
        try:
            saldo = self.object.saldoestoque
            initial['quantidade_estoque'] = saldo.quantidade_atual
        except Exception:
            initial['quantidade_estoque'] = 0
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        quantidade = form.cleaned_data.get('quantidade_estoque')
        
        if quantidade is not None:
            saldo, created = SaldoEstoque.objects.get_or_create(materia_prima=self.object)
            saldo.quantidade_atual = quantidade
            saldo.save()
            
        registrar_log(self.request, 'Estoque', f'Editou matéria-prima: {self.object.nome}')
        messages.success(self.request, f'Matéria-prima "{self.object.nome}" atualizada com sucesso!')
        return response


class MateriaPrimaDeleteView(DeleteView):
    """
    View para excluir matérias-primas.
    """
    model = MateriaPrima
    template_name = 'estoque/confirmar_exclusao_materiaprima.html'
    success_url = reverse_lazy('estoque:estoque_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        materia_prima = self.get_object()
        
        produtos_usando = ProdutoMateriaPrima.objects.filter(materia_prima=materia_prima)
        context['produtos_usando'] = produtos_usando
        
        movimentacoes = MovimentacaoEstoque.objects.filter(materia_prima=materia_prima).count()
        context['movimentacoes'] = movimentacoes
        
        return context

    def post(self, request, *args, **kwargs):
        materia_prima = self.get_object()
        
        produtos_usando = ProdutoMateriaPrima.objects.filter(materia_prima=materia_prima).exists()
        
        if produtos_usando:
            messages.error(request, f'Não é possível excluir a matéria-prima "{materia_prima.nome}" pois ela está sendo usada em produtos.')
            return redirect('estoque:estoque_list')
        
        movimentacoes = MovimentacaoEstoque.objects.filter(materia_prima=materia_prima).exists()
        
        if movimentacoes:
            messages.error(request, f'Não é possível excluir a matéria-prima "{materia_prima.nome}" pois existem movimentações de estoque registradas.')
            return redirect('estoque:estoque_list')
        
        # Armazenar o nome da matéria-prima antes de excluí-la
        nome_materia = materia_prima.nome
        
        # Remover qualquer saldo associado à matéria-prima
        try:
            saldo = SaldoEstoque.objects.get(materia_prima=materia_prima)
            saldo.delete()
        except SaldoEstoque.DoesNotExist:
            pass
        
        # Excluir a matéria-prima
        materia_prima.delete()
        
        # Registrar no log e adicionar mensagem de sucesso
        registrar_log(request, 'Estoque', f'Excluiu matéria-prima: {nome_materia}')
        messages.success(request, f'Matéria-prima "{nome_materia}" excluída com sucesso!')
        
        return redirect('estoque:estoque_list')
    
    # Sobreescrever o método delete para evitar que seja chamado
    def delete(self, request, *args, **kwargs):
        # Este método não será chamado pois o post acima realiza toda a lógica necessária
        pass