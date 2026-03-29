from rest_framework import serializers
from .models import Actividad


class ActividadSerializer(serializers.ModelSerializer):
    nino_nombre = serializers.CharField(source='id_nino.nombre', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model  = Actividad
        fields = [
            'id_actividad', 'id_nino', 'nino_nombre',
            'tipo', 'tipo_display', 'descripcion',
            'fecha', 'activo', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id_actividad', 'created_at', 'updated_at']


class ActividadListSerializer(serializers.ModelSerializer):
    nino_nombre  = serializers.CharField(source='id_nino.nombre', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model  = Actividad
        fields = [
            'id_actividad', 'id_nino', 'nino_nombre',
            'tipo', 'tipo_display', 'descripcion', 'fecha'
        ]


class ActividadBulkSerializer(serializers.Serializer):
    """Para registrar la misma actividad a múltiples niños a la vez."""
    ninos       = serializers.ListField(child=serializers.IntegerField())
    tipo        = serializers.ChoiceField(choices=Actividad.TIPO_CHOICES)
    descripcion = serializers.CharField()
    fecha       = serializers.DateField()