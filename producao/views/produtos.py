from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from rest_framework import viewsets

from core.views import LoggingMixin
from ..models import Produto, TipoProduto
from ..forms import ProdutoForm, TipoProdutoForm, ProdutoMateriaPrimaFormSet
from ..serializers import ProdutoSerializer

import logging
logger = logging.getLogger(__name__)


class ProdutoViewSet(viewsets.ModelViewSet):
    """API REST para gerenciamento de produtos"""
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer


class ProdutoListView(LoginRequiredMixin, ListView):
    """
    Exibe a listagem de produtos cadastrados com estatísticas por tipo.
    """
    model = Produto
    template_name = 'producao/produto_list.html'
    context_object_name = 'produtos'
    ordering = ['nome']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        from ..services import EstatisticasService
        estatisticas = EstatisticasService.obter_estatisticas_produto()
        
        context['total_produtos'] = estatisticas['total_produtos']
        context['produtos_madeira'] = estatisticas['produtos_por_tipo']['madeira']
        context['produtos_plastico'] = estatisticas['produtos_por_tipo']['plastico']
        context['produtos_tecido'] = estatisticas['produtos_por_tipo']['tecido']
        context['produtos_misto'] = estatisticas['produtos_por_tipo']['misto']
        context['custo_medio'] = estatisticas['custo_medio']
            
        return context


class ProdutoCreateView(LoginRequiredMixin, LoggingMixin, CreateView):
    """
    Criação de produtos com suas matérias-primas associadas.
    """
    model = Produto
    form_class = ProdutoForm
    template_name = 'producao/cadastro_produto.html'
    success_url = reverse_lazy('producao:produto_list')
    
    log_module = 'Produção'
    log_create_message = "Cadastrou novo produto: {}"
    success_message = "Produto cadastrado com sucesso!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['materias_formset'] = ProdutoMateriaPrimaFormSet(self.request.POST)
        else:
            context['materias_formset'] = ProdutoMateriaPrimaFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        materias_formset = context['materias_formset']
        if materias_formset.is_valid():
            self.object = form.save()
            materias_formset.instance = self.object
            materias_formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class ProdutoUpdateView(LoginRequiredMixin, LoggingMixin, UpdateView):
    """
    Edição de produtos e suas matérias-primas associadas.
    """
    model = Produto
    form_class = ProdutoForm
    template_name = 'producao/cadastro_produto.html'
    success_url = reverse_lazy('producao:produto_list')
    
    log_module = 'Produção'
    log_update_message = "Editou produto: {}"
    success_message = "Produto atualizado com sucesso!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['materias_formset'] = ProdutoMateriaPrimaFormSet(self.request.POST, instance=self.object)
        else:
            context['materias_formset'] = ProdutoMateriaPrimaFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        materias_formset = context['materias_formset']
        if materias_formset.is_valid():
            self.object = form.save()
            materias_formset.instance = self.object
            materias_formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class ProdutoDeleteView(LoginRequiredMixin, LoggingMixin, DeleteView):
    """
    Exclusão de produtos.
    """
    model = Produto
    template_name = 'producao/confirmar_exclusao_produto.html'
    success_url = reverse_lazy('producao:produto_list')
    
    log_module = 'Produção'
    log_delete_message = "Excluiu produto: {}"
    success_message = "Produto excluído com sucesso!"


@login_required
@require_http_methods(["GET", "POST"])
def tipo_produto_modal(request):
    """
    Gerencia tipos de produto em uma janela modal.
    """
    tipo_id = request.GET.get('id')
    
    if tipo_id:
        tipo = TipoProduto.objects.get(id=tipo_id)
        title = f"Editar Tipo: {tipo.nome}"
    else:
        tipo = None
        title = "Novo Tipo de Produto"
    
    if request.method == "POST":
        form = TipoProdutoForm(request.POST, instance=tipo)
        if form.is_valid():
            tipo = form.save()
            return JsonResponse({
                'success': True,
                'id': tipo.id,
                'nome': tipo.nome,
                'message': f"Tipo de produto '{tipo.nome}' salvo com sucesso."
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors.as_json()
            })
    else:
        form = TipoProdutoForm(instance=tipo)
    
    html = render_to_string('producao/includes/tipo_produto_modal.html', {
        'form': form,
        'tipo': tipo,
        'title': title
    }, request=request)
    
    return JsonResponse({
        'html': html,
        'title': title
    })