from django.contrib import admin
from .models import Actividad


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display   = ['id_actividad', 'id_nino', 'tipo', 'descripcion', 'fecha', 'activo']
    list_filter    = ['tipo', 'activo']
    search_fields  = ['id_nino__nombre', 'descripcion']
    date_hierarchy = 'fecha'