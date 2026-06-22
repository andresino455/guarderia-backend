from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Tutor, UsuarioTutor
from .serializers import (
    TutorSerializer,
    TutorListSerializer,
    UsuarioTutorSerializer,
    TutorConUsuarioSerializer,
)
from apps.guarderias.mixins import GuaderiaMixin


class TutorViewSet(GuaderiaMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Tutor.objects.filter(activo=True).order_by("nombre")
        qs = self.filtrar_por_guarderia(qs)
        return qs

    def get_serializer_class(self):
        return TutorListSerializer if self.action == "list" else TutorSerializer

    def destroy(self, request, *args, **kwargs):
        tutor = self.get_object()
        tutor.activo = False
        tutor.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"], url_path="ninos")
    def ninos(self, request, pk=None):
        from apps.ninos.models import TutorNino
        from apps.ninos.serializers import NinoListSerializer

        vinculos = TutorNino.objects.filter(id_tutor=pk, activo=True).select_related(
            "id_nino"
        )
        ninos = [v.id_nino for v in vinculos]
        return Response(NinoListSerializer(ninos, many=True).data)

    @action(detail=False, methods=["get"], url_path="buscar")
    def buscar(self, request):
        q = request.query_params.get("q", "")
        guarderia = self.get_guarderia()

        qs = Tutor.objects.filter(activo=True, nombre__icontains=q)
        if guarderia:
            qs = qs.filter(id_guarderia=guarderia)

        return Response(TutorListSerializer(qs[:10], many=True).data)

    @action(detail=False, methods=["post"], url_path="crear-con-usuario")
    def crear_con_usuario(self, request):
        """
        POST /api/v1/tutores/crear-con-usuario/
        Crea el tutor, su usuario y el vínculo, todo en la guardería actual.
        """
        guarderia = self.get_guarderia()
        serializer = TutorConUsuarioSerializer(
            data=request.data,
            context={"guarderia": guarderia},
        )
        serializer.is_valid(raise_exception=True)
        tutor = serializer.save()
        return Response(TutorSerializer(tutor).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def mi_dashboard(request):
    """
    GET /api/v1/tutores/mi_dashboard/
    Dashboard para el tutor autenticado, filtrado por su guardería.
    """
    from django.utils import timezone
    from apps.ninos.models import TutorNino
    from apps.ninos.serializers import NinoSerializer
    from apps.asistencia.models import Asistencia
    from apps.servicios.models import Pago
    from apps.comunicacion.models import Notificacion
    from apps.camaras.models import Camara
    from apps.camaras.serializers import CamaraListSerializer
    from apps.asistencia.serializers import AsistenciaListSerializer
    from apps.servicios.serializers import PagoListSerializer
    from apps.comunicacion.serializers import NotificacionSerializer

    user_id = request.user.id_usuario
    guarderia = getattr(request, "guarderia", None)

    try:
        usuario_tutor = UsuarioTutor.objects.get(id_usuario=user_id, activo=True)
        tutor = usuario_tutor.id_tutor
    except UsuarioTutor.DoesNotExist:
        return Response({"detail": "No tenés perfil de tutor."}, status=404)

    vinculos = TutorNino.objects.filter(id_tutor=tutor, activo=True).select_related(
        "id_nino"
    )
    ninos = [v.id_nino for v in vinculos]

    desde = timezone.now().date() - timezone.timedelta(days=7)

    asistencias = (
        Asistencia.objects.filter(
            id_nino__in=ninos,
            fecha__gte=desde,
            activo=True,
        )
        .select_related("id_nino")
        .order_by("-fecha")
    )

    pagos_pendientes = Pago.objects.filter(
        id_nino__in=ninos,
        estado="pendiente",
        activo=True,
    ).order_by("-fecha")

    notificaciones = Notificacion.objects.filter(
        id_usuario=user_id,
        leido=False,
        activo=True,
    ).order_by("-fecha")[:10]

    from apps.salas.models import AsignacionNinoSala

    sala_ids = AsignacionNinoSala.objects.filter(
        id_nino__in=ninos,
        activo=True,
    ).values_list("id_sala_id", flat=True)

    camaras_qs = Camara.objects.filter(
        id_sala__in=sala_ids, activo=True
    ).select_related("id_sala")
    if guarderia:
        camaras_qs = camaras_qs.filter(id_guarderia=guarderia)

    return Response(
        {
            "tutor": TutorListSerializer(tutor).data,
            "ninos": NinoSerializer(ninos, many=True).data,
            "asistencias_recientes": AsistenciaListSerializer(
                asistencias, many=True
            ).data,
            "pagos_pendientes": PagoListSerializer(pagos_pendientes, many=True).data,
            "notificaciones": NotificacionSerializer(notificaciones, many=True).data,
            "camaras": CamaraListSerializer(camaras_qs, many=True).data,
            "resumen": {
                "total_ninos": len(ninos),
                "pagos_pendientes": pagos_pendientes.count(),
                "notif_no_leidas": Notificacion.objects.filter(
                    id_usuario=user_id,
                    leido=False,
                    activo=True,
                ).count(),
            },
        }
    )
