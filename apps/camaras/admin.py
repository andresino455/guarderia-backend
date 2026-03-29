from django.contrib import admin
from .models import Camara


@admin.register(Camara)
class CamaraAdmin(admin.ModelAdmin):
    list_display  = ['id_camara', 'id_sala', 'url_stream', 'activo']
    list_filter   = ['activo', 'id_sala']