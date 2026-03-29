from rest_framework import serializers
from django.utils import timezone
from .models import Asistencia


class AsistenciaSerializer(serializers.ModelSerializer):
    nino_nombre = serializers.CharField(source='id_nino.nombre', read_only=True)

    class Meta:
        model  = Asistencia
        fields = [
            'id_asistencia', 'id_nino', 'nino_nombre',
            'fecha', 'hora_ingreso', 'hora_salida',
            'estado', 'activo', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id_asistencia', 'created_at', 'updated_at']

    def validate(self, data):
        # No permitir duplicado niño+fecha en creación
        if self.instance is None:
            existe = Asistencia.objects.filter(
                id_nino=data.get('id_nino'),
                fecha=data.get('fecha'),
                activo=True
            ).exists()
            if existe:
                raise serializers.ValidationError(
                    'Ya existe un registro de asistencia para este niño en esa fecha.'
                )
        return data


class AsistenciaListSerializer(serializers.ModelSerializer):
    nino_nombre = serializers.CharField(source='id_nino.nombre', read_only=True)

    class Meta:
        model  = Asistencia
        fields = [
            'id_asistencia', 'id_nino', 'nino_nombre',
            'fecha', 'hora_ingreso', 'hora_salida', 'estado'
        ]


class CheckInSerializer(serializers.Serializer):
    """Para registrar entrada rápida."""
    id_nino = serializers.IntegerField()
    estado  = serializers.ChoiceField(
        choices=['presente', 'ausente', 'tardanza'],
        default='presente'
    )


class CheckOutSerializer(serializers.Serializer):
    """Para registrar salida."""
    hora_salida = serializers.TimeField()