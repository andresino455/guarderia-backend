# guarderia_backend/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    # Auth JWT
    path("api/v1/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Apps
    path("api/v1/usuarios/", include("apps.usuarios.urls")),
    path("api/v1/tutores/", include("apps.tutores.urls")),
    path("api/v1/ninos/", include("apps.ninos.urls")),
    path("api/v1/salas/", include("apps.salas.urls")),
    path("api/v1/servicios/", include("apps.servicios.urls")),
    path("api/v1/asistencia/", include("apps.asistencia.urls")),
    path("api/v1/salud/", include("apps.salud.urls")),
    path("api/v1/actividades/", include("apps.actividades.urls")),
    path("api/v1/comunicacion/", include("apps.comunicacion.urls")),
    path("api/v1/camaras/", include("apps.camaras.urls")),
    path("api/v1/guarderias/", include("apps.guarderias.urls")),
    path("api/v1/auditoria/", include("apps.auditoria.urls")),
    path("api/v1/backup/", include("apps.backup.urls")),
    path("api/v1/reportes/", include("apps.reportes.urls")),
]

from django.http import JsonResponse
from django.contrib.auth.hashers import check_password


def debug_usuario(request):
    from apps.usuarios.models import Usuario
    from django.contrib.auth.hashers import check_password, make_password
    from apps.guarderias.models import Guarderia

    email = request.GET.get("email", "admin@guarderia.com")
    resetear = request.GET.get("reset", "false") == "true"

    u = Usuario.objects.filter(email=email).first()
    if not u:
        return JsonResponse({"error": "Usuario no encontrado"})

    if resetear:
        # Obtener la primera guardería disponible
        guarderia = Guarderia.objects.filter(activo=True).first()

        # Usar update() para bypassear el save() del modelo
        Usuario.objects.filter(email=email).update(
            password=make_password("Admin1234!"),
            id_guarderia=guarderia,
            activo=True,
        )
        u.refresh_from_db()

    return JsonResponse(
        {
            "encontrado": True,
            "nombre": u.nombre,
            "email": u.email,
            "activo": u.activo,
            "password_empieza_con": u.password[:20],
            "rol": u.id_rol.nombre if u.id_rol else None,
            "guarderia": u.id_guarderia_id,
            "check_Admin1234": check_password("Admin1234!", u.password),
        }
    )

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def debug_tenant(request):
    """
    GET /api/v1/debug-tenant/
    Muestra qué guardería tiene el request actual.
    Eliminar en producción.
    """
    guarderia = getattr(request, "guarderia", None)
    usuario = getattr(request, "user", None)

    return Response(
        {
            "usuario_id": getattr(usuario, "id_usuario", None),
            "usuario_email": getattr(usuario, "email", None),
            "usuario_guarderia_id": getattr(usuario, "id_guarderia_id", None),
            "request_guarderia": str(guarderia) if guarderia else None,
            "request_guarderia_id": guarderia.id_guarderia if guarderia else None,
        }
    )


urlpatterns += [
    path("debug-usuario/", debug_usuario),
    path("api/v1/debug-tenant/", debug_tenant),
]
