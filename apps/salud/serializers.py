from rest_framework import serializers
from .models import Salud, Medicacion, Alimentacion


class SaludSerializer(serializers.ModelSerializer):
    nino_nombre = serializers.CharField(source='id_nino.nombre', read_only=True)

    class Meta:
        model  = Salud
        fields = [
            'id_salud', 'id_nino', 'nino_nombre',
            'fecha', 'sintomas', 'observaciones',
            'activo', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id_salud', 'created_at', 'updated_at']


class SaludListSerializer(serializers.ModelSerializer):
    nino_nombre = serializers.CharField(source='id_nino.nombre', read_only=True)

    class Meta:
        model  = Salud
        fields = ['id_salud', 'id_nino', 'nino_nombre', 'fecha', 'sintomas']


class MedicacionSerializer(serializers.ModelSerializer):
    nino_nombre = serializers.CharField(source='id_nino.nombre', read_only=True)

    class Meta:
        model  = Medicacion
        fields = [
            'id_medicacion', 'id_nino', 'nino_nombre',
            'medicamento', 'dosis', 'hora',
            'activo', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id_medicacion', 'created_at', 'updated_at']


class AlimentacionSerializer(serializers.ModelSerializer):
    nino_nombre = serializers.CharField(source='id_nino.nombre', read_only=True)

    class Meta:
        model  = Alimentacion
        fields = [
            'id_alimentacion', 'id_nino', 'nino_nombre',
            'tipo_comida', 'horario', 'observaciones',
            'activo', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id_alimentacion', 'created_at', 'updated_at']