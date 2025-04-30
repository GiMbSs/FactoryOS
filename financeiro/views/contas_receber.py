"""
Views para gerenciar contas a receber.
"""
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Q

from core.views import registrar_log
from financeiro.models import ContaReceber
from financeiro.forms import ContaReceberForm


class ContaReceberListView(ListView):
    """
    View para listar contas a receber.
    """
    model = ContaReceber
    template_name = 'financeiro/conta_receber_list.html'
    ordering = ['data_vencimento']
    paginate_by = 10
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obter a data atual usando timezone aware para evitar problemas de fuso horário
        timezone_now = timezone.localtime(timezone.now())
        hoje = timezone_now.date()  # Data local no fuso horário configurado
        mes_atual = hoje.month
        ano_atual = hoje.year
        
        # Adicionar a data ao contexto para uso no template
        context['hoje'] = hoje
        context['mes_atual'] = mes_atual
        context['ano_atual'] = ano_atual
        
        # Calcular total a receber (contas pendentes)
        total_a_receber = ContaReceber.objects.filter(
            status='PENDENTE'
        ).aggregate(
            total=Sum('valor')
        )['total'] or 0
        context['total_a_receber'] = total_a_receber
        
        # Contas vencendo hoje
        contas_vencendo_hoje = ContaReceber.objects.filter(
            Q(status='PENDENTE'),
            Q(data_vencimento=hoje)
        )
        context['contas_vencendo_hoje'] = contas_vencendo_hoje.count()
        
        # Contar contas recebidas no mês atual
        contas_recebidas = ContaReceber.objects.filter(
            Q(status='RECEBIDO'),
            Q(data_recebimento__month=mes_atual),
            Q(data_recebimento__year=ano_atual)
        )
        context['contas_recebidas_mes'] = contas_recebidas.count()
        
        return context


class ContaReceberCreateView(CreateView):
    """
    View para criar novas contas a receber.
    """
    model = ContaReceber
    form_class = ContaReceberForm
    template_name = 'financeiro/cadastro_conta_receber.html'
    success_url = reverse_lazy('financeiro:conta_receber_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        registrar_log(self.request, 'Financeiro', f'Cadastrou conta a receber: {self.object.cliente} - R${self.object.valor}')
        messages.success(self.request, f'Conta para {self.object.cliente} cadastrada com sucesso!')
        return response


class ContaReceberUpdateView(UpdateView):
    """
    View para atualizar contas a receber existentes.
    """
    model = ContaReceber
    form_class = ContaReceberForm
    template_name = 'financeiro/cadastro_conta_receber.html'
    success_url = reverse_lazy('financeiro:conta_receber_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        registrar_log(self.request, 'Financeiro', f'Editou conta a receber: {self.object.cliente} - R${self.object.valor}')
        messages.success(self.request, f'Conta para {self.object.cliente} atualizada com sucesso!')
        return response


class ContaReceberDeleteView(DeleteView):
    """
    View para excluir contas a receber.
    """
    model = ContaReceber
    template_name = 'financeiro/confirmar_exclusao_conta_receber.html'
    success_url = reverse_lazy('financeiro:conta_receber_list')
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        response = super().delete(request, *args, **kwargs)
        registrar_log(request, 'Financeiro', f'Excluiu conta a receber: {obj.cliente} - R${obj.valor}')
        messages.success(self.request, 'Conta a receber excluída com sucesso!')
        return response


class RegistrarRecebimentoView(View):
    """
    View para registrar recebimento de contas a receber.
    """
    def post(self, request, pk):
        conta = get_object_or_404(ContaReceber, pk=pk)
        
        # Verifica se a conta já está recebida
        if conta.status == 'RECEBIDO':
            messages.warning(request, 'Esta conta já foi recebida anteriormente.')
            return redirect('financeiro:conta_receber_list')
        
        # Obtém os dados do formulário
        data_recebimento = request.POST.get('data_recebimento')
        valor_recebido = request.POST.get('valor_recebido')
        forma_pagamento = request.POST.get('forma_pagamento', 'DINHEIRO')
        observacao = request.POST.get('observacao', '')
        
        # Atualiza os dados da conta
        conta.status = 'RECEBIDO'
        conta.data_recebimento = data_recebimento
        
        if observacao:
            conta.observacoes = (conta.observacoes or '') + f"\nRecebimento em {data_recebimento}: {observacao}"
        
        conta.save()
        
        registrar_log(request, 'Financeiro', f'Registrou recebimento da conta: {conta.cliente} - R${valor_recebido}')
        messages.success(request, 'Recebimento registrado com sucesso!')
        return redirect('financeiro:conta_receber_list')