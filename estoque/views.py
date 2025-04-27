from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from core.views import registrar_log
from django.urls import reverse_lazy
from django.contrib import messages
from producao.models import MateriaPrima
from .models import SaldoEstoque, ProdutoEstoque
from .forms import SaldoEstoqueForm, MateriaPrimaForm

from producao.models import Produto

class EstoqueListView(TemplateView):
    template_name = 'estoque/estoque_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['materias_primas'] = MateriaPrima.objects.all()
        produtos = Produto.objects.all()
        produtos_com_estoque = []
        for produto in produtos:
            try:
                saldo = ProdutoEstoque.objects.get(produto=produto)
                quantidade = saldo.quantidade_atual
            except ProdutoEstoque.DoesNotExist:
                quantidade = 0
            produtos_com_estoque.append({
                'produto': produto,
                'quantidade_estoque': quantidade
            })
        context['produtos_acabados'] = produtos_com_estoque
        return context


class SaldoEstoqueUpdateView(UpdateView):
    model = SaldoEstoque
    form_class = SaldoEstoqueForm
    template_name = 'estoque/cadastro_material.html'
    success_url = reverse_lazy('estoque:estoque_list')

class SaldoEstoqueDeleteView(DeleteView):
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        response = super().delete(request, *args, **kwargs)
        registrar_log(request, 'Estoque', f'Excluiu saldo de material: {obj.materia_prima}')
        messages.success(self.request, 'Material excluído com sucesso!')
        return response
    model = SaldoEstoque
    template_name = 'estoque/confirmar_exclusao_material.html'
    success_url = reverse_lazy('estoque:estoque_list')

from django.views.generic.edit import CreateView, UpdateView, DeleteView

class MateriaPrimaCreateView(CreateView):
    model = MateriaPrima
    form_class = MateriaPrimaForm
    template_name = 'estoque/cadastro_materiaprima.html'
    success_url = reverse_lazy('estoque:estoque_list')

class MateriaPrimaUpdateView(UpdateView):
    model = MateriaPrima
    form_class = MateriaPrimaForm
    template_name = 'estoque/cadastro_materiaprima.html'
    success_url = reverse_lazy('estoque:estoque_list')

    def get_initial(self):
        initial = super().get_initial()
        try:
            saldo = self.object.saldoestoque
            initial['quantidade_estoque'] = saldo.quantidade_atual
        except Exception:
            initial['quantidade_estoque'] = 0
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        quantidade = form.cleaned_data.get('quantidade_estoque')
        if quantidade is not None:
            from .models import SaldoEstoque
            saldo, _ = SaldoEstoque.objects.get_or_create(materia_prima=self.object)
            saldo.quantidade_atual = quantidade
            saldo.save()
        registrar_log(self.request, 'Estoque', f'Editou matéria-prima: {self.object.nome}')
        return response


