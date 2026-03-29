from rest_framework import serializers
from .models import Bitacora, HistorialCambios


class BitacoraSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(
        source='id_usuario.nombre', read_only=True, default='Sistema'
    )

    class Meta:
        model  = Bitacora
        fields = [
            'id_bitacora', 'id_usuario', 'usuario_nombre',
            'accion', 'tabla', 'id_registro',
            'fecha', 'descripcion'
        ]


class HistorialCambiosSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(
        source='id_usuario.nombre', read_only=True, default='Sistema'
    )

    class Meta:
        model  = HistorialCambios
        fields = [
            'id_historial', 'tabla', 'id_registro',
            'campo', 'valor_anterior', 'valor_nuevo',
            'fecha', 'id_usuario', 'usuario_nombre'
        ]