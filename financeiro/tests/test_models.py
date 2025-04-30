from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from financeiro.models import ContaPagar, ContaReceber, Transacao
from comercial.models import Fornecedor, Cliente

import datetime

User = get_user_model()

class ContaPagarTest(TestCase):
    """Testes para o modelo ContaPagar"""
    
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
        self.ontem = self.hoje - datetime.timedelta(days=1)
        
        # Criar contas a pagar para testes
        self.conta_pendente = ContaPagar.objects.create(
            fornecedor=self.fornecedor,
            valor=500.00,
            data_vencimento=self.amanha,
            status='PENDENTE',
            observacoes="Conta pendente para teste"
        )
        
        self.conta_atrasada = ContaPagar.objects.create(
            fornecedor=self.fornecedor,
            valor=200.00,
            data_vencimento=self.ontem,
            status='PENDENTE',
            observacoes="Conta atrasada para teste"
        )
        
        self.conta_paga = ContaPagar.objects.create(
            fornecedor=self.fornecedor,
            valor=300.00,
            data_vencimento=self.ontem,
            status='PAGO',
            data_pagamento=self.hoje,
            observacoes="Conta paga para teste"
        )
    
    def test_criacao_conta_pagar(self):
        """Testa a criação de contas a pagar"""
        self.assertEqual(ContaPagar.objects.count(), 3)
        self.assertEqual(self.conta_pendente.valor, 500.00)
        self.assertEqual(self.conta_pendente.status, 'PENDENTE')
    
    def test_representacao_str(self):
        """Testa a representação em string da conta a pagar"""
        self.assertEqual(str(self.conta_pendente), f"{self.fornecedor} - R${self.conta_pendente.valor}")
    
    def test_vence_hoje(self):
        """Testa se a propriedade vence_hoje funciona corretamente"""
        # Criar uma conta que vence hoje
        conta_vence_hoje = ContaPagar.objects.create(
            fornecedor=self.fornecedor,
            valor=150.00,
            data_vencimento=self.hoje,
            status='PENDENTE'
        )
        
        # Testar propriedade vence_hoje
        self.assertTrue(conta_vence_hoje.vence_hoje)
        self.assertFalse(self.conta_pendente.vence_hoje)  # Vence amanhã
        self.assertFalse(self.conta_atrasada.vence_hoje)  # Venceu ontem
    
    def test_esta_atrasada(self):
        """Testa se a propriedade esta_atrasada funciona corretamente"""
        # Testar propriedade esta_atrasada
        self.assertTrue(self.conta_atrasada.esta_atrasada)  # Venceu ontem e está pendente
        self.assertFalse(self.conta_pendente.esta_atrasada)  # Vence amanhã
        self.assertFalse(self.conta_paga.esta_atrasada)  # Já foi paga
        
        # Criar uma conta que vence hoje não está atrasada (ainda)
        conta_vence_hoje = ContaPagar.objects.create(
            fornecedor=self.fornecedor,
            valor=150.00,
            data_vencimento=self.hoje,
            status='PENDENTE'
        )
        self.assertFalse(conta_vence_hoje.esta_atrasada)
    
    def test_atualizacao_status(self):
        """Testa a atualização do status da conta a pagar"""
        # Atualizar status de pendente para pago
        self.conta_pendente.status = 'PAGO'
        self.conta_pendente.data_pagamento = self.hoje
        self.conta_pendente.save()
        
        # Verificar atualização
        conta_atualizada = ContaPagar.objects.get(pk=self.conta_pendente.pk)
        self.assertEqual(conta_atualizada.status, 'PAGO')
        self.assertEqual(conta_atualizada.data_pagamento, self.hoje)


