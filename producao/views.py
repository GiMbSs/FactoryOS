from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from core.views import registrar_log
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from rest_framework import viewsets
from .models import OrdemProducao, Produto, MateriaPrima
from .forms import OrdemProducaoForm, ProdutoForm, MateriaPrimaForm
from .serializers import (
    ProdutoSerializer,
    MateriaPrimaSerializer,
    OrdemProducaoSerializer
)
import logging
from datetime import datetime, timedelta

class MateriaPrimaViewSet(viewsets.ModelViewSet):
    queryset = MateriaPrima.objects.all()
    serializer_class = MateriaPrimaSerializer

class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer

class OrdemProducaoViewSet(viewsets.ModelViewSet):
    queryset = OrdemProducao.objects.all()
    serializer_class = OrdemProducaoSerializer

logger = logging.getLogger(__name__)

from django.contrib.auth.mixins import LoginRequiredMixin

class ProdutoListView(LoginRequiredMixin, ListView):
    model = Produto
    template_name = 'producao/produto_list.html'
    context_object_name = 'produtos'
    ordering = ['nome']

class ProdutoCreateView(LoginRequiredMixin, CreateView):
    def form_valid(self, form):
        response = super().form_valid(form)
        registrar_log(self.request, 'Produção', f'Cadastrou novo produto: {self.object.nome}')
        return response
    model = Produto
    form_class = ProdutoForm
    template_name = 'producao/cadastro_produto.html'
    success_url = reverse_lazy('producao:produto_list')

class ProdutoUpdateView(LoginRequiredMixin, UpdateView):
    def form_valid(self, form):
        response = super().form_valid(form)
        registrar_log(self.request, 'Produção', f'Editou produto: {self.object.nome}')
        return response
    model = Produto
    form_class = ProdutoForm
    template_name = 'producao/cadastro_produto.html'
    success_url = reverse_lazy('producao:produto_list')

class ProdutoDeleteView(LoginRequiredMixin, DeleteView):
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        response = super().delete(request, *args, **kwargs)
        registrar_log(request, 'Produção', f'Excluiu produto: {obj.nome}')
        messages.success(self.request, 'Produto excluído com sucesso!')
        return response
    model = Produto
    template_name = 'producao/confirmar_exclusao_produto.html'
    success_url = reverse_lazy('producao:produto_list')

class MateriaPrimaListView(LoginRequiredMixin, ListView):
    model = MateriaPrima
    template_name = 'producao/materiaprima_list.html'
    context_object_name = 'materias_primas'
    ordering = ['nome']

class MateriaPrimaCreateView(LoginRequiredMixin, CreateView):
    def form_valid(self, form):
        response = super().form_valid(form)
        registrar_log(self.request, 'Produção', f'Cadastrou nova matéria-prima: {self.object.nome}')
        return response
    model = MateriaPrima
    form_class = MateriaPrimaForm
    template_name = 'producao/cadastro_materiaprima.html'
    success_url = reverse_lazy('producao:materiaprima_list')

class MateriaPrimaUpdateView(LoginRequiredMixin, UpdateView):
    def form_valid(self, form):
        response = super().form_valid(form)
        registrar_log(self.request, 'Produção', f'Editou matéria-prima: {self.object.nome}')
        return response
    model = MateriaPrima
    form_class = MateriaPrimaForm
    template_name = 'producao/cadastro_materiaprima.html'
    success_url = reverse_lazy('producao:materiaprima_list')

class MateriaPrimaDeleteView(LoginRequiredMixin, DeleteView):
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        response = super().delete(request, *args, **kwargs)
        registrar_log(request, 'Produção', f'Excluiu matéria-prima: {obj.nome}')
        messages.success(self.request, 'Matéria-prima excluída com sucesso!')
        return response
    model = MateriaPrima
    template_name = 'producao/confirmar_exclusao_materiaprima.html'
    success_url = reverse_lazy('producao:materiaprima_list')

class DashboardView(ListView):
    template_name = 'producao/dashboard.html'
    model = OrdemProducao
    context_object_name = 'ordens_andamento'

    def get_queryset(self):
        return OrdemProducao.objects.filter(status__in=['EM_PRODUCAO', 'FINALIZADA'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Dados para o gráfico de produção mensal
        meses = []
        quantidades = []
        today = datetime.now()
        for i in range(6):
            month = today - timedelta(days=30*i)
            meses.insert(0, month.strftime('%b/%Y'))
            quantidades.insert(0, OrdemProducao.objects.filter(
                data_fim__month=month.month,
                data_fim__year=month.year,
                status='FINALIZADA'
            ).count())
        
        context['meses'] = meses
        context['quantidades'] = quantidades

        # Totais do mês atual
        now = datetime.now()
        # Considera apenas ordens com data preenchida
        context['total_ordens_mes'] = OrdemProducao.objects.filter(
            data_inicio__isnull=False,
            data_inicio__month=now.month,
            data_inicio__year=now.year
        ).count() or 0
        context['total_produzido_mes'] = OrdemProducao.objects.filter(
            data_fim__isnull=False,
            data_fim__month=now.month,
            data_fim__year=now.year,
            status='FINALIZADA'
        ).count() or 0

        # Alertas de estoque
        from estoque.models import SaldoEstoque
        context['alertas_estoque'] = [
            {
                'materia_prima': saldo.materia_prima.nome,
                'quantidade_atual': saldo.quantidade_atual,
                'unidade_medida': saldo.materia_prima.unidade_medida,
                'estoque_minimo': round(saldo.materia_prima.estoque_minimo if saldo.materia_prima.estoque_minimo > 0 else saldo.calcular_estoque_minimo(), 2)
            }
            for saldo in SaldoEstoque.objects.all()
            if saldo.quantidade_atual < (saldo.materia_prima.estoque_minimo if saldo.materia_prima.estoque_minimo > 0 else saldo.calcular_estoque_minimo())
        ]
        
        return context

class OrdemProducaoListView(ListView):
    model = OrdemProducao
    template_name = 'producao/ordemproducao_list.html'
    paginate_by = 10
    ordering = ['-data_inicio']

class OrdemProducaoCreateView(CreateView):
    model = OrdemProducao
    form_class = OrdemProducaoForm
    template_name = 'producao/ordemproducao_form.html'
    success_url = reverse_lazy('producao:lista_ordens')

    def form_valid(self, form):
        response = super().form_valid(form)
        logger.info(f"Nova ordem de produção criada: {self.object}")
        return response

class OrdemProducaoDetailView(DetailView):
    model = OrdemProducao
    template_name = 'producao/ordemproducao_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from decimal import Decimal
        custo_unitario = self.object.produto.calcular_custo()
        if not isinstance(custo_unitario, Decimal):
            custo_unitario = Decimal(str(custo_unitario))
        quantidade = self.object.quantidade
        context['custo_total'] = custo_unitario * Decimal(quantidade)
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('format') == 'pdf':
            template = get_template('producao/ordemproducao_pdf.html')
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'filename=ordem_producao_{self.object.id}.pdf'
            
            pisa_status = pisa.CreatePDF(html, dest=response)
            if pisa_status.err:
                return HttpResponse('Erro ao gerar PDF')
            return response
        
        return super().render_to_response(context, **response_kwargs)
