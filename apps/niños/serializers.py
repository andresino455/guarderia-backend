from rest_framework import serializers
from .models import Nino, TutorNino, PersonaAutorizada
from apps.tutores.serializers import TutorListSerializer


class NinoSerializer(serializers.ModelSerializer):
    tutores = serializers.SerializerMethodField()

    class Meta:
        model  = Nino
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
                'nombre':   v.id_tutor.nombre,
                'relacion': v.relacion,
            }
            for v in vinculos
        ]


class NinoListSerializer(serializers.ModelSerializer):
    """Versión liviana para listados y relaciones."""
    class Meta:
        model  = Nino
        fields = ['id_nino', 'nombre', 'fecha_nacimiento', 'edad', 'foto', 'activo']


class TutorNinoSerializer(serializers.ModelSerializer):
    nino_nombre  = serializers.CharField(source='id_nino.nombre', read_only=True)
    tutor_nombre = serializers.CharField(source='id_tutor.nombre', read_only=True)

    class Meta:
        model  = TutorNino
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
            # El código de seguridad no se devuelve en listados
            "codigo_seguridad": {"write_only": True}
        }

    def validate_ci(self, value):
        """No permitir CI duplicado para el mismo niño."""
        nino_id = self.initial_data.get("id_nino")
        qs = PersonaAutorizada.objects.filter(ci=value, id_nino=nino_id, activo=True)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "Ya existe una persona autorizada con ese CI para este niño."
            )
        return value


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
            "activo",
            # codigo_seguridad nunca aparece en listados
        ]


class VerificarCodigoSerializer(serializers.Serializer):
    """Para verificar si una persona está autorizada a recoger al niño."""

    ci = serializers.CharField()
    codigo_seguridad = serializers.CharField()
