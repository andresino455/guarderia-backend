from django.contrib import admin
from .models import Asistencia

@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display  = ['id_asistencia', 'id_nino', 'fecha', 'hora_ingreso', 'hora_salida', 'estado']
    list_filter   = ['estado', 'fecha']
    search_fields = ['id_nino__nombre']
    date_hierarchy = 'fecha'