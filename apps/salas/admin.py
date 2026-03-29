from django.contrib import admin
from .models import Personal, Sala, PersonalSala, AsignacionNinoSala


@admin.register(Personal)
class PersonalAdmin(admin.ModelAdmin):
    list_display  = ['id_personal', 'nombre', 'telefono', 'tipo', 'activo']
    list_filter   = ['tipo', 'activo']
    search_fields = ['nombre']


class PersonalSalaInline(admin.TabularInline):
    model  = PersonalSala
    extra  = 0
    fields = ['id_personal', 'activo']


class AsignacionInline(admin.TabularInline):
    model  = AsignacionNinoSala
    extra  = 0
    fields = ['id_nino', 'fecha', 'activo']


@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ['id_sala', 'nombre', 'edad_min', 'edad_max', 'cupo_max', 'activo']
    list_filter  = ['activo']
    inlines      = [PersonalSalaInline, AsignacionInline]


@admin.register(AsignacionNinoSala)
class AsignacionAdmin(admin.ModelAdmin):
    list_display  = ['id_asignacion', 'id_nino', 'id_sala', 'fecha', 'activo']
    list_filter   = ['activo', 'id_sala']
    search_fields = ['id_nino__nombre']