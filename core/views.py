from django.shortcuts import render

from django.views.generic import ListView
from .models import LogEntry

from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.shortcuts import redirect

from django.contrib import messages
from django.utils import timezone

# Importar tudo dos módulos reorganizados para manter compatibilidade
from .views.dashboard import *
from .views.logs import *
