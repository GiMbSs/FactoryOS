"""
Views para gerenciar contas a pagar.
"""
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Q

from core.views import registrar_log
from financeiro.models import ContaPagar
from financeiro.forms import ContaPagarForm


class ContaPagarListView(ListView):
    """
    View para listar contas a pagar.
    """
    model = ContaPagar
    template_name = 'financeiro/conta_pagar_list.html'
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
        
        # Calcular total a pagar (contas pendentes)
        total_a_pagar = ContaPagar.objects.filter(
            status='PENDENTE'
        ).aggregate(
            total=Sum('valor')
        )['total'] or 0
        context['total_a_pagar'] = total_a_pagar
        
        # Contas vencendo hoje
        contas_vencendo_hoje = ContaPagar.objects.filter(
            Q(status='PENDENTE'),
            Q(data_vencimento=hoje)
        )
        context['contas_vencendo_hoje'] = contas_vencendo_hoje.count()
        
        # Contar contas pagas no mês atual
        contas_pagas = ContaPagar.objects.filter(
            Q(status='PAGO'),
            Q(data_pagamento__month=mes_atual),
            Q(data_pagamento__year=ano_atual)
        )
        context['contas_pagas_mes'] = contas_pagas.count()
        
        return context


class ContaPagarCreateView(CreateView):
    """
    View para criar novas contas a pagar.
    """
    model = ContaPagar
    form_class = ContaPagarForm
    template_name = 'financeiro/cadastro_conta_pagar.html'
    success_url = reverse_lazy('financeiro:conta_pagar_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        registrar_log(self.request, 'Financeiro', f'Cadastrou conta a pagar: {self.object.fornecedor} - R${self.object.valor}')
        messages.success(self.request, f'Conta para {self.object.fornecedor} cadastrada com sucesso!')
        return response


class ContaPagarUpdateView(UpdateView):
    """
    View para atualizar contas a pagar existentes.
    """
    model = ContaPagar
    form_class = ContaPagarForm
    template_name = 'financeiro/cadastro_conta_pagar.html'
    success_url = reverse_lazy('financeiro:conta_pagar_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        registrar_log(self.request, 'Financeiro', f'Editou conta a pagar: {self.object.fornecedor} - R${self.object.valor}')
        messages.success(self.request, f'Conta para {self.object.fornecedor} atualizada com sucesso!')
        return response


class ContaPagarDeleteView(DeleteView):
    """
    View para excluir contas a pagar.
    """
    model = ContaPagar
    template_name = 'financeiro/confirmar_exclusao_conta_pagar.html'
    success_url = reverse_lazy('financeiro:conta_pagar_list')
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        response = super().delete(request, *args, **kwargs)
        registrar_log(request, 'Financeiro', f'Excluiu conta a pagar: {obj.fornecedor} - R${obj.valor}')
        messages.success(self.request, 'Conta a pagar excluída com sucesso!')
        return response


class RegistrarPagamentoView(View):
    """
    View para registrar pagamento de contas a pagar.
    """
    def post(self, request, pk):
        conta = get_object_or_404(ContaPagar, pk=pk)
        
        # Verifica se a conta já está paga
        if conta.status == 'PAGO':
            messages.warning(request, 'Esta conta já foi paga anteriormente.')
            return redirect('financeiro:conta_pagar_list')
        
        # Obtém os dados do formulário
        data_pagamento = request.POST.get('data_pagamento')
        valor_pago = request.POST.get('valor_pago')
        observacao = request.POST.get('observacao', '')
        
        # Atualiza os dados da conta
        conta.status = 'PAGO'
        conta.data_pagamento = data_pagamento
        
        if observacao:
            conta.observacoes = (conta.observacoes or '') + f"\nPagamento em {data_pagamento}: {observacao}"
        
        conta.save()
        
        registrar_log(request, 'Financeiro', f'Registrou pagamento da conta: {conta.fornecedor} - R${valor_pago}')
        messages.success(request, 'Pagamento registrado com sucesso!')
        return redirect('financeiro:conta_pagar_list')