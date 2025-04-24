from django.urls import path
from .views import LogListView, limpar_log

app_name = 'core'

urlpatterns = [
    path('log/', LogListView.as_view(), name='log_list'),
    path('log/limpar/', limpar_log, name='log_clear'),
]
