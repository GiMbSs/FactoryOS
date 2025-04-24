from django.db import models

class LogEntry(models.Model):
    modulo = models.CharField(max_length=100)
    acao = models.CharField(max_length=255)
    usuario = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='core_logentry_set')
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.data:%d/%m/%Y %H:%M}] {self.modulo}: {self.acao} por {self.usuario}"
