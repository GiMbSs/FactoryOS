from django import forms
from .models import Cliente, Venda, Fornecedor, ItemVenda

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'tipo', 'cnpj_cpf', 'email', 'telefone', 'endereco']
        widgets = {
            'telefone': forms.TextInput(attrs={'placeholder': '(00) 00000-0000'}),
            'cnpj_cpf': forms.TextInput(attrs={
                'placeholder': '00.000.000/0000-00 ou 000.000.000-00',
                'data-mask': '00.000.000/0000-00'
            }),
            'endereco': forms.Textarea(attrs={'rows': 3})
        }

class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = ['nome', 'cnpj', 'email', 'telefone']
        widgets = {
            'telefone': forms.TextInput(attrs={'placeholder': '(00) 00000-0000'}),
            'cnpj': forms.TextInput(attrs={'placeholder': '00.000.000/0000-00'}),
        }

class ItemVendaForm(forms.ModelForm):
    class Meta:
        model = ItemVenda
        fields = ['produto', 'quantidade', 'preco_unitario']
        widgets = {
            'produto': forms.Select(attrs={'class': 'form-select'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'preco_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class VendaForm(forms.ModelForm):
    class Meta:
        model = Venda
        fields = ['cliente', 'vendedor', 'valor_total', 'status', 'observacoes']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'vendedor': forms.Select(attrs={'class': 'form-select'}),
            'valor_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
