from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from core.views import registrar_log
from django.contrib import messages
from django.urls import reverse_lazy
from .models import ContaPagar, ContaReceber
from django.db import models
from .forms import ContaPagarForm, ContaReceberForm

class ContaPagarListView(ListView):
    model = ContaPagar
    template_name = 'financeiro/conta_pagar_list.html'
    ordering = ['data_vencimento']
    paginate_by = 10

class ContaPagarCreateView(CreateView):
    def form_valid(self, form):
        response = super().form_valid(form)
        registrar_log(self.request, 'Financeiro', f'Cadastrou conta a pagar: {self.object.fornecedor} - R${self.object.valor}')
        return response
    model = ContaPagar
    form_class = ContaPagarForm
    template_name = 'financeiro/cadastro_conta_pagar.html'
    success_url = reverse_lazy('financeiro:conta_pagar_list')

class ContaPagarUpdateView(UpdateView):
    def form_valid(self, form):
        response = super().form_valid(form)
        registrar_log(self.request, 'Financeiro', f'Editou conta a pagar: {self.object.fornecedor} - R${self.object.valor}')
        return response
    model = ContaPagar
    form_class = ContaPagarForm
    template_name = 'financeiro/cadastro_conta_pagar.html'
    success_url = reverse_lazy('financeiro:conta_pagar_list')

class ContaReceberListView(ListView):
    model = ContaReceber
    template_name = 'financeiro/conta_receber_list.html'
    ordering = ['data_vencimento']
    paginate_by = 10

class ContaPagarDeleteView(DeleteView):
    model = ContaPagar
    template_name = 'financeiro/confirmar_exclusao_conta_pagar.html'
    success_url = reverse_lazy('financeiro:conta_pagar_list')
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        response = super().delete(request, *args, **kwargs)
        registrar_log(request, 'Financeiro', f'Excluiu conta a pagar: {obj.fornecedor} - R${obj.valor}')
        messages.success(self.request, 'Conta a pagar excluída com sucesso!')
        return response

class ContaReceberDeleteView(DeleteView):
    model = ContaReceber
    template_name = 'financeiro/confirmar_exclusao_conta_receber.html'
    success_url = reverse_lazy('financeiro:conta_receber_list')
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        response = super().delete(request, *args, **kwargs)
        registrar_log(request, 'Financeiro', f'Excluiu conta a receber: {obj.cliente} - R${obj.valor}')
        messages.success(self.request, 'Conta a receber excluída com sucesso!')
        return response

class ContaReceberCreateView(CreateView):
    def form_valid(self, form):
        response = super().form_valid(form)
        registrar_log(self.request, 'Financeiro', f'Cadastrou conta a receber: {self.object.cliente} - R${self.object.valor}')
        return response
    model = ContaReceber
    form_class = ContaReceberForm
    template_name = 'financeiro/cadastro_conta_receber.html'
    success_url = reverse_lazy('financeiro:conta_receber_list')

class ContaReceberUpdateView(UpdateView):
    def form_valid(self, form):
        response = super().form_valid(form)
        registrar_log(self.request, 'Financeiro', f'Editou conta a receber: {self.object.cliente} - R${self.object.valor}')
        return response
    model = ContaReceber
    form_class = ContaReceberForm
    template_name = 'financeiro/cadastro_conta_receber.html'
    success_url = reverse_lazy('financeiro:conta_receber_list')

class DashboardView(ListView):
    template_name = 'financeiro/dashboard.html'
    model = ContaPagar

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Dados para cards
        context['contas_pagar_pendentes'] = ContaPagar.objects.filter(status='PENDENTE').count()
        context['contas_pagar_pagas'] = ContaPagar.objects.filter(status='PAGO').count()
        context['contas_receber_pendentes'] = ContaReceber.objects.filter(status='PENDENTE').count()
        context['contas_receber_recebidas'] = ContaReceber.objects.filter(status='RECEBIDO').count()
        context['valor_pagar_pendente'] = ContaPagar.objects.filter(status='PENDENTE').aggregate(total=models.Sum('valor'))['total'] or 0
        context['valor_pagar_pago'] = ContaPagar.objects.filter(status='PAGO').aggregate(total=models.Sum('valor'))['total'] or 0
        context['valor_receber_pendente'] = ContaReceber.objects.filter(status='PENDENTE').aggregate(total=models.Sum('valor'))['total'] or 0
        context['valor_receber_recebido'] = ContaReceber.objects.filter(status='RECEBIDO').aggregate(total=models.Sum('valor'))['total'] or 0
        context['saldo'] = (context['valor_receber_recebido'] or 0) - (context['valor_pagar_pago'] or 0)
        # Para gráficos
        context['grafico_pagar'] = {
            'labels': ['Pendente', 'Pago', 'Cancelado'],
            'data': [
                ContaPagar.objects.filter(status='PENDENTE').count(),
                ContaPagar.objects.filter(status='PAGO').count(),
                ContaPagar.objects.filter(status='CANCELADO').count(),
            ]
        }
        context['grafico_receber'] = {
            'labels': ['Pendente', 'Recebido', 'Cancelado'],
            'data': [
                ContaReceber.objects.filter(status='PENDENTE').count(),
                ContaReceber.objects.filter(status='RECEBIDO').count(),
                ContaReceber.objects.filter(status='CANCELADO').count(),
            ]
        }
        return context
