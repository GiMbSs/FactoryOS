from django.views.generic import CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db import transaction

from estoque.models import MovimentacaoEstoque, SaldoEstoque


class MovimentacaoCreateView(LoginRequiredMixin, CreateView):
    model = MovimentacaoEstoque
    template_name = 'estoque/movimentacao_form.html'
    fields = ['materia_prima', 'quantidade', 'tipo_movimento', 'origem_destino', 'lote', 'observacao']
    success_url = reverse_lazy('estoque:movimentacoes_list')
    
    def form_valid(self, form):
        try:
            with transaction.atomic():
                movimentacao = form.save(commit=False)
                
                # Obter o saldo atual da matéria prima
                materia_prima = movimentacao.materia_prima
                saldo, created = SaldoEstoque.objects.get_or_create(
                    materia_prima=materia_prima,
                    defaults={'quantidade_atual': 0}
                )
                
                # Atualizar o saldo de acordo com o tipo de movimento
                quantidade = float(movimentacao.quantidade)
                if movimentacao.tipo_movimento == 'ENTRADA':
                    saldo.quantidade_atual = float(saldo.quantidade_atual) + quantidade
                elif movimentacao.tipo_movimento == 'SAIDA':
                    # Verificar se tem saldo suficiente para saída
                    if float(saldo.quantidade_atual) < quantidade:
                        form.add_error('quantidade', 
                                      f'Quantidade insuficiente em estoque. Saldo atual: {saldo.quantidade_atual}')
                        return self.form_invalid(form)
                    saldo.quantidade_atual = float(saldo.quantidade_atual) - quantidade
                
                # Salvar as alterações após fazer os cálculos
                movimentacao.save()
                saldo.save()
                
                messages.success(self.request, 'Movimentação registrada com sucesso.')
                return super(CreateView, self).form_valid(form)
        except Exception as e:
            messages.error(self.request, f'Erro ao registrar movimentação: {str(e)}')
            return self.form_invalid(form)


class MovimentacaoListView(LoginRequiredMixin, ListView):
    model = MovimentacaoEstoque
    template_name = 'estoque/movimentacoes_list.html'
    context_object_name = 'movimentacoes'
    ordering = ['-data', '-id']
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por materia_prima se especificado
        materia_prima_id = self.request.GET.get('materia_prima')
        if materia_prima_id:
            queryset = queryset.filter(materia_prima_id=materia_prima_id)
        
        # Filtrar por tipo de movimento se especificado
        tipo_movimento = self.request.GET.get('tipo_movimento')
        if tipo_movimento:
            queryset = queryset.filter(tipo_movimento=tipo_movimento)
        
        # Filtrar por data se especificado
        data_inicial = self.request.GET.get('data_inicial')
        data_final = self.request.GET.get('data_final')
        
        if data_inicial:
            queryset = queryset.filter(data__gte=data_inicial)
        
        if data_final:
            queryset = queryset.filter(data__lte=data_final)
        
        return queryset