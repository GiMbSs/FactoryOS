"""
Views para gerenciamento de vendas no sistema.
"""
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from django.db import models
from django.db.models import Sum
from django.forms import inlineformset_factory

from core.views import registrar_log
from comercial.models import Venda, ItemVenda
from comercial.forms import VendaForm, ItemVendaForm


class VendaListView(ListView):
    """
    View para listar vendas/pedidos cadastrados no sistema.
    """
    model = Venda
    template_name = 'comercial/pedido_list.html'
    context_object_name = 'pedidos'
    paginate_by = 10
    ordering = ['-data_venda']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['faturamento_total'] = Venda.objects.filter(
            status='FECHADA'
        ).aggregate(
            Sum('valor_total')
        )['valor_total__sum'] or 0
        
        context['pedidos_pendentes'] = Venda.objects.filter(status='ABERTA').count()
        
        context['pedidos_mes'] = Venda.objects.filter(
            data_venda__month=timezone.now().month,
            data_venda__year=timezone.now().year
        ).count()
        
        return context


class VendaCreateView(CreateView):
    """
    View para criar novas vendas/pedidos.
    """
    model = Venda
    form_class = VendaForm
    template_name = 'comercial/cadastro_pedido.html'
    success_url = reverse_lazy('comercial:pedido_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ItemVendaFormSet = inlineformset_factory(
            Venda, 
            ItemVenda, 
            form=ItemVendaForm, 
            extra=1, 
            can_delete=True
        )
        
        if self.request.POST:
            context['itens_formset'] = ItemVendaFormSet(self.request.POST)
        else:
            context['itens_formset'] = ItemVendaFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        itens_formset = context['itens_formset']
        
        algum_item_valido = False
        for form_item in itens_formset.forms:
            if form_item.is_valid() and form_item.cleaned_data and not form_item.cleaned_data.get('DELETE', False):
                produto = form_item.cleaned_data.get('produto')
                quantidade = form_item.cleaned_data.get('quantidade')
                preco = form_item.cleaned_data.get('preco_unitario')
                if produto and quantidade and preco:
                    algum_item_valido = True
                    break
        
        if algum_item_valido:
            for form_item in itens_formset.forms:
                if not form_item.is_valid() and form_item.errors:
                    data = form_item.cleaned_data if hasattr(form_item, 'cleaned_data') else {}
                    if not data.get('produto') and not data.get('quantidade') and not data.get('preco_unitario'):
                        for field in form_item.errors:
                            form_item.errors[field] = []
                        form_item._errors = {}
            
            if not itens_formset.is_valid():
                itens_formset.is_valid()
        
        if itens_formset.is_valid() and form.is_valid():
            self.object = form.save()
            itens_formset.instance = self.object
            
            instances = itens_formset.save(commit=False)
            for instance in instances:
                try:
                    produto_exists = instance.produto_id is not None
                except:
                    produto_exists = False
                
                if produto_exists and instance.quantidade and instance.preco_unitario:
                    instance.save()
            
            for obj in itens_formset.deleted_objects:
                obj.delete()
                
            messages.success(self.request, 'Pedido cadastrado com sucesso!')
            registrar_log(self.request, 'Comercial', f'Cadastrou pedido #{self.object.id} para {self.object.cliente.nome}')
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        context = self.get_context_data()
        itens_formset = context.get('itens_formset')
        
        form_errors = []
        formset_errors = []
        
        if form.errors:
            for field, errors in form.errors.items():
                for error in errors:
                    field_label = form[field].label or field
                    form_errors.append(f"{field_label}: {error}")
        
        if itens_formset and itens_formset.errors:
            item_errors = {}
            
            for idx, form_errors_dict in enumerate(itens_formset.errors):
                if form_errors_dict:
                    item_form = itens_formset.forms[idx]
                    
                    data = item_form.cleaned_data if hasattr(item_form, 'cleaned_data') else {}
                    produto = data.get('produto')
                    quantidade = data.get('quantidade')
                    preco = data.get('preco_unitario')
                    
                    if produto or quantidade or preco:
                        item_num = idx + 1
                        if item_num not in item_errors:
                            item_errors[item_num] = []
                            
                        for field, errors in form_errors_dict.items():
                            field_label = item_form[field].label or field
                            for error in errors:
                                item_errors[item_num].append(f"{field_label}: {error}")
            
            for item_num, errors in item_errors.items():
                if errors:
                    formset_errors.append(f"Item {item_num}: {' / '.join(errors)}")
        
        if form_errors:
            messages.error(self.request, f"Erros no formulário: {' / '.join(form_errors)}")
        
        if formset_errors:
            for error in formset_errors:
                messages.error(self.request, error)
                
        if not form_errors and not formset_errors and itens_formset and not itens_formset.is_valid():
            messages.error(self.request, "Adicione pelo menos um item válido ao pedido. É necessário preencher os campos Produto, Quantidade e Preço.")
            
        return super().form_invalid(form)


