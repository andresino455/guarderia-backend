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
]
