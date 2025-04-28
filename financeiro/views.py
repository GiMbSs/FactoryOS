from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, View
from core.views import registrar_log
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from .models import ContaPagar, ContaReceber
from django.db import models
from .forms import ContaPagarForm, ContaReceberForm

class ContaPagarListView(ListView):
    model = ContaPagar
    template_name = 'financeiro/conta_pagar_list.html'
    ordering = ['data_vencimento']
    paginate_by = 10
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.utils import timezone
        from django.db.models import Sum, Q
        import datetime
        
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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.utils import timezone
        from django.db.models import Sum, Q
        import datetime
        
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
        from django.utils import timezone
        import datetime
        
        # Obter a data atual usando timezone aware para evitar problemas de fuso horário
        timezone_now = timezone.localtime(timezone.now())
        hoje = timezone_now.date()
        mes_atual = hoje.month
        ano_atual = hoje.year
        
        # Dados para cards
        context['contas_pagar_pendentes'] = ContaPagar.objects.filter(status='PENDENTE').count()
        context['contas_pagar_pagas'] = ContaPagar.objects.filter(status='PAGO').count()
        context['contas_receber_pendentes'] = ContaReceber.objects.filter(status='PENDENTE').count()
        context['contas_receber_recebidas'] = ContaReceber.objects.filter(status='RECEBIDO').count()
        context['valor_pagar_pendente'] = ContaPagar.objects.filter(status='PENDENTE').aggregate(total=models.Sum('valor'))['total'] or 0
        context['valor_pagar_pago'] = ContaPagar.objects.filter(status='PAGO').aggregate(total=models.Sum('valor'))['total'] or 0
        context['valor_receber_pendente'] = ContaReceber.objects.filter(status='PENDENTE').aggregate(total=models.Sum('valor'))['total'] or 0
        context['valor_receber_recebido'] = ContaReceber.objects.filter(status='RECEBIDO').aggregate(total=models.Sum('valor'))['total'] or 0
        
        # Dados de vendas finalizadas
        from comercial.models import Venda
        
        # Total de vendas finalizadas
        context['vendas_finalizadas'] = Venda.objects.filter(status='FECHADA').count()
        
        # Valor total de vendas finalizadas
        context['valor_vendas_finalizadas'] = Venda.objects.filter(status='FECHADA').aggregate(total=models.Sum('valor_total'))['total'] or 0
        
        # O saldo agora considera as vendas finalizadas
        total_entradas = (context['valor_receber_recebido'] or 0) + (context['valor_vendas_finalizadas'] or 0)
        total_saidas = (context['valor_pagar_pago'] or 0)
        context['saldo'] = total_entradas - total_saidas
        
        # Vendas finalizadas no mês atual
        context['vendas_finalizadas_mes'] = Venda.objects.filter(
            status='FECHADA',
            data_venda__month=mes_atual,
            data_venda__year=ano_atual
        ).count()
        
        # Valor de vendas finalizadas no mês atual
        context['valor_vendas_finalizadas_mes'] = Venda.objects.filter(
            status='FECHADA',
            data_venda__month=mes_atual,
            data_venda__year=ano_atual
        ).aggregate(total=models.Sum('valor_total'))['total'] or 0
        
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
        
        # Gráfico de vendas por mês (últimos 6 meses)
        meses = []
        dados_vendas = []
        
        for i in range(5, -1, -1):
            # Calcula o mês e ano para cada um dos últimos 6 meses
            mes = mes_atual - i
            ano = ano_atual
            
            # Ajusta o ano se o mês for negativo
            while mes <= 0:
                mes += 12
                ano -= 1
            
            # Obtém o nome do mês
            nome_mes = datetime.date(ano, mes, 1).strftime('%b')
            meses.append(f'{nome_mes}/{str(ano)[2:]}')
            
            # Calcula o valor das vendas para este mês
            valor_vendas = Venda.objects.filter(
                status='FECHADA',
                data_venda__month=mes,
                data_venda__year=ano
            ).aggregate(total=models.Sum('valor_total'))['total'] or 0
            
            dados_vendas.append(float(valor_vendas))
        
        context['grafico_vendas_mensal'] = {
            'labels': meses,
            'data': dados_vendas
        }
        return context


class RegistrarPagamentoView(View):
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
        # Não usamos valor_pago para evitar erro caso o campo não exista
        
        if observacao:
            conta.observacoes = (conta.observacoes or '') + f"\nPagamento em {data_pagamento}: {observacao}"
        
        conta.save()
        
        registrar_log(request, 'Financeiro', f'Registrou pagamento da conta: {conta.fornecedor} - R${valor_pago}')
        messages.success(request, 'Pagamento registrado com sucesso!')
        return redirect('financeiro:conta_pagar_list')


class RegistrarRecebimentoView(View):
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
        # Removemos referências a campos que podem não existir
        # conta.valor_recebido = valor_recebido
        # conta.forma_pagamento = forma_pagamento
        
        if observacao:
            conta.observacoes = (conta.observacoes or '') + f"\nRecebimento em {data_recebimento}: {observacao}"
        
        conta.save()
        
        registrar_log(request, 'Financeiro', f'Registrou recebimento da conta: {conta.cliente} - R${valor_recebido}')
        messages.success(request, 'Recebimento registrado com sucesso!')
        return redirect('financeiro:conta_receber_list')
