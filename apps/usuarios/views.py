# apps/usuarios/views.py
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Rol, Usuario
from .serializers import (
    RolSerializer, UsuarioSerializer,
    UsuarioListSerializer, CambiarPasswordSerializer, LoginSerializer
)
from .permissions import IsAdmin, IsAdminOrSelf


# ─── Utilidad ────────────────────────────────────────────────────────────────

def get_tokens_for_user(usuario):
    """Genera access + refresh token para un Usuario personalizado."""
    refresh = RefreshToken()
    refresh['user_id'] = usuario.id_usuario
    refresh['email'] = usuario.email
    refresh['nombre'] = usuario.nombre
    refresh['rol'] = usuario.id_rol.nombre if usuario.id_rol else None
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# ─── Auth ─────────────────────────────────────────────────────────────────────

class LoginView(generics.GenericAPIView):
    """POST /api/v1/auth/login/  →  { access, refresh, usuario }"""
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            usuario = Usuario.objects.select_related('id_rol').get(
                email=email, activo=True
            )
        except Usuario.DoesNotExist:
            return Response(
                {'detail': 'Credenciales inválidas.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not check_password(password, usuario.password):
            return Response(
                {'detail': 'Credenciales inválidas.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        tokens = get_tokens_for_user(usuario)
        return Response({
            **tokens,
            'usuario': UsuarioListSerializer(usuario).data
        }, status=status.HTTP_200_OK)


# ─── Roles ────────────────────────────────────────────────────────────────────

class RolViewSet(viewsets.ModelViewSet):
    """CRUD completo de roles. Solo admin."""
    queryset = Rol.objects.filter(activo=True).order_by('nombre')
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
    queryset = Usuario.objects.select_related('id_rol').filter(activo=True)
    permission_classes = [IsAuthenticated, IsAdminOrSelf]

    def get_permissions(self):
        # Permitir crear usuario sin token (solo para setup inicial)
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminOrSelf()]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UsuarioListSerializer
        return UsuarioSerializer

    def destroy(self, request, *args, **kwargs):
        # Soft delete
        usuario = self.get_object()
        usuario.activo = False
        usuario.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """GET /api/v1/usuarios/me/  →  perfil del usuario autenticado."""
        # Extraer id del token JWT
        user_id = request.auth.payload.get('user_id')
        try:
            usuario = Usuario.objects.select_related('id_rol').get(
                id_usuario=user_id, activo=True
            )
        except Usuario.DoesNotExist:
            return Response({'detail': 'Usuario no encontrado.'}, status=404)
        return Response(UsuarioListSerializer(usuario).data)

    @action(detail=True, methods=['post'], url_path='cambiar-password')
    def cambiar_password(self, request, pk=None):
        """POST /api/v1/usuarios/{id}/cambiar-password/"""
        usuario = self.get_object()
        serializer = CambiarPasswordSerializer(
            data=request.data,
            context={'request': request, 'user_obj': usuario}
        )
        # Inyectamos el usuario en el contexto para la validación
        serializer.context['request'].user_obj = usuario
        serializer.is_valid(raise_exception=True)
        usuario.password = serializer.validated_data['password_nueva']
        usuario.save()
        return Response({'detail': 'Contraseña actualizada correctamente.'})

    @action(detail=True, methods=['patch'], url_path='activar')
    def activar(self, request, pk=None):
        """PATCH /api/v1/usuarios/{id}/activar/  →  reactiva un usuario."""
        usuario = self.get_object()
        usuario.activo = True
        usuario.save()
        return Response({'detail': 'Usuario activado.'})