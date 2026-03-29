from django.contrib import admin
from .models import Tutor, UsuarioTutor

@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display   = ['id_tutor', 'nombre', 'ci', 'telefono', 'email', 'activo']
    list_filter    = ['activo']
    search_fields  = ['nombre', 'ci', 'email']

@admin.register(UsuarioTutor)
class UsuarioTutorAdmin(admin.ModelAdmin):
    list_display = ['id_usuario', 'id_tutor', 'activo']