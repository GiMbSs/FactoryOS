from django.urls import path
from .views import (
    DashboardView,
    ContaPagarListView, ContaPagarCreateView, ContaPagarDeleteView, ContaPagarUpdateView, RegistrarPagamentoView,
    ContaReceberListView, ContaReceberCreateView, ContaReceberDeleteView, ContaReceberUpdateView, RegistrarRecebimentoView
)

app_name = 'financeiro'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('contas-pagar/', ContaPagarListView.as_view(), name='conta_pagar_list'),
    path('contas-pagar/nova/', ContaPagarCreateView.as_view(), name='conta_pagar_create'),
    path('contas-pagar/editar/<int:pk>/', ContaPagarUpdateView.as_view(), name='conta_pagar_update'),
    path('contas-pagar/excluir/<int:pk>/', ContaPagarDeleteView.as_view(), name='conta_pagar_delete'),
    path('contas-pagar/pagar/<int:pk>/', RegistrarPagamentoView.as_view(), name='conta_pagar_pagar'),
    path('contas-receber/', ContaReceberListView.as_view(), name='conta_receber_list'),
    path('contas-receber/nova/', ContaReceberCreateView.as_view(), name='conta_receber_create'),
    path('contas-receber/editar/<int:pk>/', ContaReceberUpdateView.as_view(), name='conta_receber_update'),
    path('contas-receber/excluir/<int:pk>/', ContaReceberDeleteView.as_view(), name='conta_receber_delete'),
    path('contas-receber/receber/<int:pk>/', RegistrarRecebimentoView.as_view(), name='conta_receber_receber'),
]
