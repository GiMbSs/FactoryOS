from django.contrib import admin
from .models import LogEntry

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['data', 'modulo', 'acao', 'usuario']
    list_filter = ['modulo', 'data']
    search_fields = ['modulo', 'acao', 'usuario__username']
    date_hierarchy = 'data'
    readonly_fields = ['data', 'modulo', 'acao', 'usuario']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
