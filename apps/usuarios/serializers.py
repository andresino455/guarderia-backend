# apps/usuarios/serializers.py
from rest_framework import serializers
from django.contrib.auth.hashers import make_password, check_password
from .models import Rol, Usuario


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id_rol', 'nombre', 'activo', 'created_at', 'updated_at']
        read_only_fields = ['id_rol', 'created_at', 'updated_at']


class UsuarioSerializer(serializers.ModelSerializer):
    rol_nombre = serializers.CharField(source='id_rol.nombre', read_only=True)

    class Meta:
        model = Usuario
        fields = [
            'id_usuario', 'nombre', 'email', 'password',
            'id_rol', 'rol_nombre', 'activo', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id_usuario', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True},  # nunca devolver el hash
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Si mandan password nueva, hashearla
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)


class UsuarioListSerializer(serializers.ModelSerializer):
    """Versión liviana para listados (sin password)."""
    rol_nombre = serializers.CharField(source='id_rol.nombre', read_only=True)

    class Meta:
        model = Usuario
        fields = ['id_usuario', 'nombre', 'email', 'id_rol', 'rol_nombre', 'activo']


class CambiarPasswordSerializer(serializers.Serializer):
    password_actual = serializers.CharField(write_only=True)
    password_nueva = serializers.CharField(write_only=True, min_length=8)
    password_confirmacion = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['password_nueva'] != data['password_confirmacion']:
            raise serializers.ValidationError(
                {'password_confirmacion': 'Las contraseñas no coinciden.'}
            )
        return data

    def validate_password_actual(self, value):
        usuario = self.context['request'].user_obj
        if not check_password(value, usuario.password):
            raise serializers.ValidationError('La contraseña actual es incorrecta.')
        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)