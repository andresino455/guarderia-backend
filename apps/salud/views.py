from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from .models import Salud, Medicacion, Alimentacion
from .serializers import (
    SaludSerializer,
    SaludListSerializer,
    MedicacionSerializer,
    AlimentacionSerializer,
)
from apps.guarderias.mixins import GuaderiaMixin


class SaludViewSet(GuaderiaMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Salud.objects.select_related("id_nino").filter(activo=True)
        qs = self.filtrar_por_guarderia(qs)

        nino = self.request.query_params.get("nino")
        fecha = self.request.query_params.get("fecha")

        if nino:
            qs = qs.filter(id_nino=nino)
        if fecha:
            qs = qs.filter(fecha=fecha)

        return qs.order_by("-fecha")

    def get_serializer_class(self):
        return SaludListSerializer if self.action == "list" else SaludSerializer

    def destroy(self, request, *args, **kwargs):
        registro = self.get_object()
        registro.activo = False
        registro.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="alertas-hoy")
    def alertas_hoy(self, request):
        hoy = timezone.now().date()
        guarderia = self.get_guarderia()

        qs = Salud.objects.select_related("id_nino").filter(fecha=hoy, activo=True)
        if guarderia:
            qs = qs.filter(id_guarderia=guarderia)

        return Response(
            {
                "fecha": str(hoy),
                "total": qs.count(),
                "alertas": SaludListSerializer(qs, many=True).data,
            }
        )


class MedicacionViewSet(GuaderiaMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MedicacionSerializer

    def get_queryset(self):
        qs = Medicacion.objects.select_related("id_nino").filter(activo=True)
        qs = self.filtrar_por_guarderia(qs)

        nino = self.request.query_params.get("nino")
        if nino:
            qs = qs.filter(id_nino=nino)

        return qs.order_by("hora")

    def destroy(self, request, *args, **kwargs):
        med = self.get_object()
        med.activo = False
        med.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="hoy")
    def hoy(self, request):
        hora_actual = timezone.now().time()
        guarderia = self.get_guarderia()

        qs = Medicacion.objects.select_related("id_nino").filter(
            activo=True, hora__gte=hora_actual
        )
        if guarderia:
            qs = qs.filter(id_guarderia=guarderia)

        return Response(MedicacionSerializer(qs.order_by("hora"), many=True).data)


class AlimentacionViewSet(GuaderiaMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AlimentacionSerializer

    def get_queryset(self):
        qs = Alimentacion.objects.select_related("id_nino").filter(activo=True)
        qs = self.filtrar_por_guarderia(qs)

        nino = self.request.query_params.get("nino")
        if nino:
            qs = qs.filter(id_nino=nino)

        return qs.order_by("horario")

    def destroy(self, request, *args, **kwargs):
        alim = self.get_object()
        alim.activo = False
        alim.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
