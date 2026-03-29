from django.contrib import admin
from .models import Salud, Medicacion, Alimentacion

@admin.register(Salud)
class SaludAdmin(admin.ModelAdmin):
    list_display  = ['id_salud', 'id_nino', 'fecha', 'sintomas']
    list_filter   = ['fecha']
    search_fields = ['id_nino__nombre', 'sintomas']
    date_hierarchy = 'fecha'

@admin.register(Medicacion)
class MedicacionAdmin(admin.ModelAdmin):
    list_display  = ['id_medicacion', 'id_nino', 'medicamento', 'dosis', 'hora', 'activo']
    list_filter   = ['activo']
    search_fields = ['id_nino__nombre', 'medicamento']

@admin.register(Alimentacion)
class AlimentacionAdmin(admin.ModelAdmin):
    list_display  = ['id_alimentacion', 'id_nino', 'tipo_comida', 'horario', 'activo']
    search_fields = ['id_nino__nombre', 'tipo_comida']