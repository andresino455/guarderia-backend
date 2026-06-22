from rest_framework import serializers
from .models import Guarderia


class GuarderiaSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Guarderia
        fields = [
            "id_guarderia",
            "nombre",
            "direccion",
            "telefono",
            "email",
            "logo",
            "activo",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id_guarderia", "created_at", "updated_at"]

    def validate_nombre(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError(
                "El nombre de la guardería es obligatorio."
            )
        # Verificar que no exista otra con el mismo nombre
        qs = Guarderia.objects.filter(nombre__iexact=value.strip(), activo=True)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya existe una guardería con ese nombre.")
        return value.strip()


class GuarderiaRegistroSerializer(serializers.Serializer):
    """
    Serializer para el endpoint de registro público.
    Documenta todos los campos necesarios.
    """

    # Datos de la guardería
    nombre = serializers.CharField(max_length=100)
    direccion = serializers.CharField(required=False, allow_blank=True)
    telefono = serializers.CharField(required=False, allow_blank=True, max_length=20)
    email = serializers.EmailField(required=False, allow_blank=True)

    # Datos del administrador inicial
    admin_nombre = serializers.CharField(max_length=100)
    admin_email = serializers.EmailField()
    admin_password = serializers.CharField(min_length=8, write_only=True)
