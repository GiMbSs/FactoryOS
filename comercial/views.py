from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from core.views import registrar_log
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.urls import reverse_lazy
from django.utils import timezone
from .models import Cliente, Venda, Fornecedor, ItemVenda
from .forms import ClienteForm, VendaForm, FornecedorForm, ItemVendaForm
from django.forms import inlineformset_factory

class FornecedorListView(ListView):
    model = Fornecedor
    template_name = 'comercial/fornecedor_list.html'
    context_object_name = 'fornecedores'
    paginate_by = 10
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from producao.models import MateriaPrima
        
        # Contar total de matérias-primas
        context['materias_primas_count'] = MateriaPrima.objects.count()
        
        # Contar compras no mês atual
        from django.utils import timezone
        # Aqui você precisaria ter um modelo de Compra ou usar alguma outra lógica
        # para contar as compras. Como não temos esse modelo, vamos usar um valor padrão
        context['compras_mes'] = 0
        
        # Contar novos fornecedores no mês atual
        context['novos_fornecedores_mes'] = Fornecedor.objects.filter(
            data_cadastro__month=timezone.now().month,
            data_cadastro__year=timezone.now().year
        ).count()
        
        return context

class FornecedorUpdateView(UpdateView):
    model = Fornecedor
    form_class = FornecedorForm
    template_name = 'comercial/cadastro_fornecedor.html'
    success_url = reverse_lazy('comercial:lista_fornecedores')
    def form_valid(self, form):
        response = super().form_valid(form)
        registrar_log(self.request, 'Comercial', f'Editou fornecedor: {self.object.nome}')
        return response

class FornecedorDeleteView(DeleteView):
    model = Fornecedor
    template_name = 'comercial/confirmar_exclusao_fornecedor.html'
    success_url = reverse_lazy('comercial:lista_fornecedores')
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        response = super().delete(request, *args, **kwargs)
        registrar_log(request, 'Comercial', f'Excluiu fornecedor: {obj.nome}')
        return response


class FornecedorCreateView(CreateView):
    def form_valid(self, form):
        response = super().form_valid(form)
        registrar_log(self.request, 'Comercial', f'Cadastrou fornecedor: {self.object.nome}')
        return response
    model = Fornecedor
    form_class = FornecedorForm
    template_name = 'comercial/cadastro_fornecedor.html'
    success_url = reverse_lazy('comercial:lista_fornecedores')


class ClienteCreateView(CreateView):
    def form_valid(self, form):
        response = super().form_valid(form)
        registrar_log(self.request, 'Comercial', f'Cadastrou cliente: {self.object.nome}')
        return response
    model = Cliente
    form_class = ClienteForm
    template_name = 'comercial/cadastro_cliente.html'
    success_url = reverse_lazy('comercial:lista_clientes')

class ClienteListView(ListView):
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
        from .models import Venda
        context['total_vendas'] = Venda.objects.count()
        # Contar novos clientes do mês atual
        context['novos_clientes_mes'] = Cliente.objects.filter(
            data_cadastro__month=timezone.now().month,
            data_cadastro__year=timezone.now().year
        ).count()
        return context

class ClienteDeleteView(DeleteView):
    model = Cliente
    template_name = 'comercial/confirmar_exclusao_cliente.html'
    success_url = reverse_lazy('comercial:lista_clientes')
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        response = super().delete(request, *args, **kwargs)
        registrar_log(request, 'Comercial', f'Excluiu cliente: {obj.nome}')
        return response


class ClienteUpdateView(UpdateView):
    def form_valid(self, form):
        response = super().form_valid(form)
        registrar_log(self.request, 'Comercial', f'Editou cliente: {self.object.nome}')
        return response
    model = Cliente
    form_class = ClienteForm
    template_name = 'comercial/cadastro_cliente.html'
    success_url = reverse_lazy('comercial:lista_clientes')

class ToggleClienteView(View):
    def post(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk)
        cliente.ativo = not cliente.ativo
        cliente.save()
        return redirect('comercial:lista_clientes')

from django.contrib import messages

