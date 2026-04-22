from rest_framework import serializers
from .models import Tutor, UsuarioTutor
from rest_framework.response import Response


class TutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tutor
        fields = [
            "id_tutor",
            "nombre",
            "ci",
            "telefono",
            "direccion",
            "email",
            "activo",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id_tutor", "created_at", "updated_at"]

    def validate_ci(self, value):
        qs = Tutor.objects.filter(ci=value, activo=True)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya existe un tutor con ese CI.")
        return value


class TutorListSerializer(serializers.ModelSerializer):
    """Versión liviana para listados."""

    class Meta:
        model = Tutor
        fields = ["id_tutor", "nombre", "ci", "telefono", "email", "activo"]


class UsuarioTutorSerializer(serializers.ModelSerializer):
    tutor_nombre = serializers.CharField(source="id_tutor.nombre", read_only=True)
    usuario_nombre = serializers.CharField(source="id_usuario.nombre", read_only=True)

    class Meta:
        model = UsuarioTutor
        fields = [
            "id_usuario",
            "usuario_nombre",
            "id_tutor",
            "tutor_nombre",
            "activo",
            "created_at",
        ]
        read_only_fields = ["created_at"]


from apps.usuarios.models import Usuario, Rol
from django.contrib.auth.hashers import make_password


class TutorConUsuarioSerializer(serializers.ModelSerializer):
    """Crea el tutor y su usuario en una sola operación."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = Tutor
        fields = ["nombre", "ci", "telefono", "direccion", "email", "password"]

    def validate_ci(self, value):
        if Tutor.objects.filter(ci=value, activo=True).exists():
            raise serializers.ValidationError("Ya existe un tutor con ese CI.")
        return value

    def validate_email(self, value):
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con ese email.")
        return value

    def create(self, validated_data):
        email = validated_data.pop("email")
        password = validated_data.pop("password")

        tutor = Tutor.objects.create(email=email, **validated_data)

        rol, _ = Rol.objects.get_or_create(nombre="Tutor")

        usuario = Usuario.objects.create(
            nombre=tutor.nombre,
            email=email,
            password=make_password(password),
            id_rol=rol,
            activo=True,
        )

        UsuarioTutor.objects.create(
            id_usuario=usuario,
            id_tutor=tutor,
            activo=True,
        )

        return tutor

    def destroy(self, request, *args, **kwargs):
        tutor = self.get_object()

        serializer = self.get_serializer()
        serializer.delete(tutor)

        return Response({"message": "Tutor eliminado PERMANENTEMENTE"}, status=200)
