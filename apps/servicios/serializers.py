from rest_framework import serializers
from .models import Servicio, NinoServicio, Pago, DetallePago


class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Servicio
        fields = [
            'id_servicio', 'nombre', 'descripcion',
            'precio', 'tipo', 'activo', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id_servicio', 'created_at', 'updated_at']


class ServicioListSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Servicio
        fields = ['id_servicio', 'nombre', 'precio', 'tipo', 'activo']


class NinoServicioSerializer(serializers.ModelSerializer):
    nino_nombre     = serializers.CharField(source='id_nino.nombre',     read_only=True)
    servicio_nombre = serializers.CharField(source='id_servicio.nombre', read_only=True)
    servicio_precio = serializers.DecimalField(
        source='id_servicio.precio', max_digits=10,
        decimal_places=2, read_only=True
    )

    class Meta:
        model  = NinoServicio
        fields = [
            'id_nino', 'nino_nombre',
            'id_servicio', 'servicio_nombre', 'servicio_precio',
            'activo', 'created_at'
        ]
        read_only_fields = ['created_at']


# ── Pagos ──────────────────────────────────────────────────────────────────────

class DetallePagoSerializer(serializers.ModelSerializer):
    servicio_nombre = serializers.CharField(source='id_servicio.nombre', read_only=True)

    class Meta:
        model  = DetallePago
        fields = [
            'id_detalle', 'id_servicio', 'servicio_nombre',
            'monto', 'activo'
        ]
        read_only_fields = ['id_detalle']


class PagoSerializer(serializers.ModelSerializer):
    nino_nombre = serializers.CharField(source='id_nino.nombre', read_only=True)
    detalles    = DetallePagoSerializer(many=True)

    class Meta:
        model  = Pago
        fields = [
            'id_pago', 'id_nino', 'nino_nombre',
            'fecha', 'total', 'estado',
            'detalles', 'activo', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id_pago', 'total', 'created_at', 'updated_at']

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')

        # Calcular total automáticamente desde los detalles
        total = sum(d['monto'] for d in detalles_data)
        pago  = Pago.objects.create(**validated_data, total=total)

        for detalle in detalles_data:
            DetallePago.objects.create(id_pago=pago, **detalle)

        return pago

    def update(self, instance, validated_data):
        detalles_data = validated_data.pop('detalles', None)

        # Actualizar campos del pago
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if detalles_data is not None:
            # Reemplazar detalles existentes
            instance.detalles.all().delete()
            for detalle in detalles_data:
                DetallePago.objects.create(id_pago=instance, **detalle)
            instance.total = sum(d['monto'] for d in detalles_data)

        instance.save()
        return instance


class PagoListSerializer(serializers.ModelSerializer):
    nino_nombre     = serializers.CharField(source='id_nino.nombre', read_only=True)
    cantidad_items  = serializers.IntegerField(source='detalles.count', read_only=True)

    class Meta:
        model  = Pago
        fields = [
            'id_pago', 'id_nino', 'nino_nombre',
            'fecha', 'total', 'estado', 'cantidad_items'
        ]


class ResumenPagosSerializer(serializers.Serializer):
    """Para el endpoint de resumen mensual."""
    mes          = serializers.IntegerField()
    anio         = serializers.IntegerField()
    total_pagado = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_pagos  = serializers.IntegerField()
    pendientes   = serializers.IntegerField()
    anulados     = serializers.IntegerField()