# apps/usuarios/views.py
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Rol, Usuario
from .serializers import (
    RolSerializer,
    UsuarioSerializer,
    UsuarioListSerializer,
    CambiarPasswordSerializer,
    LoginSerializer,
)
from .permissions import IsAdmin, IsAdminOrSelf

# ─── Utilidad ────────────────────────────────────────────────────────────────

from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(usuario):
    refresh = RefreshToken()
    refresh["user_id"] = usuario.id_usuario
    refresh["email"] = usuario.email
    refresh["nombre"] = usuario.nombre
    refresh["rol"] = usuario.id_rol.nombre if usuario.id_rol else None
    refresh["id_guarderia"] = usuario.id_guarderia_id
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


# ─── Auth ─────────────────────────────────────────────────────────────────────


from django.core.cache import cache
from django.utils import timezone

class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        # ── Claves de cache ───────────────────────────────────────
        cache_intentos = f"login_intentos_{email}"
        cache_bloqueado = f"login_bloqueado_{email}"

        # ── Verificar si está bloqueado ───────────────────────────
        bloqueado_hasta = cache.get(cache_bloqueado)
        if bloqueado_hasta:
            segundos_restantes = int(bloqueado_hasta - timezone.now().timestamp())
            if segundos_restantes > 0:
                minutos = segundos_restantes // 60
                segundos = segundos_restantes % 60
                return Response(
                    {
                        "detail": f"Cuenta bloqueada por demasiados intentos fallidos. "
                        f"Intentá de nuevo en {minutos}m {segundos}s.",
                        "bloqueado": True,
                        "segundos_restantes": segundos_restantes,
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )
            else:
                # El bloqueo expiró, limpiar
                cache.delete(cache_bloqueado)
                cache.delete(cache_intentos)

        # ── Verificar credenciales ────────────────────────────────
        try:
            usuario = Usuario.objects.select_related("id_rol").get(
                email=email, activo=True
            )
        except Usuario.DoesNotExist:
            # No revelar si el usuario existe o no
            self._registrar_intento_fallido(cache_intentos, cache_bloqueado, email)
            intentos = cache.get(cache_intentos, 0)
            return Response(
                self._respuesta_fallida(intentos),
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not check_password(password, usuario.password):
            self._registrar_intento_fallido(cache_intentos, cache_bloqueado, email)
            intentos = cache.get(cache_intentos, 0)
            return Response(
                self._respuesta_fallida(intentos),
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # ── Login exitoso → limpiar intentos ─────────────────────
        cache.delete(cache_intentos)
        cache.delete(cache_bloqueado)

        tokens = get_tokens_for_user(usuario)
        return Response(
            {
                **tokens,
                "usuario": UsuarioListSerializer(usuario).data,
                "guarderia": {
                    "id_guarderia": usuario.id_guarderia_id,
                    "nombre": (
                        usuario.id_guarderia.nombre if usuario.id_guarderia else None
                    ),
                },
            },
            status=status.HTTP_200_OK,
        )

    def _registrar_intento_fallido(self, cache_intentos, cache_bloqueado, email):
        intentos = cache.get(cache_intentos, 0) + 1
        cache.set(cache_intentos, intentos, timeout=300)  # 5 min

        if intentos >= 3:
            # Guardar timestamp de cuando expira el bloqueo
            expira = timezone.now().timestamp() + 300  # 5 min
            cache.set(cache_bloqueado, expira, timeout=300)
            cache.delete(cache_intentos)

    def _respuesta_fallida(self, intentos):
        restantes = max(0, 3 - intentos)
        if intentos >= 3:
            return {
                "detail": "Cuenta bloqueada por 5 minutos por demasiados intentos fallidos.",
                "bloqueado": True,
                "segundos_restantes": 300,
            }
        return {
            "detail": f"Credenciales inválidas. Te quedan {restantes} intento{'s' if restantes != 1 else ''}.",
            "bloqueado": False,
            "intentos_restantes": restantes,
        }


# ─── Roles ────────────────────────────────────────────────────────────────────


class RolViewSet(viewsets.ModelViewSet):
    """CRUD completo de roles. Solo admin."""

    queryset = Rol.objects.filter(activo=True).order_by("nombre")
    serializer_class = RolSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def destroy(self, request, *args, **kwargs):
        # Soft delete en lugar de borrar físicamente
        rol = self.get_object()
        rol.activo = False
        rol.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─── Usuarios ─────────────────────────────────────────────────────────────────


class UsuarioViewSet(viewsets.ModelViewSet):
    """CRUD de usuarios con acciones adicionales."""

    queryset = Usuario.objects.select_related("id_rol").filter(activo=True)
    permission_classes = [IsAuthenticated, IsAdminOrSelf]

    def get_permissions(self):
        # Permitir crear usuario sin token (solo para setup inicial)
        if self.action == "create":
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminOrSelf()]

    def get_serializer_class(self):
        if self.action == "list":
            return UsuarioListSerializer
        return UsuarioSerializer

    def destroy(self, request, *args, **kwargs):
        # Hard delete: Borra el registro físicamente
        usuario = self.get_object()
        usuario.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        """GET /api/v1/usuarios/me/ — perfil del usuario autenticado."""
        return Response(UsuarioListSerializer(request.user).data)

    @action(detail=True, methods=["post"], url_path="cambiar-password")
    def cambiar_password(self, request, pk=None):
        usuario = self.get_object()
        serializer = CambiarPasswordSerializer(
            data=request.data, context={"request": request, "user_obj": usuario}
        )
        serializer.context["request"].user_obj = usuario
        serializer.is_valid(raise_exception=True)
        usuario.password = serializer.validated_data["password_nueva"]
        usuario.save()
        return Response({"detail": "Contraseña actualizada correctamente."})

    @action(detail=True, methods=["patch"], url_path="activar")
    def activar(self, request, pk=None):
        """PATCH /api/v1/usuarios/{id}/activar/  →  reactiva un usuario."""
        usuario = self.get_object()
        usuario.activo = True
        usuario.save()
        return Response({"detail": "Usuario activado."})