class VendaUpdateView(UpdateView):
    """
    View para atualizar vendas/pedidos existentes.
    """
    model = Venda
    form_class = VendaForm
    template_name = 'comercial/cadastro_pedido.html'
    success_url = reverse_lazy('comercial:pedido_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ItemVendaFormSet = inlineformset_factory(
            Venda, 
            ItemVenda, 
            form=ItemVendaForm, 
            extra=0, 
            can_delete=True
        )
        
        if self.request.POST:
            context['itens_formset'] = ItemVendaFormSet(self.request.POST, instance=self.object)
        else:
            context['itens_formset'] = ItemVendaFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        itens_formset = context['itens_formset']
        
        algum_item_valido = False
        for form_item in itens_formset.forms:
            if form_item.is_valid() and form_item.cleaned_data and not form_item.cleaned_data.get('DELETE', False):
                produto = form_item.cleaned_data.get('produto')
                quantidade = form_item.cleaned_data.get('quantidade')
                preco = form_item.cleaned_data.get('preco_unitario')
                if produto and quantidade and preco:
                    algum_item_valido = True
                    break
        
        if algum_item_valido:
            for form_item in itens_formset.forms:
                if not form_item.is_valid() and form_item.errors:
                    data = form_item.cleaned_data if hasattr(form_item, 'cleaned_data') else {}
                    if not data.get('produto') and not data.get('quantidade') and not data.get('preco_unitario'):
                        for field in form_item.errors:
                            form_item.errors[field] = []
                        form_item._errors = {}
            
            if not itens_formset.is_valid():
                itens_formset.is_valid()
                
        if itens_formset.is_valid() and form.is_valid():
            self.object = form.save()
            itens_formset.instance = self.object
            
            instances = itens_formset.save(commit=False)
            for instance in instances:
                try:
                    produto_exists = instance.produto_id is not None
                except:
                    produto_exists = False
                
                if produto_exists and instance.quantidade and instance.preco_unitario:
                    instance.save()
            
            for obj in itens_formset.deleted_objects:
                obj.delete()
                
            messages.success(self.request, 'Pedido atualizado com sucesso!')
            registrar_log(self.request, 'Comercial', f'Atualizou pedido #{self.object.id} de {self.object.cliente.nome}')
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        context = self.get_context_data()
        itens_formset = context.get('itens_formset')
        
        form_errors = []
        formset_errors = []
        
        if form.errors:
            for field, errors in form.errors.items():
                for error in errors:
                    field_label = form[field].label or field
                    form_errors.append(f"{field_label}: {error}")
        
        if itens_formset and itens_formset.errors:
            item_errors = {}
            
            for idx, form_errors_dict in enumerate(itens_formset.errors):
                if form_errors_dict:
                    item_form = itens_formset.forms[idx]
                    
                    data = item_form.cleaned_data if hasattr(item_form, 'cleaned_data') else {}
                    produto = data.get('produto')
                    quantidade = data.get('quantidade')
                    preco = data.get('preco_unitario')
                    
                    if produto or quantidade or preco:
                        item_num = idx + 1
                        if item_num not in item_errors:
                            item_errors[item_num] = []
                            
                        for field, errors in form_errors_dict.items():
                            field_label = item_form[field].label or field
                            for error in errors:
                                item_errors[item_num].append(f"{field_label}: {error}")
            
            for item_num, errors in item_errors.items():
                if errors:
                    formset_errors.append(f"Item {item_num}: {' / '.join(errors)}")
        
        if form_errors:
            messages.error(self.request, f"Erros no formulário: {' / '.join(form_errors)}")
        
        if formset_errors:
            for error in formset_errors:
                messages.error(self.request, error)
                
        if not form_errors and not formset_errors and itens_formset and not itens_formset.is_valid():
            messages.error(self.request, "Adicione pelo menos um item válido ao pedido. É necessário preencher os campos Produto, Quantidade e Preço.")
            
        return super().form_invalid(form)


class VendaDeleteView(DeleteView):
    """
    View para excluir vendas/pedidos.
    """
    model = Venda
    template_name = 'comercial/confirmar_exclusao_pedido.html'
    success_url = reverse_lazy('comercial:pedido_list')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        response = super().delete(request, *args, **kwargs)
        registrar_log(request, 'Comercial', f'Excluiu venda: {obj.id}')
        messages.success(self.request, 'Pedido excluído com sucesso!')
        return response


class VendaUpdateStatusView(View):
    """
    View para atualizar o status de vendas/pedidos.
    """
    def post(self, request, pk):
        venda = get_object_or_404(Venda, pk=pk)
        status = request.POST.get('status')
        observacao = request.POST.get('observacao', '')
        data_vencimento = request.POST.get('data_vencimento')
        
        status_anterior = venda.status
        
        if status in ['ABERTA', 'FECHADA']:
            venda.status = status
            if observacao:
                venda.observacoes = observacao
            venda.save()
            
            if status == 'FECHADA' and status_anterior != 'FECHADA':
                from financeiro.models import ContaReceber
                import datetime
                
                if not data_vencimento:
                    data_vencimento = (timezone.now() + datetime.timedelta(days=30)).date()
                else:
                    from datetime import datetime as dt
                    data_vencimento = dt.strptime(data_vencimento, '%Y-%m-%d').date()
                
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