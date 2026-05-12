from django.http import JsonResponse
from apps.guarderias.models import Guarderia


class GuarderiaMiddleware:
    """
    Inyecta la guardería del usuario autenticado en cada request.
    Así todas las vistas pueden filtrar por request.guarderia.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.guarderia = None

        # Rutas que no necesitan guardería
        rutas_publicas = [
            '/admin/', '/api/v1/auth/', '/api/v1/usuarios/login/',
            '/api/v1/guarderias/',
        ]
        if any(request.path.startswith(r) for r in rutas_publicas):
            return self.get_response(request)

        # Si el usuario está autenticado, obtener su guardería
        if hasattr(request, 'user') and hasattr(request.user, 'id_guarderia_id'):
            request.guarderia = request.user.id_guarderia

        return self.get_response(request)