from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from core.views import registrar_log
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.urls import reverse_lazy
from django.utils import timezone
from .models import Cliente, Venda, Fornecedor, ItemVenda
from .forms import ClienteForm, VendaForm, FornecedorForm, ItemVendaForm
from django.forms import inlineformset_factory
from django.db import models

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
        
        # Verificar se há pelo menos um item preenchido corretamente
        algum_item_valido = False
        for form_item in itens_formset.forms:
            if form_item.is_valid() and form_item.cleaned_data and not form_item.cleaned_data.get('DELETE', False):
                # Verificar se os campos principais estão preenchidos
                produto = form_item.cleaned_data.get('produto')
                quantidade = form_item.cleaned_data.get('quantidade')
                preco = form_item.cleaned_data.get('preco_unitario')
                if produto and quantidade and preco:
                    algum_item_valido = True
                    break
        
        # Se pelo menos um item é válido, ignorar os erros dos outros itens vazios
        if algum_item_valido:
            # Limpar os erros de itens vazios
            for form_item in itens_formset.forms:
                if not form_item.is_valid() and form_item.errors:
                    # Se for um item vazio, ignorar os erros
                    data = form_item.cleaned_data if hasattr(form_item, 'cleaned_data') else {}
                    if not data.get('produto') and not data.get('quantidade') and not data.get('preco_unitario'):
                        for field in form_item.errors:
                            form_item.errors[field] = []
                        form_item._errors = {}
            
            # Forçar o formset a ser válido se havia apenas erros em itens vazios
            if not itens_formset.is_valid():
                # Recalcular a validação do formset
                itens_formset.is_valid()
        
        if itens_formset.is_valid() and form.is_valid():
            self.object = form.save()
            itens_formset.instance = self.object
            
            # Salvar apenas os itens com dados
            instances = itens_formset.save(commit=False)
            for instance in instances:
                # Verificação mais segura para evitar o erro RelatedObjectDoesNotExist
                try:
                    produto_exists = instance.produto_id is not None
                except:
                    produto_exists = False
                
                # Só salva se tiver produto, quantidade e preço
                if produto_exists and instance.quantidade and instance.preco_unitario:
                    instance.save()
            
            # Tratar itens marcados para deleção
            for obj in itens_formset.deleted_objects:
                obj.delete()
                
            messages.success(self.request, 'Pedido cadastrado com sucesso!')
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        context = self.get_context_data()
        itens_formset = context.get('itens_formset')
        
        # Agrupar mensagens de erro
        form_errors = []
        formset_errors = []
        
        # Coletar erros do formulário principal
        if form.errors:
            for field, errors in form.errors.items():
                for error in errors:
                    field_label = form[field].label or field
                    form_errors.append(f"{field_label}: {error}")
        
        # Coletar erros do formset (apenas para itens com dados parciais)
        if itens_formset and itens_formset.errors:
            item_errors = {}  # Dicionário para agrupar erros por item
            
            for idx, form_errors_dict in enumerate(itens_formset.errors):
                if form_errors_dict:  # Se há erros neste formulário
                    item_form = itens_formset.forms[idx]
                    
                    # Verificar se o item tem pelo menos um campo preenchido
                    data = item_form.cleaned_data if hasattr(item_form, 'cleaned_data') else {}
                    produto = data.get('produto')
                    quantidade = data.get('quantidade')
                    preco = data.get('preco_unitario')
                    
                    # Se pelo menos um campo está preenchido, considerar os erros
                    if produto or quantidade or preco:
                        item_num = idx + 1
                        if item_num not in item_errors:
                            item_errors[item_num] = []
                            
                        for field, errors in form_errors_dict.items():
                            field_label = item_form[field].label or field
                            for error in errors:
                                item_errors[item_num].append(f"{field_label}: {error}")
            
            # Converter os erros agrupados em mensagens
            for item_num, errors in item_errors.items():
                if errors:
                    formset_errors.append(f"Item {item_num}: {' / '.join(errors)}")
        
        # Exibir mensagens de erro agrupadas
        if form_errors:
            messages.error(self.request, f"Erros no formulário: {' / '.join(form_errors)}")
        
        if formset_errors:
            for error in formset_errors:
                messages.error(self.request, error)
                
        # Se não houver produtos válidos, mostrar uma mensagem mais clara
        if not form_errors and not formset_errors and itens_formset and not itens_formset.is_valid():
            messages.error(self.request, "Adicione pelo menos um item válido ao pedido. É necessário preencher os campos Produto, Quantidade e Preço.")
            
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
        
        # Verificar se há pelo menos um item preenchido corretamente
        algum_item_valido = False
        for form_item in itens_formset.forms:
            if form_item.is_valid() and form_item.cleaned_data and not form_item.cleaned_data.get('DELETE', False):
                # Verificar se os campos principais estão preenchidos
                produto = form_item.cleaned_data.get('produto')
                quantidade = form_item.cleaned_data.get('quantidade')
                preco = form_item.cleaned_data.get('preco_unitario')
                if produto and quantidade and preco:
                    algum_item_valido = True
                    break
        
        # Se pelo menos um item é válido, ignorar os erros dos outros itens vazios
        if algum_item_valido:
            # Limpar os erros de itens vazios
            for form_item in itens_formset.forms:
                if not form_item.is_valid() and form_item.errors:
                    # Se for um item vazio, ignorar os erros
                    data = form_item.cleaned_data if hasattr(form_item, 'cleaned_data') else {}
                    if not data.get('produto') and not data.get('quantidade') and not data.get('preco_unitario'):
                        for field in form_item.errors:
                            form_item.errors[field] = []
                        form_item._errors = {}
            
            # Forçar o formset a ser válido se havia apenas erros em itens vazios
            if not itens_formset.is_valid():
                # Recalcular a validação do formset
                itens_formset.is_valid()
                
        if itens_formset.is_valid() and form.is_valid():
            self.object = form.save()
            itens_formset.instance = self.object
            
            # Salvar apenas os itens com dados
            instances = itens_formset.save(commit=False)
            for instance in instances:
                # Verificação mais segura para evitar o erro RelatedObjectDoesNotExist
                try:
                    produto_exists = instance.produto_id is not None
                except:
                    produto_exists = False
                
                # Só salva se tiver produto, quantidade e preço
                if produto_exists and instance.quantidade and instance.preco_unitario:
                    instance.save()
            
            # Tratar itens marcados para deleção
            for obj in itens_formset.deleted_objects:
                obj.delete()
                
            messages.success(self.request, 'Pedido atualizado com sucesso!')
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        context = self.get_context_data()
        itens_formset = context.get('itens_formset')
        
        # Agrupar mensagens de erro
        form_errors = []
        formset_errors = []
        
        # Coletar erros do formulário principal
        if form.errors:
            for field, errors in form.errors.items():
                for error in errors:
                    field_label = form[field].label or field
                    form_errors.append(f"{field_label}: {error}")
        
        # Coletar erros do formset (apenas para itens com dados parciais)
        if itens_formset and itens_formset.errors:
            item_errors = {}  # Dicionário para agrupar erros por item
            
            for idx, form_errors_dict in enumerate(itens_formset.errors):
                if form_errors_dict:  # Se há erros neste formulário
                    item_form = itens_formset.forms[idx]
                    
                    # Verificar se o item tem pelo menos um campo preenchido
                    data = item_form.cleaned_data if hasattr(item_form, 'cleaned_data') else {}
                    produto = data.get('produto')
                    quantidade = data.get('quantidade')
                    preco = data.get('preco_unitario')
                    
                    # Se pelo menos um campo está preenchido, considerar os erros
                    if produto or quantidade or preco:
                        item_num = idx + 1
                        if item_num not in item_errors:
                            item_errors[item_num] = []
                            
                        for field, errors in form_errors_dict.items():
                            field_label = item_form[field].label or field
                            for error in errors:
                                item_errors[item_num].append(f"{field_label}: {error}")
            
            # Converter os erros agrupados em mensagens
            for item_num, errors in item_errors.items():
                if errors:
                    formset_errors.append(f"Item {item_num}: {' / '.join(errors)}")
        
        # Exibir mensagens de erro agrupadas
        if form_errors:
            messages.error(self.request, f"Erros no formulário: {' / '.join(form_errors)}")
        
        if formset_errors:
            for error in formset_errors:
                messages.error(self.request, error)
                
        # Se não houver produtos válidos, mostrar uma mensagem mais clara
        if not form_errors and not formset_errors and itens_formset and not itens_formset.is_valid():
            messages.error(self.request, "Adicione pelo menos um item válido ao pedido. É necessário preencher os campos Produto, Quantidade e Preço.")
            
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