class MateriaPrimaDeleteView(DeleteView):
    model = MateriaPrima
    template_name = 'estoque/confirmar_exclusao_materiaprima.html'
    success_url = reverse_lazy('estoque:estoque_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        materia_prima = self.get_object()
        
        # Verificar se a matéria-prima está em uso em produtos
        from producao.models import ProdutoMateriaPrima
        produtos_usando = ProdutoMateriaPrima.objects.filter(materia_prima=materia_prima)
        context['produtos_usando'] = produtos_usando
        
        # Verificar se há movimentações de estoque para esta matéria-prima
        from estoque.models import MovimentacaoEstoque
        movimentacoes = MovimentacaoEstoque.objects.filter(materia_prima=materia_prima).count()
        context['movimentacoes'] = movimentacoes
        
        return context

    def post(self, request, *args, **kwargs):
        materia_prima = self.get_object()
        
        # Verificar se a matéria-prima está em uso
        from producao.models import ProdutoMateriaPrima
        produtos_usando = ProdutoMateriaPrima.objects.filter(materia_prima=materia_prima).exists()
        
        if produtos_usando:
            messages.error(request, f'Não é possível excluir a matéria-prima "{materia_prima.nome}" pois ela está sendo usada em produtos.')
            return redirect('estoque:estoque_list')
        
        # Verificar se há movimentações de estoque
        from estoque.models import MovimentacaoEstoque
        movimentacoes = MovimentacaoEstoque.objects.filter(materia_prima=materia_prima).exists()
        
        if movimentacoes:
            messages.error(request, f'Não é possível excluir a matéria-prima "{materia_prima.nome}" pois existem movimentações de estoque registradas.')
            return redirect('estoque:estoque_list')
        
        return super().post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        response = super().delete(request, *args, **kwargs)
        registrar_log(request, 'Estoque', f'Excluiu matéria-prima: {obj.nome}')
        messages.success(request, f'Matéria-prima "{obj.nome}" excluída com sucesso!')
        return response

class SaldoEstoqueDeleteView(DeleteView):
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        response = super().delete(request, *args, **kwargs)
        registrar_log(request, 'Estoque', f'Excluiu saldo de material: {obj.materia_prima}')
        return response
    model = SaldoEstoque
    template_name = 'estoque/confirmar_exclusao_material.html'
    success_url = reverse_lazy('estoque:estoque_list')

class DashboardView(TemplateView):
    template_name = 'estoque/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.db.models import Sum, F, ExpressionWrapper, DecimalField, Q, Count
        from django.utils import timezone
        from datetime import timedelta
        from producao.models import MateriaPrima
        from .models import SaldoEstoque, MovimentacaoEstoque
        
        # Todas as matérias-primas
        materias_primas = MateriaPrima.objects.all()
        context['materias_primas'] = materias_primas
        
        # Calcular valor total em estoque
        valor_total = SaldoEstoque.objects.annotate(
            valor_item=ExpressionWrapper(
                F('quantidade_atual') * F('materia_prima__custo_unitario'),
                output_field=DecimalField()
            )
        ).aggregate(total=Sum('valor_item'))['total'] or 0
        context['valor_total_estoque'] = valor_total
        
        # Itens abaixo do estoque mínimo
        itens_criticos = []
        itens_abaixo_minimo = 0
        itens_sem_estoque = 0
        
        for materia in materias_primas:
            try:
                saldo = SaldoEstoque.objects.get(materia_prima=materia)
                quantidade_atual = saldo.quantidade_atual
            except SaldoEstoque.DoesNotExist:
                quantidade_atual = 0
                
            if quantidade_atual <= 0:
                itens_sem_estoque += 1
                itens_criticos.append(materia)
            elif quantidade_atual <= materia.estoque_minimo:
                itens_abaixo_minimo += 1
                itens_criticos.append(materia)
        
        context['itens_abaixo_minimo'] = itens_abaixo_minimo
        context['itens_sem_estoque'] = itens_sem_estoque
        context['materias_criticas'] = itens_criticos
        
        # Dados para gráficos (em um ambiente real, estes dados viriam do banco)
        # Aqui estamos apenas preparando a estrutura para o template
        
        # Dados para movimentações recentes (6 meses)
        meses = []
        entradas = []
        saidas = []
        
        for i in range(5, -1, -1):
            data_inicio = timezone.now() - timedelta(days=30 * i + 30)
            data_fim = timezone.now() - timedelta(days=30 * i)
            mes = data_fim.strftime('%b')
            meses.append(mes)
            
            entrada = MovimentacaoEstoque.objects.filter(
                data__gte=data_inicio,
                data__lt=data_fim,
                tipo_movimento='ENTRADA'
            ).count()
            
            saida = MovimentacaoEstoque.objects.filter(
                data__gte=data_inicio,
                data__lt=data_fim,
                tipo_movimento='SAIDA'
            ).count()
            
            entradas.append(entrada)
            saidas.append(saida)
        
        context['dados_movimentacoes'] = {
            'meses': meses,
            'entradas': entradas,
            'saidas': saidas
        }
        
        # Registrar acesso ao dashboard no log
        registrar_log(self.request, 'Estoque', 'Acessou o dashboard de estoque')
        
        return context
