from rest_framework import serializers
from .models import Nino, TutorNino
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