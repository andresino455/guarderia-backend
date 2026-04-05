from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.settings import api_settings
from .models import Usuario


class UsuarioJWTAuthentication(JWTAuthentication):
    """
    Autenticador JWT personalizado que usa el modelo Usuario
    en lugar del User de Django.
    """

    def get_user(self, validated_token):
        try:
            user_id = validated_token['user_id']
        except KeyError:
            raise InvalidToken('Token no contiene user_id.')

        try:
            usuario = Usuario.objects.select_related('id_rol').get(
                id_usuario=user_id, activo=True
            )
        except Usuario.DoesNotExist:
            raise InvalidToken('Usuario no encontrado o inactivo.')

        return usuario