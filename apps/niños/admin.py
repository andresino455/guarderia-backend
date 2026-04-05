from django.contrib import admin
from .models import Nino, TutorNino

@admin.register(Nino)
class NinoAdmin(admin.ModelAdmin):
    list_display  = ['id_nino', 'nombre', 'fecha_nacimiento', 'edad', 'activo']
    list_filter   = ['activo']
    search_fields = ['nombre']

@admin.register(TutorNino)
class TutorNinoAdmin(admin.ModelAdmin):
    list_display = ['id_nino', 'id_tutor', 'relacion', 'activo']

from .models import PersonaAutorizada


@admin.register(PersonaAutorizada)
class PersonaAutorizadaAdmin(admin.ModelAdmin):
    list_display = ["id_persona", "nombre", "ci", "telefono", "id_nino", "activo"]
    list_filter = ["activo"]
    search_fields = ["nombre", "ci", "id_nino__nombre"]
    # Ocultar código de seguridad en el admin
    exclude = ["codigo_seguridad"]
