# apps/usuarios/permissions.py
from rest_framework.permissions import BasePermission


def get_usuario_from_token(request):
    """Extrae el rol del payload del JWT."""
    if not request.auth:
        return None, None
    payload = request.auth.payload
    return payload.get('user_id'), payload.get('rol')


class IsAdmin(BasePermission):
    """Solo usuarios con rol 'Administrador'."""
    def has_permission(self, request, view):
        _, rol = get_usuario_from_token(request)
        return rol == 'Administrador'


class IsPersonal(BasePermission):
    """Solo personal de la guardería."""
    def has_permission(self, request, view):
        _, rol = get_usuario_from_token(request)
        return rol in ('Administrador', 'Personal')


class IsTutor(BasePermission):
    """Padres/tutores accediendo a sus propios datos."""
    def has_permission(self, request, view):
        _, rol = get_usuario_from_token(request)
        return rol in ('Administrador', 'Tutor')


class IsAdminOrSelf(BasePermission):
    """Admin puede todo; un usuario solo puede ver/editar su propio perfil."""
    def has_permission(self, request, view):
        return bool(request.auth)

    def has_object_permission(self, request, view, obj):
        user_id, rol = get_usuario_from_token(request)
        if rol == 'Administrador':
            return True
        return obj.id_usuario == user_id