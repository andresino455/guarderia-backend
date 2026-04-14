from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from .models import Asistencia
from .serializers import (
    AsistenciaSerializer, AsistenciaListSerializer,
    CheckInSerializer, CheckOutSerializer
)
from apps.ninos.models import Nino

class AsistenciaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Asistencia.objects.select_related('id_nino').filter(activo=True)

        # Filtros por query params
        fecha  = self.request.query_params.get('fecha')
        nino   = self.request.query_params.get('nino')
        estado = self.request.query_params.get('estado')

        if fecha:
            qs = qs.filter(fecha=fecha)
        if nino:
            qs = qs.filter(id_nino=nino)
        if estado:
            qs = qs.filter(estado=estado)

        return qs.order_by('-fecha', 'id_nino__nombre')

    def get_serializer_class(self):
        if self.action == 'list':
            return AsistenciaListSerializer
        return AsistenciaSerializer

    def destroy(self, request, *args, **kwargs):
        asistencia = self.get_object()
        asistencia.activo = False
        asistencia.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='hoy')
    def hoy(self, request):
        """GET /api/v1/asistencia/hoy/ — asistencia del día actual."""
        hoy = timezone.now().date()
        registros = Asistencia.objects.select_related('id_nino').filter(
            fecha=hoy, activo=True
        ).order_by('id_nino__nombre')

        # Niños sin registro hoy
        ninos_con_registro = registros.values_list('id_nino_id', flat=True)
        ninos_sin_registro = Nino.objects.filter(activo=True).exclude(
            id_nino__in=ninos_con_registro
        ).values('id_nino', 'nombre')

        return Response({
            'fecha':            str(hoy),
            'total_presentes':  registros.filter(estado='presente').count(),
            'total_ausentes':   registros.filter(estado='ausente').count(),
            'total_tardanzas':  registros.filter(estado='tardanza').count(),
            'registros':        AsistenciaListSerializer(registros, many=True).data,
            'sin_registro':     list(ninos_sin_registro),
        })

    @action(detail=False, methods=['post'], url_path='checkin')
    def checkin(self, request):
        """POST /api/v1/asistencia/checkin/ — entrada rápida de un niño."""
        serializer = CheckInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        hoy     = timezone.now().date()
        hora    = timezone.now().time()
        id_nino = serializer.validated_data['id_nino']
        estado  = serializer.validated_data['estado']

        asistencia, created = Asistencia.objects.get_or_create(
            id_nino_id=id_nino,
            fecha=hoy,
            defaults={
                'hora_ingreso': hora,
                'estado':       estado,
                'activo':       True,
            }
        )
        if not created:
            return Response(
                {'detail': 'Este niño ya tiene registro de asistencia hoy.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            AsistenciaSerializer(asistencia).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['patch'], url_path='checkout')
    def checkout(self, request, pk=None):
        """PATCH /api/v1/asistencia/{id}/checkout/ — registrar salida."""
        asistencia = self.get_object()
        serializer = CheckOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if asistencia.hora_salida:
            return Response(
                {'detail': 'Ya se registró la salida de este niño.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        asistencia.hora_salida = serializer.validated_data['hora_salida']
        asistencia.save()
        return Response(AsistenciaSerializer(asistencia).data)

    @action(detail=False, methods=['get'], url_path='reporte')
    def reporte(self, request):
        """GET /api/v1/asistencia/reporte/?desde=YYYY-MM-DD&hasta=YYYY-MM-DD"""
        desde = request.query_params.get('desde')
        hasta = request.query_params.get('hasta')

        qs = Asistencia.objects.filter(activo=True)
        if desde:
            qs = qs.filter(fecha__gte=desde)
        if hasta:
            qs = qs.filter(fecha__lte=hasta)

        from django.db.models import Count
        resumen = qs.values('estado').annotate(total=Count('id_asistencia'))

        return Response({
            'desde':   desde,
            'hasta':   hasta,
            'resumen': list(resumen),
            'detalle': AsistenciaListSerializer(
                qs.select_related('id_nino').order_by('-fecha'), many=True
            ).data,
        })
