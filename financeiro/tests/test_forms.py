from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from financeiro.forms import ContaPagarForm, ContaReceberForm
from comercial.models import Fornecedor, Cliente

import datetime

User = get_user_model()

class ContaPagarFormTest(TestCase):
    """Testes para o formulário de contas a pagar"""
    
    def setUp(self):
        # Criar um fornecedor para associar às contas
        self.fornecedor = Fornecedor.objects.create(
            nome="Fornecedor de Teste",
            cnpj="12.345.678/0001-90",
            email="fornecedor@teste.com",
            telefone="(11) 1234-5678"
        )
        
        # Data base para os testes
        self.hoje = timezone.now().date()
        self.amanha = self.hoje + datetime.timedelta(days=1)
        
        # Dados válidos para o formulário
        self.dados_validos = {
            'fornecedor': self.fornecedor.id,
            'valor': 500.00,
            'data_vencimento': self.amanha,
            'status': 'PENDENTE',
            'observacoes': "Conta de teste"
        }
    
    def test_form_valido(self):
        """Testa se o formulário é válido com dados corretos"""
        form = ContaPagarForm(self.dados_validos)
        self.assertTrue(form.is_valid())
    
    def test_form_invalido_fornecedor(self):
        """Testa se o formulário é inválido sem fornecedor"""
        dados_invalidos = self.dados_validos.copy()
        dados_invalidos['fornecedor'] = None
        form = ContaPagarForm(dados_invalidos)
        self.assertFalse(form.is_valid())
        self.assertIn('fornecedor', form.errors)
    
    def test_form_invalido_valor_negativo(self):
        """Testa se o formulário é inválido com valor negativo"""
        dados_invalidos = self.dados_validos.copy()
        dados_invalidos['valor'] = -100.00
        form = ContaPagarForm(dados_invalidos)
        self.assertFalse(form.is_valid())
        self.assertIn('valor', form.errors)
    
    def test_form_data_pagamento_status(self):
        """Testa se o formulário exige data de pagamento quando o status for PAGO"""
        dados_com_status_pago = self.dados_validos.copy()
        dados_com_status_pago['status'] = 'PAGO'
        
        # Sem data de pagamento
        form = ContaPagarForm(dados_com_status_pago)
        self.assertFalse(form.is_valid())
        self.assertIn('data_pagamento', form.errors)
        
        # Com data de pagamento
        dados_com_status_pago['data_pagamento'] = self.hoje
        form = ContaPagarForm(dados_com_status_pago)
        self.assertTrue(form.is_valid())


class ContaReceberFormTest(TestCase):
    """Testes para o formulário de contas a receber"""
    
    def setUp(self):
        # Criar um cliente para associar às contas
        self.cliente = Cliente.objects.create(
            nome="Cliente de Teste",
            email="cliente@teste.com",
            telefone="(11) 9876-5432"
        )
        
        # Data base para os testes
        self.hoje = timezone.now().date()
        self.amanha = self.hoje + datetime.timedelta(days=1)
        
        # Dados válidos para o formulário
        self.dados_validos = {
            'cliente': self.cliente.id,
            'valor': 800.00,
            'data_vencimento': self.amanha,
            'status': 'PENDENTE',
            'observacoes': "Conta de teste"
        }
    
    def test_form_valido(self):
        """Testa se o formulário é válido com dados corretos"""
        form = ContaReceberForm(self.dados_validos)
        self.assertTrue(form.is_valid())
    
    def test_form_invalido_cliente(self):
        """Testa se o formulário é inválido sem cliente"""
        dados_invalidos = self.dados_validos.copy()
        dados_invalidos['cliente'] = None
        form = ContaReceberForm(dados_invalidos)
        self.assertFalse(form.is_valid())
        self.assertIn('cliente', form.errors)
    
    def test_form_invalido_valor_negativo(self):
        """Testa se o formulário é inválido com valor negativo"""
        dados_invalidos = self.dados_validos.copy()
        dados_invalidos['valor'] = -100.00
        form = ContaReceberForm(dados_invalidos)
        self.assertFalse(form.is_valid())
        self.assertIn('valor', form.errors)
    
    def test_form_data_recebimento_status(self):
        """Testa se o formulário exige data de recebimento quando o status for RECEBIDO"""
        dados_com_status_recebido = self.dados_validos.copy()
        dados_com_status_recebido['status'] = 'RECEBIDO'
        
        # Sem data de recebimento
        form = ContaReceberForm(dados_com_status_recebido)
        self.assertFalse(form.is_valid())
        self.assertIn('data_recebimento', form.errors)
        
        # Com data de recebimento
        dados_com_status_recebido['data_recebimento'] = self.hoje
        form = ContaReceberForm(dados_com_status_recebido)
        self.assertTrue(form.is_valid())