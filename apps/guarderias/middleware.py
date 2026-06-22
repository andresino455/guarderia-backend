from django.http import JsonResponse


RUTAS_PUBLICAS = [
    "/admin/",
    "/api/v1/usuarios/login/",
    "/api/v1/auth/",
]


class GuarderiaMiddleware:
    """
    Inyecta request.guarderia en cada request autenticado.
    Usa el autenticador personalizado del proyecto (UsuarioJWTAuthentication).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def _get_authenticator(self):
        try:
            from apps.usuarios.authentication import UsuarioJWTAuthentication

            return UsuarioJWTAuthentication()
        except ImportError:
            from rest_framework_simplejwt.authentication import JWTAuthentication

            return JWTAuthentication()

    def __call__(self, request):
        request.guarderia = None

        # Rutas completamente públicas
        if self._es_ruta_publica(request.path):
            return self.get_response(request)

        # Registro público: solo POST a /api/v1/guarderias/
        if (
            request.path.rstrip("/") == "/api/v1/guarderias"
            and request.method == "POST"
        ):
            return self.get_response(request)

        # Intentar autenticar
        try:
            auth = self._get_authenticator()
            resultado = auth.authenticate(request)

            if resultado is not None:
                usuario, _ = resultado
                guarderia = getattr(usuario, "id_guarderia", None)

                if guarderia is None:
                    return JsonResponse(
                        {
                            "detail": "Tu usuario no tiene una guardería asignada.",
                            "code": "no_guarderia",
                        },
                        status=403,
                    )

                request.guarderia = guarderia
                request.user = usuario

        except Exception:
            pass

        return self.get_response(request)

    def _es_ruta_publica(self, path):
        return any(path.startswith(ruta) for ruta in RUTAS_PUBLICAS)
