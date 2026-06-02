from django.contrib import admin
from .models import Guarderia


@admin.register(Guarderia)
class GuarderiaAdmin(admin.ModelAdmin):
    list_display = [
        "id_guarderia",
        "nombre",
        "telefono",
        "email",
        "activo",
        "created_at",
    ]
    list_filter = ["activo"]
    search_fields = ["nombre", "email", "telefono"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        (
            "Información general",
            {"fields": ("nombre", "direccion", "telefono", "email", "logo")},
        ),
        ("Estado", {"fields": ("activo",)}),
        ("Fechas", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
