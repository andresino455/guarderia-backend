from django.contrib import admin
from .models import Mensaje, Notificacion


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display  = ['id_mensaje', 'id_emisor', 'id_receptor', 'fecha', 'activo']
    list_filter   = ['activo']
    search_fields = ['id_emisor__nombre', 'id_receptor__nombre']


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display  = ['id_notificacion', 'id_usuario', 'mensaje', 'leido', 'fecha']
    list_filter   = ['leido', 'activo']
    search_fields = ['id_usuario__nombre', 'mensaje']