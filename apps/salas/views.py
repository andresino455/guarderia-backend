from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from .models import Personal, Sala, PersonalSala, AsignacionNinoSala
from .serializers import (
    PersonalSerializer, PersonalListSerializer,
    SalaSerializer, SalaListSerializer,
    PersonalSalaSerializer, AsignacionNinoSalaSerializer,
)


class PersonalViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs   = Personal.objects.filter(activo=True)
        tipo = self.request.query_params.get('tipo')
        if tipo:
            qs = qs.filter(tipo=tipo)
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return PersonalListSerializer
        return PersonalSerializer

    def destroy(self, request, *args, **kwargs):
        personal        = self.get_object()
        personal.activo = False
        personal.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], url_path='salas')
    def salas(self, request, pk=None):
        """GET /api/v1/salas/personal/{id}/salas/"""
        vinculos = PersonalSala.objects.filter(
            id_personal=pk, activo=True
        ).select_related('id_sala')
        return Response(PersonalSalaSerializer(vinculos, many=True).data)


class SalaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Sala.objects.filter(activo=True)

    def get_serializer_class(self):
        if self.action == 'list':
            return SalaListSerializer
        return SalaSerializer

    def destroy(self, request, *args, **kwargs):
        sala        = self.get_object()
        sala.activo = False
        sala.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path='asignar-personal')
    def asignar_personal(self, request, pk=None):
        """POST /api/v1/salas/{id}/asignar-personal/"""
        sala        = self.get_object()
        id_personal = request.data.get('id_personal')

        if not id_personal:
            return Response(
                {'detail': 'id_personal es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        vinculo, created = PersonalSala.objects.get_or_create(
            id_personal_id=id_personal,
            id_sala=sala,
            defaults={'activo': True}
        )
        if not created:
            vinculo.activo = True
            vinculo.save()

        return Response(
            PersonalSalaSerializer(vinculo).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], url_path='asignar-nino')
    def asignar_nino(self, request, pk=None):
        """POST /api/v1/salas/{id}/asignar-nino/"""
        sala    = self.get_object()
        id_nino = request.data.get('id_nino')

        if not id_nino:
            return Response(
                {'detail': 'id_nino es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Desactivar asignación previa del niño si existe
        AsignacionNinoSala.objects.filter(
            id_nino_id=id_nino, activo=True
        ).update(activo=False)

        serializer = AsignacionNinoSalaSerializer(data={
            'id_nino': id_nino,
            'id_sala': sala.id_sala,
            'fecha':   timezone.now().date(),
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='ninos')
    def ninos(self, request, pk=None):
        """GET /api/v1/salas/{id}/ninos/ — niños activos en la sala."""
        asignaciones = AsignacionNinoSala.objects.filter(
            id_sala=pk, activo=True
        ).select_related('id_nino').order_by('id_nino__nombre')
        return Response(
            AsignacionNinoSalaSerializer(asignaciones, many=True).data
        )

    @action(detail=False, methods=['get'], url_path='resumen')
    def resumen(self, request):
        """GET /api/v1/salas/resumen/ — ocupación de todas las salas."""
        salas = Sala.objects.filter(activo=True)
        return Response([
            {
                'id_sala':          s.id_sala,
                'nombre':           s.nombre,
                'edad_min':         s.edad_min,
                'edad_max':         s.edad_max,
                'cupo_max':         s.cupo_max,
                'ocupacion':        s.ocupacion,
                'cupo_disponible':  s.cupo_disponible,
                'porcentaje':       round(
                    (s.ocupacion / s.cupo_max * 100) if s.cupo_max else 0, 1
                ),
            }
            for s in salas
        ])


@action(detail=False, methods=['get'], url_path='mi-sala')
def mi_sala(self, request):
    """
    GET /api/v1/salas/mi-sala/
    Devuelve la sala asignada al personal autenticado.
    """
    from apps.usuarios.views import get_tokens_for_user
    user_id = request.user.id_usuario

    vinculo = PersonalSala.objects.filter(
        id_personal__activo=True,
        id_sala__activo=True,
        activo=True
    ).select_related('id_sala').first()

    if not vinculo:
        return Response({'detail': 'No tenés sala asignada.'}, status=404)

    return Response(SalaSerializer(vinculo.id_sala).data)
