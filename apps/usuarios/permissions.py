from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, "id_rol"):
            return False
        return request.user.id_rol and request.user.id_rol.nombre == "Administrador"


class IsPersonal(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, "id_rol"):
            return False
        return request.user.id_rol and request.user.id_rol.nombre in (
            "Administrador",
            "Personal",
        )


class IsTutor(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, "id_rol"):
            return False
        return request.user.id_rol and request.user.id_rol.nombre in (
            "Administrador",
            "Tutor",
        )


class IsAdminOrSelf(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "id_usuario")

    def has_object_permission(self, request, view, obj):
        if not hasattr(request.user, "id_rol"):
            return False
        if request.user.id_rol and request.user.id_rol.nombre == "Administrador":
            return True
        return obj.id_usuario == request.user.id_usuario
