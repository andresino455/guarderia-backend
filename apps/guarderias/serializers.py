from rest_framework import serializers
from .models import Guarderia


class GuarderiaSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Guarderia
        fields = [
            'id_guarderia', 'nombre', 'direccion',
            'telefono', 'email', 'logo', 'activo',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id_guarderia', 'created_at', 'updated_at']