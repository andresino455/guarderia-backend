from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.usuarios.permissions import IsAdmin
from .models import Nino, TutorNino
from .serializers import NinoSerializer, NinoListSerializer, TutorNinoSerializer


class NinoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Nino.objects.filter(activo=True).order_by('nombre')

    def get_serializer_class(self):
        if self.action == 'list':
            return NinoListSerializer
        return NinoSerializer

    def destroy(self, request, *args, **kwargs):
        nino = self.get_object()
        nino.activo = False
        nino.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], url_path='tutores')
    def tutores(self, request, pk=None):
        """GET /api/v1/ninos/{id}/tutores/ — tutores del niño."""
        vinculos = TutorNino.objects.filter(
            id_nino=pk, activo=True
        ).select_related('id_tutor')
        return Response(TutorNinoSerializer(vinculos, many=True).data)

    @action(detail=True, methods=['post'], url_path='vincular-tutor')
    def vincular_tutor(self, request, pk=None):
        """POST /api/v1/ninos/{id}/vincular-tutor/"""
        nino = self.get_object()
        id_tutor = request.data.get('id_tutor')
        relacion = request.data.get('relacion', '')

        if not id_tutor:
            return Response(
                {'detail': 'id_tutor es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        vinculo, created = TutorNino.objects.get_or_create(
            id_nino=nino,
            id_tutor_id=id_tutor,
            defaults={'relacion': relacion, 'activo': True}
        )
        if not created:
            vinculo.activo   = True
            vinculo.relacion = relacion
            vinculo.save()

        return Response(
            TutorNinoSerializer(vinculo).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get'], url_path='buscar')
    def buscar(self, request):
        """GET /api/v1/ninos/buscar/?q=nombre"""
        q = request.query_params.get('q', '')
        ninos = Nino.objects.filter(activo=True, nombre__icontains=q)[:10]
        return Response(NinoListSerializer(ninos, many=True).data)


# ── Resumen para el Dashboard ──────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_resumen(request):
    from django.utils import timezone
    from django.db.models import Sum, Count
    from django.db.models.functions import TruncDay
    from apps.asistencia.models import Asistencia
    from apps.salud.models import Salud
    from apps.servicios.models import Pago

    hoy         = timezone.now().date()
    mes_actual  = hoy.month
    anio_actual = hoy.year

    total_ninos    = Nino.objects.filter(activo=True).count()
    asistencia_hoy = Asistencia.objects.filter(fecha=hoy, estado='presente').count()
    pagos_mes      = Pago.objects.filter(
        fecha__month=mes_actual, fecha__year=anio_actual
    ).count()
    alertas_salud  = Salud.objects.filter(
        fecha=hoy
    ).values('id_nino').distinct().count()

    pagos_grafico = [
        {
            'dia':      p['dia'].strftime('%d/%m'),
            'total':    float(p['total'] or 0),
            'cantidad': p['cantidad'],
        }
        for p in Pago.objects
        .filter(fecha__month=mes_actual, fecha__year=anio_actual)
        .annotate(dia=TruncDay('fecha'))
        .values('dia')
        .annotate(total=Sum('total'), cantidad=Count('id_pago'))
        .order_by('dia')
    ]

    return Response({
        'total_ninos':    total_ninos,
        'asistencia_hoy': asistencia_hoy,
        'pagos_mes':      pagos_mes,
        'alertas_salud':  alertas_salud,
        'pagos_grafico':  pagos_grafico,
    })