class VendaCreateView(CreateView):
    model = Venda
    form_class = VendaForm
    template_name = 'comercial/cadastro_pedido.html'
    success_url = reverse_lazy('comercial:pedido_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ItemVendaFormSet = inlineformset_factory(Venda, ItemVenda, form=ItemVendaForm, extra=1, can_delete=True)
        if self.request.POST:
            context['itens_formset'] = ItemVendaFormSet(self.request.POST)
        else:
            context['itens_formset'] = ItemVendaFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        itens_formset = context['itens_formset']
        if itens_formset.is_valid() and form.is_valid():
            self.object = form.save()
            itens_formset.instance = self.object
            itens_formset.save()
            messages.success(self.request, 'Pedido cadastrado com sucesso!')
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        context = self.get_context_data()
        itens_formset = context.get('itens_formset')
        if form.errors:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(self.request, f"Erro no campo '{field}': {error}")
        if itens_formset and itens_formset.errors:
            for idx, form_errors in enumerate(itens_formset.errors):
                for field, errors in form_errors.items():
                    for error in errors:
                        messages.error(self.request, f"Erro no item {idx+1}, campo '{field}': {error}")
        return super().form_invalid(form)

class VendaUpdateView(UpdateView):
    model = Venda
    form_class = VendaForm
    template_name = 'comercial/cadastro_pedido.html'
    success_url = reverse_lazy('comercial:pedido_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ItemVendaFormSet = inlineformset_factory(Venda, ItemVenda, form=ItemVendaForm, extra=0, can_delete=True)
        if self.request.POST:
            context['itens_formset'] = ItemVendaFormSet(self.request.POST, instance=self.object)
        else:
            context['itens_formset'] = ItemVendaFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        itens_formset = context['itens_formset']
        if itens_formset.is_valid() and form.is_valid():
            self.object = form.save()
            itens_formset.instance = self.object
            itens_formset.save()
            messages.success(self.request, 'Pedido atualizado com sucesso!')
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        context = self.get_context_data()
        itens_formset = context.get('itens_formset')
        if form.errors:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(self.request, f"Erro no campo '{field}': {error}")
        if itens_formset and itens_formset.errors:
            for idx, form_errors in enumerate(itens_formset.errors):
                for field, errors in form_errors.items():
                    for error in errors:
                        messages.error(self.request, f"Erro no item {idx+1}, campo '{field}': {error}")
        return super().form_invalid(form)

class VendaDeleteView(DeleteView):
    model = Venda
    template_name = 'comercial/confirmar_exclusao_pedido.html'
    success_url = reverse_lazy('comercial:pedido_list')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        response = super().delete(request, *args, **kwargs)
        registrar_log(request, 'Comercial', f'Excluiu venda: {obj.id}')
        messages.success(self.request, 'Pedido excluído com sucesso!')
        return response

class VendaListView(ListView):
    model = Venda
    template_name = 'comercial/pedido_list.html'
    context_object_name = 'pedidos'
    paginate_by = 10
    ordering = ['-data_venda']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Calcular faturamento total
        from django.db.models import Sum
        context['faturamento_total'] = Venda.objects.filter(status='FECHADA').aggregate(Sum('valor_total'))['valor_total__sum'] or 0
        # Contar pedidos pendentes
        context['pedidos_pendentes'] = Venda.objects.filter(status='ABERTA').count()
        # Contar pedidos do mês atual
        context['pedidos_mes'] = Venda.objects.filter(
            data_venda__month=timezone.now().month,
            data_venda__year=timezone.now().year
        ).count()
        return context

class VendaUpdateStatusView(View):
    def post(self, request, pk):
        venda = get_object_or_404(Venda, pk=pk)
        status = request.POST.get('status')
        observacao = request.POST.get('observacao', '')
        data_vencimento = request.POST.get('data_vencimento')
        
        # Verificar status anterior
        status_anterior = venda.status
        
        # Permitir apenas os status ABERTA e FECHADA
        if status in ['ABERTA', 'FECHADA']:
            venda.status = status
            if observacao:
                venda.observacoes = observacao
            venda.save()
            
            # Se a venda foi fechada e não estava fechada antes, criar conta a receber
            if status == 'FECHADA' and status_anterior != 'FECHADA':
                from financeiro.models import ContaReceber
                from django.utils import timezone
                import datetime
                
                # Se não foi informada data de vencimento, usar data atual + 30 dias
                if not data_vencimento:
                    data_vencimento = (timezone.now() + datetime.timedelta(days=30)).date()
                else:
                    # Converter string para data
                    from datetime import datetime as dt
                    data_vencimento = dt.strptime(data_vencimento, '%Y-%m-%d').date()
                
                # Criar conta a receber
                conta_receber = ContaReceber.objects.create(
                    cliente=venda.cliente,
                    valor=venda.valor_total,
                    data_vencimento=data_vencimento,
                    status='PENDENTE',
                    observacoes=f"Gerado automaticamente da venda #{venda.id}. {observacao}"
                )
                
                registrar_log(request, 'Financeiro', f'Criou conta a receber automática da venda #{venda.id}: {conta_receber.cliente} - R${conta_receber.valor}')
                messages.success(request, f'Conta a receber criada automaticamente para o cliente {venda.cliente.nome}')
            
            registrar_log(request, 'Comercial', f'Alterou status do pedido #{venda.id} para {venda.get_status_display()}')
            messages.success(request, f'Status do pedido #{venda.id} alterado para {venda.get_status_display()}')
        else:
            messages.error(request, 'Status inválido')
            
        return redirect('comercial:pedido_list')

class DashboardView(TemplateView):
    template_name = 'comercial/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            from .models import Venda, Cliente
            vendas = Venda.objects.all()[:5] if Venda.objects.exists() else []
            clientes = Cliente.objects.all()[:10] if Cliente.objects.exists() else []
            context['vendas'] = vendas
            context['clientes'] = clientes
            context['vendas_count'] = len(vendas)
            context['clientes_count'] = len(clientes)

            # Financeiro: vendas finalizadas
            vendas_finalizadas = Venda.objects.filter(status='FECHADA')
            context['vendas_finalizadas_count'] = vendas_finalizadas.count()
            context['vendas_finalizadas_valor'] = vendas_finalizadas.aggregate(total=models.Sum('valor_total'))['total'] or 0
        except Exception as e:
            context['vendas'] = []
            context['clientes'] = []
            context['vendas_count'] = 0
            context['clientes_count'] = 0
            context['vendas_finalizadas_count'] = 0
            context['vendas_finalizadas_valor'] = 0
        return context
