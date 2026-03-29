from rest_framework import serializers
from .models import Camara


class CamaraSerializer(serializers.ModelSerializer):
    sala_nombre = serializers.CharField(source='id_sala.nombre', read_only=True)

    class Meta:
        model  = Camara
        fields = [
            'id_camara', 'id_sala', 'sala_nombre',
            'url_stream', 'activo', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id_camara', 'created_at', 'updated_at']


class CamaraListSerializer(serializers.ModelSerializer):
    sala_nombre = serializers.CharField(source='id_sala.nombre', read_only=True)

    class Meta:
        model  = Camara
        fields = ['id_camara', 'id_sala', 'sala_nombre', 'url_stream', 'activo']