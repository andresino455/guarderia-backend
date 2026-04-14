import random
from rest_framework import serializers
from .models import Nino, TutorNino, PersonaAutorizada, RetiroNino


class NinoSerializer(serializers.ModelSerializer):
    tutores = serializers.SerializerMethodField()

    class Meta:
        model = Nino
        fields = [
            'id_nino', 'nombre', 'fecha_nacimiento', 'edad',
            'foto', 'info_medica', 'activo',
            'created_at', 'updated_at', 'tutores'
        ]
        read_only_fields = ['id_nino', 'edad', 'created_at', 'updated_at']

    def get_tutores(self, obj):
        vinculos = TutorNino.objects.filter(
            id_nino=obj, activo=True
        ).select_related('id_tutor')
        return [
            {
                'id_tutor': v.id_tutor.id_tutor,
                'nombre': v.id_tutor.nombre,
                'relacion': v.relacion,
            }
            for v in vinculos
        ]


class NinoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nino
        fields = ['id_nino', 'nombre', 'fecha_nacimiento', 'edad', 'foto', 'activo']


class TutorNinoSerializer(serializers.ModelSerializer):
    nino_nombre = serializers.CharField(source='id_nino.nombre', read_only=True)
    tutor_nombre = serializers.CharField(source='id_tutor.nombre', read_only=True)

    class Meta:
        model = TutorNino
        fields = [
            'id_tutor', 'tutor_nombre',
            'id_nino', 'nino_nombre',
            'relacion', 'activo', 'created_at'
        ]
        read_only_fields = ['created_at']


class PersonaAutorizadaSerializer(serializers.ModelSerializer):
    nino_nombre = serializers.CharField(source="id_nino.nombre", read_only=True)

    class Meta:
        model = PersonaAutorizada
        fields = [
            "id_persona",
            "id_nino",
            "nino_nombre",
            "nombre",
            "ci",
            "telefono",
            "codigo_seguridad",
            "activo",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id_persona", "created_at", "updated_at"]
        extra_kwargs = {
            "codigo_seguridad": {"required": False, "allow_blank": True},
            "telefono": {"required": False, "allow_blank": True, "allow_null": True},
        }

    def validate_ci(self, value):
        nino_id = self.initial_data.get("id_nino")
        qs = PersonaAutorizada.objects.filter(ci=value, id_nino=nino_id, activo=True)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "Ya existe una persona autorizada con ese CI para este niño."
            )
        return value

    def _generar_codigo_seguridad(self, id_nino):
        while True:
            codigo = f"COD-{id_nino}-{random.randint(100, 999)}"
            if not PersonaAutorizada.objects.filter(codigo_seguridad=codigo).exists():
                return codigo

    def create(self, validated_data):
        codigo = validated_data.get("codigo_seguridad")
        id_nino = validated_data["id_nino"]

        if not codigo or not str(codigo).strip():
            validated_data["codigo_seguridad"] = self._generar_codigo_seguridad(
                id_nino.id_nino
            )

        return super().create(validated_data)

    def update(self, instance, validated_data):
        codigo = validated_data.get("codigo_seguridad", None)

        if codigo is not None and not str(codigo).strip():
            validated_data.pop("codigo_seguridad", None)

        if not instance.codigo_seguridad and "codigo_seguridad" not in validated_data:
            validated_data["codigo_seguridad"] = self._generar_codigo_seguridad(
                instance.id_nino.id_nino
            )

        return super().update(instance, validated_data)


class PersonaAutorizadaListSerializer(serializers.ModelSerializer):
    nino_nombre = serializers.CharField(source="id_nino.nombre", read_only=True)

    class Meta:
        model = PersonaAutorizada
        fields = [
            "id_persona",
            "id_nino",
            "nino_nombre",
            "nombre",
            "ci",
            "telefono",
            "codigo_seguridad",
            "activo",
        ]


class VerificarCodigoSerializer(serializers.Serializer):
    id_nino = serializers.IntegerField()
    ci = serializers.CharField()
    codigo_seguridad = serializers.CharField()


class RegistrarRetiroSerializer(serializers.Serializer):
    ci = serializers.CharField()
    codigo_seguridad = serializers.CharField()
    observacion = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class RetiroNinoSerializer(serializers.ModelSerializer):
    nino_nombre = serializers.CharField(source='id_nino.nombre', read_only=True)
    persona_nombre = serializers.CharField(source='id_persona_autorizada.nombre', read_only=True)
    persona_ci = serializers.CharField(source='id_persona_autorizada.ci', read_only=True)
    registrado_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = RetiroNino
        fields = [
            'id_retiro',
            'id_nino',
            'nino_nombre',
            'id_persona_autorizada',
            'persona_nombre',
            'persona_ci',
            'codigo_seguridad_usado',
            'observacion',
            'fecha_hora_retiro',
            'created_at',
            'registrado_por',
            'registrado_por_nombre',
        ]
        read_only_fields = fields

    def get_registrado_por_nombre(self, obj):
        if not obj.registrado_por:
            return None
        return getattr(obj.registrado_por, 'nombre', None) or getattr(obj.registrado_por, 'username', None)