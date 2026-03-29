# apps/usuarios/admin.py
from django.contrib import admin
from .models import Rol, Usuario

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ['id_rol', 'nombre', 'activo', 'created_at']
    list_filter = ['activo']

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['id_usuario', 'nombre', 'email', 'id_rol', 'activo']
    list_filter = ['activo', 'id_rol']
    search_fields = ['nombre', 'email']
    readonly_fields = ['password', 'created_at', 'updated_at']