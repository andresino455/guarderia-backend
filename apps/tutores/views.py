from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.usuarios.permissions import IsAdmin, IsAdminOrSelf
from .models import Tutor, UsuarioTutor
from .serializers import TutorSerializer, TutorListSerializer, UsuarioTutorSerializer


class TutorViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Tutor.objects.filter(activo=True).order_by('nombre')

    def get_serializer_class(self):
        if self.action == 'list':
            return TutorListSerializer
        return TutorSerializer

    def destroy(self, request, *args, **kwargs):
        tutor = self.get_object()
        tutor.activo = False
        tutor.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], url_path='ninos')
    def ninos(self, request, pk=None):
        """GET /api/v1/tutores/{id}/ninos/ — niños vinculados al tutor."""
        from apps.niños.models import TutorNino
        from apps.niños.serializers import NinoListSerializer
        vinculos = TutorNino.objects.filter(
            id_tutor=pk, activo=True
        ).select_related('id_nino')
        ninos = [v.id_nino for v in vinculos]
        return Response(NinoListSerializer(ninos, many=True).data)

    @action(detail=False, methods=['get'], url_path='buscar')
    def buscar(self, request):
        """GET /api/v1/tutores/buscar/?q=nombre — búsqueda rápida."""
        q = request.query_params.get('q', '')
        tutores = Tutor.objects.filter(
            activo=True, nombre__icontains=q
        )[:10]
        return Response(TutorListSerializer(tutores, many=True).data)
    
@action(detail=False, methods=['get'], url_path='mi-dashboard')
def mi_dashboard(self, request):
    """
    GET /api/v1/tutores/mi-dashboard/
    Dashboard completo para el tutor autenticado.
    """
    from apps.usuarios.models import Usuario
    from apps.niños.models import TutorNino
    from apps.niños.serializers import NinoSerializer
    from apps.asistencia.models import Asistencia
    from apps.servicios.models import Pago
    from apps.comunicacion.models import Notificacion
    from apps.camaras.models import Camara
    from apps.camaras.serializers import CamaraListSerializer
    from django.utils import timezone

    user_id = request.auth.payload.get('user_id')

    # Buscar tutor vinculado al usuario
    try:
        usuario_tutor = UsuarioTutor.objects.get(
            id_usuario=user_id, activo=True
        )
        tutor = usuario_tutor.id_tutor
    except UsuarioTutor.DoesNotExist:
        return Response({'detail': 'No tenés perfil de tutor.'}, status=404)

    # Niños del tutor
    vinculos = TutorNino.objects.filter(
        id_tutor=tutor, activo=True
    ).select_related('id_nino')
    ninos = [v.id_nino for v in vinculos]

    # Asistencia reciente (últimos 7 días) de cada niño
    desde = timezone.now().date() - timezone.timedelta(days=7)
    asistencias = Asistencia.objects.filter(
        id_nino__in=ninos,
        fecha__gte=desde,
        activo=True
    ).select_related('id_nino').order_by('-fecha')

    # Pagos pendientes
    pagos_pendientes = Pago.objects.filter(
        id_nino__in=ninos,
        estado='pendiente',
        activo=True
    ).order_by('-fecha')

    # Notificaciones no leídas
    notificaciones = Notificacion.objects.filter(
        id_usuario=user_id,
        leido=False,
        activo=True
    ).order_by('-fecha')[:10]

    # Cámaras de las salas de los niños
    from apps.salas.models import AsignacionNinoSala
    sala_ids = AsignacionNinoSala.objects.filter(
        id_nino__in=ninos, activo=True
    ).values_list('id_sala_id', flat=True)
    camaras = Camara.objects.filter(
        id_sala__in=sala_ids, activo=True
    ).select_related('id_sala')

    from apps.asistencia.serializers import AsistenciaListSerializer
    from apps.servicios.serializers import PagoListSerializer
    from apps.comunicacion.serializers import NotificacionSerializer

    return Response({
        'tutor': TutorListSerializer(tutor).data,
        'ninos': NinoSerializer(ninos, many=True).data,
        'asistencias_recientes': AsistenciaListSerializer(
            asistencias, many=True
        ).data,
        'pagos_pendientes': PagoListSerializer(
            pagos_pendientes, many=True
        ).data,
        'notificaciones': NotificacionSerializer(
            notificaciones, many=True
        ).data,
        'camaras': CamaraListSerializer(camaras, many=True).data,
        'resumen': {
            'total_ninos':       len(ninos),
            'pagos_pendientes':  pagos_pendientes.count(),
            'notif_no_leidas':   Notificacion.objects.filter(
                id_usuario=user_id, leido=False, activo=True
            ).count(),
        }
    })