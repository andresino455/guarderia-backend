from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum, Count

from .models import Servicio, NinoServicio, Pago, DetallePago
from .serializers import (
    ServicioSerializer,
    ServicioListSerializer,
    NinoServicioSerializer,
    PagoSerializer,
    PagoListSerializer,
)
from apps.guarderias.mixins import GuaderiaMixin


class ServicioViewSet(GuaderiaMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Servicio.objects.filter(activo=True)
        qs = self.filtrar_por_guarderia(qs)

        tipo = self.request.query_params.get("tipo")
        if tipo:
            qs = qs.filter(tipo=tipo)

        return qs

    def get_serializer_class(self):
        return ServicioListSerializer if self.action == "list" else ServicioSerializer

    def destroy(self, request, *args, **kwargs):
        servicio = self.get_object()
        servicio.activo = False
        servicio.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"], url_path="ninos")
    def ninos(self, request, pk=None):
        vinculos = NinoServicio.objects.filter(
            id_servicio=pk, activo=True
        ).select_related("id_nino")
        return Response(NinoServicioSerializer(vinculos, many=True).data)

    @action(detail=False, methods=["post"], url_path="asignar")
    def asignar(self, request):
        id_nino = request.data.get("id_nino")
        id_servicio = request.data.get("id_servicio")

        if not id_nino or not id_servicio:
            return Response(
                {"detail": "id_nino e id_servicio son requeridos."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        vinculo, created = NinoServicio.objects.get_or_create(
            id_nino_id=id_nino,
            id_servicio_id=id_servicio,
            defaults={"activo": True},
        )
        if not created:
            vinculo.activo = True
            vinculo.save()

        return Response(
            NinoServicioSerializer(vinculo).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=False, methods=["delete"], url_path="desasignar")
    def desasignar(self, request):
        id_nino = request.data.get("id_nino")
        id_servicio = request.data.get("id_servicio")

        try:
            vinculo = NinoServicio.objects.get(
                id_nino_id=id_nino, id_servicio_id=id_servicio
            )
            vinculo.activo = False
            vinculo.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except NinoServicio.DoesNotExist:
            return Response(
                {"detail": "Vínculo no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=False, methods=["get"], url_path="por-nino")
    def por_nino(self, request):
        nino_id = request.query_params.get("nino")
        if not nino_id:
            return Response(
                {"detail": "Parámetro nino es requerido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        vinculos = NinoServicio.objects.filter(
            id_nino=nino_id, activo=True
        ).select_related("id_servicio")

        return Response(
            [
                {
                    "id_servicio": v.id_servicio.id_servicio,
                    "nombre": v.id_servicio.nombre,
                    "precio": float(v.id_servicio.precio),
                    "tipo": v.id_servicio.tipo,
                }
                for v in vinculos
            ]
        )


class PagoViewSet(GuaderiaMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Pago.objects.select_related("id_nino").filter(activo=True)
        qs = self.filtrar_por_guarderia(qs)

        nino = self.request.query_params.get("nino")
        estado = self.request.query_params.get("estado")
        mes = self.request.query_params.get("mes")
        anio = self.request.query_params.get("anio")

        if nino:
            qs = qs.filter(id_nino=nino)
        if estado:
            qs = qs.filter(estado=estado)
        if mes:
            qs = qs.filter(fecha__month=mes)
        if anio:
            qs = qs.filter(fecha__year=anio)

        return qs.order_by("-fecha")

    def get_serializer_class(self):
        return PagoListSerializer if self.action == "list" else PagoSerializer

    def destroy(self, request, *args, **kwargs):
        pago = self.get_object()
        pago.estado = "anulado"
        pago.activo = False
        pago.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["patch"], url_path="marcar-pagado")
    def marcar_pagado(self, request, pk=None):
        pago = self.get_object()
        if pago.estado == "pagado":
            return Response(
                {"detail": "Este pago ya fue registrado como pagado."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        pago.estado = "pagado"
        pago.save()
        return Response(PagoSerializer(pago).data)

    @action(detail=False, methods=["get"], url_path="resumen")
    def resumen(self, request):
        hoy = timezone.now().date()
        mes = int(request.query_params.get("mes", hoy.month))
        anio = int(request.query_params.get("anio", hoy.year))
        guarderia = self.get_guarderia()

        qs = Pago.objects.filter(fecha__month=mes, fecha__year=anio, activo=True)
        if guarderia:
            qs = qs.filter(id_guarderia=guarderia)

        total_pagado = qs.filter(estado="pagado").aggregate(s=Sum("total"))["s"] or 0

        return Response(
            {
                "mes": mes,
                "anio": anio,
                "total_pagado": float(total_pagado),
                "total_pagos": qs.filter(estado="pagado").count(),
                "pendientes": qs.filter(estado="pendiente").count(),
                "anulados": qs.filter(estado="anulado").count(),
            }
        )

    @action(detail=False, methods=["post"], url_path="generar-mensual")
    def generar_mensual(self, request):
        hoy = timezone.now().date()
        mes = request.data.get("mes", hoy.month)
        anio = request.data.get("anio", hoy.year)
        guarderia = self.get_guarderia()

        from apps.ninos.models import Nino

        ninos_qs = Nino.objects.filter(activo=True)
        if guarderia:
            ninos_qs = ninos_qs.filter(id_guarderia=guarderia)

        creados = 0
        for nino in ninos_qs:
            servicios_mensuales = NinoServicio.objects.filter(
                id_nino=nino,
                activo=True,
                id_servicio__tipo="mensual",
                id_servicio__activo=True,
            ).select_related("id_servicio")

            if not servicios_mensuales.exists():
                continue

            ya_existe = Pago.objects.filter(
                id_nino=nino,
                fecha__month=mes,
                fecha__year=anio,
                activo=True,
            ).exists()
            if ya_existe:
                continue

            total = sum(ns.id_servicio.precio for ns in servicios_mensuales)
            pago = Pago.objects.create(
                id_nino=nino,
                fecha=hoy,
                total=total,
                estado="pendiente",
                id_guarderia=guarderia,
            )
            for ns in servicios_mensuales:
                DetallePago.objects.create(
                    id_pago=pago,
                    id_servicio=ns.id_servicio,
                    monto=ns.id_servicio.precio,
                )
            creados += 1

        return Response(
            {
                "detail": f"Se generaron {creados} pagos pendientes.",
                "creados": creados,
                "mes": mes,
                "anio": anio,
            },
            status=status.HTTP_201_CREATED,
        )
