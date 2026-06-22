from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db import transaction

from .models import Guarderia
from .serializers import GuarderiaSerializer


class GuarderiaViewSet(viewsets.ModelViewSet):
    queryset = Guarderia.objects.filter(activo=True)
    serializer_class = GuarderiaSerializer

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [IsAuthenticated()]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        POST /api/v1/guarderias/
        Registro público. Crea:
          1. La guardería
          2. Los roles base (Administrador, Personal, Tutor)
          3. El usuario administrador inicial
          4. Retorna tokens JWT listos para usar
        """
        from apps.usuarios.models import Rol, Usuario
        from apps.usuarios.views import get_tokens_for_user
        from django.contrib.auth.hashers import make_password

        # ── Validar datos de la guardería ─────────────────────────────────
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # ── Validar datos del admin ───────────────────────────────────────
        admin_nombre = request.data.get("admin_nombre", "").strip()
        admin_email = request.data.get("admin_email", "").strip()
        admin_password = request.data.get("admin_password", "").strip()

        errores = {}
        if not admin_nombre:
            errores["admin_nombre"] = "El nombre del administrador es obligatorio."
        if not admin_email:
            errores["admin_email"] = "El email del administrador es obligatorio."
        if not admin_password or len(admin_password) < 8:
            errores["admin_password"] = (
                "La contraseña debe tener al menos 8 caracteres."
            )
        if Usuario.objects.filter(email=admin_email).exists():
            errores["admin_email"] = "Ya existe un usuario con ese email."

        if errores:
            return Response(errores, status=status.HTTP_400_BAD_REQUEST)

        # ── Crear guardería ───────────────────────────────────────────────
        guarderia = serializer.save()

        # ── Crear roles base para esta guardería ──────────────────────────
        roles_base = ["Administrador", "Personal", "Tutor"]
        roles_creados = {}
        for nombre in roles_base:
            rol = Rol.objects.create(
                nombre=nombre,
                id_guarderia=guarderia,
                activo=True,
            )
            roles_creados[nombre] = rol

        # ── Crear usuario admin ───────────────────────────────────────────
        usuario = Usuario.objects.create(
            nombre=admin_nombre,
            email=admin_email,
            password=make_password(admin_password),
            id_rol=roles_creados["Administrador"],
            id_guarderia=guarderia,
            activo=True,
        )

        # ── Retornar tokens + info ────────────────────────────────────────
        tokens = get_tokens_for_user(usuario)

        return Response(
            {
                **tokens,
                "guarderia": GuarderiaSerializer(guarderia).data,
                "usuario": {
                    "id_usuario": usuario.id_usuario,
                    "nombre": usuario.nombre,
                    "email": usuario.email,
                    "rol_nombre": "Administrador",
                },
                "mensaje": f'Guardería "{guarderia.nombre}" creada correctamente.',
            },
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, *args, **kwargs):
        """Soft delete."""
        g = self.get_object()
        g.activo = False
        g.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="mi-guarderia")
    def mi_guarderia(self, request):
        """GET /api/v1/guarderias/mi-guarderia/ — info de la guardería actual."""
        guarderia = getattr(request, "guarderia", None)
        if not guarderia:
            return Response(
                {"detail": "No tenés guardería asignada."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(GuarderiaSerializer(guarderia).data)

    @action(detail=True, methods=["patch"], url_path="configuracion")
    def configuracion(self, request, pk=None):
        """PATCH /api/v1/guarderias/{id}/configuracion/ — actualizar datos."""
        guarderia = self.get_object()

        # Solo el admin de esa guardería puede modificarla
        if request.guarderia != guarderia:
            return Response(
                {"detail": "No tenés permiso para modificar esta guardería."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(guarderia, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
