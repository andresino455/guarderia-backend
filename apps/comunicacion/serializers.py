from rest_framework import serializers
from .models import Mensaje, Notificacion


class MensajeSerializer(serializers.ModelSerializer):
    emisor_nombre   = serializers.CharField(source='id_emisor.nombre',   read_only=True)
    receptor_nombre = serializers.CharField(source='id_receptor.nombre', read_only=True)

    class Meta:
        model  = Mensaje
        fields = [
            'id_mensaje',
            'id_emisor',   'emisor_nombre',
            'id_receptor', 'receptor_nombre',
            'mensaje', 'fecha', 'activo'
        ]
        read_only_fields = ['id_mensaje', 'fecha']


class MensajeListSerializer(serializers.ModelSerializer):
    emisor_nombre   = serializers.CharField(source='id_emisor.nombre',   read_only=True)
    receptor_nombre = serializers.CharField(source='id_receptor.nombre', read_only=True)

    class Meta:
        model  = Mensaje
        fields = [
            'id_mensaje', 'emisor_nombre', 'receptor_nombre',
            'mensaje', 'fecha'
        ]


class NotificacionSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='id_usuario.nombre', read_only=True)

    class Meta:
        model  = Notificacion
        fields = [
            'id_notificacion', 'id_usuario', 'usuario_nombre',
            'mensaje', 'fecha', 'leido', 'activo'
        ]
        read_only_fields = ['id_notificacion', 'fecha']


class NotificacionBulkSerializer(serializers.Serializer):
    """Para enviar la misma notificación a múltiples usuarios."""
    usuarios = serializers.ListField(child=serializers.IntegerField())
    mensaje  = serializers.CharField()