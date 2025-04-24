from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from core.views import registrar_log
from django.urls import reverse_lazy
from django.contrib import messages
from producao.models import MateriaPrima
from .models import SaldoEstoque, ProdutoEstoque
from .forms import SaldoEstoqueForm, MateriaPrimaForm

from producao.models import Produto

class EstoqueListView(TemplateView):
    template_name = 'estoque/estoque_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['materias_primas'] = MateriaPrima.objects.all()
        produtos = Produto.objects.all()
        produtos_com_estoque = []
        for produto in produtos:
            try:
                saldo = ProdutoEstoque.objects.get(produto=produto)
                quantidade = saldo.quantidade_atual
            except ProdutoEstoque.DoesNotExist:
                quantidade = 0
            produtos_com_estoque.append({
                'produto': produto,
                'quantidade_estoque': quantidade
            })
        context['produtos_acabados'] = produtos_com_estoque
        return context


class SaldoEstoqueUpdateView(UpdateView):
    model = SaldoEstoque
    form_class = SaldoEstoqueForm
    template_name = 'estoque/cadastro_material.html'
    success_url = reverse_lazy('estoque:estoque_list')

class SaldoEstoqueDeleteView(DeleteView):
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        response = super().delete(request, *args, **kwargs)
        registrar_log(request, 'Estoque', f'Excluiu saldo de material: {obj.materia_prima}')
        messages.success(self.request, 'Material excluído com sucesso!')
        return response
    model = SaldoEstoque
    template_name = 'estoque/confirmar_exclusao_material.html'
    success_url = reverse_lazy('estoque:estoque_list')

from django.views.generic.edit import CreateView, UpdateView, DeleteView

class MateriaPrimaCreateView(CreateView):
    model = MateriaPrima
    form_class = MateriaPrimaForm
    template_name = 'estoque/cadastro_materiaprima.html'
    success_url = reverse_lazy('estoque:estoque_list')

class MateriaPrimaUpdateView(UpdateView):
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
            from .models import SaldoEstoque
            saldo, _ = SaldoEstoque.objects.get_or_create(materia_prima=self.object)
            saldo.quantidade_atual = quantidade
            saldo.save()
        registrar_log(self.request, 'Estoque', f'Editou matéria-prima: {self.object.nome}')
        return response


class MateriaPrimaDeleteView(DeleteView):
    model = MateriaPrima
    template_name = 'estoque/confirmar_exclusao_materiaprima.html'
    success_url = reverse_lazy('estoque:estoque_list')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        response = super().delete(request, *args, **kwargs)
        registrar_log(request, 'Estoque', f'Excluiu matéria-prima: {obj.nome}')
        return response

class SaldoEstoqueDeleteView(DeleteView):
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        response = super().delete(request, *args, **kwargs)
        registrar_log(request, 'Estoque', f'Excluiu saldo de material: {obj.materia_prima}')
        return response
    model = SaldoEstoque
    template_name = 'estoque/confirmar_exclusao_material.html'
    success_url = reverse_lazy('estoque:estoque_list')

class DashboardView(TemplateView):
    template_name = 'estoque/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from producao.models import MateriaPrima
        context['materias_primas'] = MateriaPrima.objects.all()[:10]  # Limitar a 10 itens para demonstração
        return context
