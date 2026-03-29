from django.contrib import admin
from .models import Bitacora, HistorialCambios


@admin.register(Bitacora)
class BitacoraAdmin(admin.ModelAdmin):
    list_display   = ['id_bitacora', 'id_usuario', 'accion', 'tabla', 'id_registro', 'fecha']
    list_filter    = ['accion', 'tabla']
    search_fields  = ['tabla', 'descripcion']
    date_hierarchy = 'fecha'
    readonly_fields = ['id_bitacora', 'id_usuario', 'accion', 'tabla', 'id_registro', 'fecha', 'descripcion']


@admin.register(HistorialCambios)
class HistorialCambiosAdmin(admin.ModelAdmin):
    list_display  = ['id_historial', 'tabla', 'id_registro', 'campo', 'fecha']
    list_filter   = ['tabla', 'campo']
    search_fields = ['tabla', 'campo']
    readonly_fields = list_display