class ContaReceberTest(TestCase):
    """Testes para o modelo ContaReceber"""
    
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
        self.ontem = self.hoje - datetime.timedelta(days=1)
        
        # Criar contas a receber para testes
        self.conta_pendente = ContaReceber.objects.create(
            cliente=self.cliente,
            valor=800.00,
            data_vencimento=self.amanha,
            status='PENDENTE',
            observacoes="Conta pendente para teste"
        )
        
        self.conta_atrasada = ContaReceber.objects.create(
            cliente=self.cliente,
            valor=400.00,
            data_vencimento=self.ontem,
            status='PENDENTE',
            observacoes="Conta atrasada para teste"
        )
        
        self.conta_recebida = ContaReceber.objects.create(
            cliente=self.cliente,
            valor=600.00,
            data_vencimento=self.ontem,
            status='RECEBIDO',
            data_recebimento=self.hoje,
            observacoes="Conta recebida para teste"
        )
    
    def test_criacao_conta_receber(self):
        """Testa a criação de contas a receber"""
        self.assertEqual(ContaReceber.objects.count(), 3)
        self.assertEqual(self.conta_pendente.valor, 800.00)
        self.assertEqual(self.conta_pendente.status, 'PENDENTE')
    
    def test_representacao_str(self):
        """Testa a representação em string da conta a receber"""
        self.assertEqual(str(self.conta_pendente), f"{self.cliente} - R${self.conta_pendente.valor}")
    
    def test_vence_hoje(self):
        """Testa se a propriedade vence_hoje funciona corretamente"""
        # Criar uma conta que vence hoje
        conta_vence_hoje = ContaReceber.objects.create(
            cliente=self.cliente,
            valor=250.00,
            data_vencimento=self.hoje,
            status='PENDENTE'
        )
        
        # Testar propriedade vence_hoje
        self.assertTrue(conta_vence_hoje.vence_hoje)
        self.assertFalse(self.conta_pendente.vence_hoje)  # Vence amanhã
        self.assertFalse(self.conta_atrasada.vence_hoje)  # Venceu ontem
    
    def test_esta_atrasada(self):
        """Testa se a propriedade esta_atrasada funciona corretamente"""
        # Testar propriedade esta_atrasada
        self.assertTrue(self.conta_atrasada.esta_atrasada)  # Venceu ontem e está pendente
        self.assertFalse(self.conta_pendente.esta_atrasada)  # Vence amanhã
        self.assertFalse(self.conta_recebida.esta_atrasada)  # Já foi recebida
    
    def test_atualizacao_status(self):
        """Testa a atualização do status da conta a receber"""
        # Atualizar status de pendente para recebido
        self.conta_pendente.status = 'RECEBIDO'
        self.conta_pendente.data_recebimento = self.hoje
        self.conta_pendente.save()
        
        # Verificar atualização
        conta_atualizada = ContaReceber.objects.get(pk=self.conta_pendente.pk)
        self.assertEqual(conta_atualizada.status, 'RECEBIDO')
        self.assertEqual(conta_atualizada.data_recebimento, self.hoje)


class TransacaoTest(TestCase):
    """Testes para o modelo Transacao"""
    
    def setUp(self):
        # Criar um usuário responsável
        self.usuario = User.objects.create_user(
            username="financeiro", 
            password="senha123"
        )
        
        # Data base para os testes
        self.hoje = timezone.now().date()
        
        # Criar transações para testes
        self.receita = Transacao.objects.create(
            descricao="Venda de produtos",
            valor=1000.00,
            tipo='RECEITA',
            data=self.hoje,
            categoria='VENDAS',
            responsavel=self.usuario,
            observacoes="Receita teste"
        )
        
        self.despesa = Transacao.objects.create(
            descricao="Compra de matéria-prima",
            valor=600.00,
            tipo='DESPESA',
            data=self.hoje,
            categoria='COMPRAS',
            responsavel=self.usuario,
            observacoes="Despesa teste"
        )
    
    def test_criacao_transacao(self):
        """Testa a criação de transações"""
        self.assertEqual(Transacao.objects.count(), 2)
        self.assertEqual(self.receita.valor, 1000.00)
        self.assertEqual(self.receita.tipo, 'RECEITA')
        self.assertEqual(self.despesa.valor, 600.00)
        self.assertEqual(self.despesa.tipo, 'DESPESA')
    
    def test_representacao_str(self):
        """Testa a representação em string da transação"""
        self.assertEqual(str(self.receita), f"Venda de produtos - R${self.receita.valor}")
        self.assertEqual(str(self.despesa), f"Compra de matéria-prima - R${self.despesa.valor}")
    
    def test_calculo_saldo(self):
        """Testa o cálculo de saldo"""
        # O saldo deve ser: receita (1000) - despesa (600) = 400
        saldo = Transacao.get_saldo()
        self.assertEqual(saldo, 400.00)
        
        # Adicionar mais uma receita
        Transacao.objects.create(
            descricao="Receita extra",
            valor=200.00,
            tipo='RECEITA',
            data=self.hoje,
            categoria='OUTROS',
            responsavel=self.usuario
        )
        
        # O saldo deve ser atualizado: receitas (1000 + 200) - despesa (600) = 600
        novo_saldo = Transacao.get_saldo()
        self.assertEqual(novo_saldo, 600.00)
        
        # Adicionar mais uma despesa
        Transacao.objects.create(
            descricao="Despesa extra",
            valor=100.00,
            tipo='DESPESA',
            data=self.hoje,
            categoria='OUTROS',
            responsavel=self.usuario
        )
        
        # O saldo deve ser atualizado: receitas (1000 + 200) - despesas (600 + 100) = 500
        novo_saldo = Transacao.get_saldo()
        self.assertEqual(novo_saldo, 500.00)