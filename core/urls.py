from django.urls import path
from .views import LogListView, limpar_log, CustomLoginView, CustomLogoutView, DashboardView
from django.contrib.auth.decorators import login_required

app_name = 'core'

urlpatterns = [
    # Autenticação
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    
    # Dashboard
    path('', login_required(DashboardView.as_view()), name='dashboard'),
    
    # Logs
    path('log/', login_required(LogListView.as_view()), name='log_list'),
    path('log/limpar/', login_required(limpar_log), name='log_clear'),
]
