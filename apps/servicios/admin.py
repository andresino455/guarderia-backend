from django.contrib import admin
from .models import Servicio, NinoServicio, Pago, DetallePago


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display  = ['id_servicio', 'nombre', 'precio', 'tipo', 'activo']
    list_filter   = ['tipo', 'activo']
    search_fields = ['nombre']


@admin.register(NinoServicio)
class NinoServicioAdmin(admin.ModelAdmin):
    list_display = ['id_nino', 'id_servicio', 'activo']
    list_filter  = ['activo']


class DetallePagoInline(admin.TabularInline):
    model  = DetallePago
    extra  = 0
    fields = ['id_servicio', 'monto', 'activo']


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display   = ['id_pago', 'id_nino', 'fecha', 'total', 'estado', 'activo']
    list_filter    = ['estado', 'activo']
    search_fields  = ['id_nino__nombre']
    date_hierarchy = 'fecha'
    inlines        = [DetallePagoInline]


@admin.register(DetallePago)
class DetallePagoAdmin(admin.ModelAdmin):
    list_display = ['id_detalle', 'id_pago', 'id_servicio', 'monto']