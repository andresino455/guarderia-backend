from rest_framework import serializers
from .models import Personal, Sala, PersonalSala, AsignacionNinoSala


class PersonalSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Personal
        fields = [
            'id_personal', 'nombre', 'telefono',
            'tipo', 'activo', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id_personal', 'created_at', 'updated_at']


class PersonalListSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Personal
        fields = ['id_personal', 'nombre', 'telefono', 'tipo', 'activo']


class PersonalSalaSerializer(serializers.ModelSerializer):
    personal_nombre = serializers.CharField(source='id_personal.nombre', read_only=True)
    personal_tipo   = serializers.CharField(source='id_personal.tipo',   read_only=True)

    class Meta:
        model  = PersonalSala
        fields = [
            'id_personal', 'personal_nombre', 'personal_tipo',
            'id_sala', 'activo', 'created_at'
        ]
        read_only_fields = ['created_at']


class AsignacionNinoSalaSerializer(serializers.ModelSerializer):
    nino_nombre = serializers.CharField(source='id_nino.nombre', read_only=True)
    nino_edad   = serializers.IntegerField(source='id_nino.edad', read_only=True)

    class Meta:
        model  = AsignacionNinoSala
        fields = [
            'id_asignacion', 'id_nino', 'nino_nombre', 'nino_edad',
            'id_sala', 'fecha', 'activo', 'created_at'
        ]
        read_only_fields = ['id_asignacion', 'created_at']

    def validate(self, data):
        sala = data.get('id_sala')
        nino = data.get('id_nino')

        # Verificar cupo disponible
        if sala and sala.cupo_disponible <= 0:
            raise serializers.ValidationError(
                f'La sala "{sala.nombre}" no tiene cupo disponible.'
            )

        # Verificar rango de edad
        if sala and nino and nino.edad is not None:
            if not (sala.edad_min <= nino.edad <= sala.edad_max):
                raise serializers.ValidationError(
                    f'El niño tiene {nino.edad} años y la sala '
                    f'acepta de {sala.edad_min} a {sala.edad_max} años.'
                )
        return data


class SalaSerializer(serializers.ModelSerializer):
    cupo_disponible = serializers.IntegerField(read_only=True)
    ocupacion       = serializers.IntegerField(read_only=True)
    personal        = PersonalSalaSerializer(many=True, read_only=True)
    ninos           = AsignacionNinoSalaSerializer(
        source='asignaciones', many=True, read_only=True
    )

    class Meta:
        model  = Sala
        fields = [
            'id_sala', 'nombre', 'edad_min', 'edad_max',
            'cupo_max', 'cupo_disponible', 'ocupacion',
            'personal', 'ninos',
            'activo', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id_sala', 'created_at', 'updated_at']

    def validate(self, data):
        if data.get('edad_min', 0) > data.get('edad_max', 99):
            raise serializers.ValidationError(
                'La edad mínima no puede ser mayor a la edad máxima.'
            )
        return data


class SalaListSerializer(serializers.ModelSerializer):
    cupo_disponible = serializers.IntegerField(read_only=True)
    ocupacion       = serializers.IntegerField(read_only=True)

    class Meta:
        model  = Sala
        fields = [
            'id_sala', 'nombre', 'edad_min', 'edad_max',
            'cupo_max', 'cupo_disponible', 'ocupacion', 'activo'
        ]