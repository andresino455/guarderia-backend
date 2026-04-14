from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count

from .models import Actividad
from .serializers import (
    ActividadSerializer, ActividadListSerializer, ActividadBulkSerializer
)
from apps.ninos.models import Nino

class ActividadViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs    = Actividad.objects.select_related('id_nino').filter(activo=True)
        nino  = self.request.query_params.get('nino')
        tipo  = self.request.query_params.get('tipo')
        fecha = self.request.query_params.get('fecha')
        desde = self.request.query_params.get('desde')
        hasta = self.request.query_params.get('hasta')

        if nino:
            qs = qs.filter(id_nino=nino)
        if tipo:
            qs = qs.filter(tipo=tipo)
        if fecha:
            qs = qs.filter(fecha=fecha)
        if desde:
            qs = qs.filter(fecha__gte=desde)
        if hasta:
            qs = qs.filter(fecha__lte=hasta)

        return qs.order_by('-fecha')

    def get_serializer_class(self):
        if self.action == 'list':
            return ActividadListSerializer
        return ActividadSerializer

    def destroy(self, request, *args, **kwargs):
        actividad        = self.get_object()
        actividad.activo = False
        actividad.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='hoy')
    def hoy(self, request):
        """GET /api/v1/actividades/hoy/ — actividades del día."""
        hoy        = timezone.now().date()
        actividades = Actividad.objects.select_related('id_nino').filter(
            fecha=hoy, activo=True
        ).order_by('tipo')
        return Response({
            'fecha':      str(hoy),
            'total':      actividades.count(),
            'actividades': ActividadListSerializer(actividades, many=True).data,
        })

    @action(detail=False, methods=['post'], url_path='registrar-grupo')
    def registrar_grupo(self, request):
        """
        POST /api/v1/actividades/registrar-grupo/
        Registra la misma actividad para varios niños a la vez.
        """
        serializer = ActividadBulkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ninos_ids   = serializer.validated_data['ninos']
        tipo        = serializer.validated_data['tipo']
        descripcion = serializer.validated_data['descripcion']
        fecha       = serializer.validated_data['fecha']

        ninos    = Nino.objects.filter(id_nino__in=ninos_ids, activo=True)
        creadas  = []

        for nino in ninos:
            actividad = Actividad.objects.create(
                id_nino=nino,
                tipo=tipo,
                descripcion=descripcion,
                fecha=fecha,
            )
            creadas.append(actividad)

        return Response({
            'detail':   f'Se registraron {len(creadas)} actividades.',
            'creadas':  ActividadListSerializer(creadas, many=True).data,
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='estadisticas')
    def estadisticas(self, request):
        """GET /api/v1/actividades/estadisticas/ — conteo por tipo."""
        desde = request.query_params.get('desde')
        hasta = request.query_params.get('hasta')

        qs = Actividad.objects.filter(activo=True)
        if desde:
            qs = qs.filter(fecha__gte=desde)
        if hasta:
            qs = qs.filter(fecha__lte=hasta)

        por_tipo = qs.values('tipo').annotate(
            total=Count('id_actividad')
        ).order_by('-total')

        return Response({
            'total_actividades': qs.count(),
            'por_tipo':          list(por_tipo),
        })
