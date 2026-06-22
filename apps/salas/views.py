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
from apps.guarderias.mixins import GuaderiaMixin


class PersonalViewSet(GuaderiaMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Personal.objects.filter(activo=True)
        qs = self.filtrar_por_guarderia(qs)

        tipo = self.request.query_params.get("tipo")
        if tipo:
            qs = qs.filter(tipo=tipo)

        return qs

    def get_serializer_class(self):
        return PersonalListSerializer if self.action == "list" else PersonalSerializer

    def destroy(self, request, *args, **kwargs):
        personal = self.get_object()
        personal.activo = False
        personal.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"], url_path="salas")
    def salas(self, request, pk=None):
        vinculos = PersonalSala.objects.filter(
            id_personal=pk, activo=True
        ).select_related("id_sala")
        return Response(PersonalSalaSerializer(vinculos, many=True).data)


class SalaViewSet(GuaderiaMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Sala.objects.filter(activo=True)
        qs = self.filtrar_por_guarderia(qs)
        return qs

    def get_serializer_class(self):
        return SalaListSerializer if self.action == "list" else SalaSerializer

    def destroy(self, request, *args, **kwargs):
        sala = self.get_object()
        sala.activo = False
        sala.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="asignar-personal")
    def asignar_personal(self, request, pk=None):
        sala = self.get_object()
        id_personal = request.data.get("id_personal")

        if not id_personal:
            return Response(
                {"detail": "id_personal es requerido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verificar que el personal pertenece a la misma guardería
        guarderia = self.get_guarderia()
        if guarderia:
            if not Personal.objects.filter(
                id_personal=id_personal,
                id_guarderia=guarderia,
                activo=True,
            ).exists():
                return Response(
                    {"detail": "El personal no pertenece a esta guardería."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        vinculo, created = PersonalSala.objects.get_or_create(
            id_personal_id=id_personal,
            id_sala=sala,
            defaults={"activo": True},
        )
        if not created:
            vinculo.activo = True
            vinculo.save()

        return Response(
            PersonalSalaSerializer(vinculo).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="asignar-nino")
    def asignar_nino(self, request, pk=None):
        sala = self.get_object()
        id_nino = request.data.get("id_nino")

        if not id_nino:
            return Response(
                {"detail": "id_nino es requerido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verificar que el niño pertenece a la misma guardería
        guarderia = self.get_guarderia()
        if guarderia:
            from apps.ninos.models import Nino

            if not Nino.objects.filter(
                id_nino=id_nino,
                id_guarderia=guarderia,
                activo=True,
            ).exists():
                return Response(
                    {"detail": "El niño no pertenece a esta guardería."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        # Desactivar asignación previa del niño
        AsignacionNinoSala.objects.filter(id_nino_id=id_nino, activo=True).update(
            activo=False
        )

        serializer = AsignacionNinoSalaSerializer(
            data={
                "id_nino": id_nino,
                "id_sala": sala.id_sala,
                "fecha": timezone.now().date(),
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="ninos")
    def ninos(self, request, pk=None):
        asignaciones = (
            AsignacionNinoSala.objects.filter(id_sala=pk, activo=True)
            .select_related("id_nino")
            .order_by("id_nino__nombre")
        )
        return Response(AsignacionNinoSalaSerializer(asignaciones, many=True).data)

    @action(detail=False, methods=["get"], url_path="resumen")
    def resumen(self, request):
        guarderia = self.get_guarderia()
        salas = Sala.objects.filter(activo=True)
        if guarderia:
            salas = salas.filter(id_guarderia=guarderia)

        return Response(
            [
                {
                    "id_sala": s.id_sala,
                    "nombre": s.nombre,
                    "edad_min": s.edad_min,
                    "edad_max": s.edad_max,
                    "cupo_max": s.cupo_max,
                    "ocupacion": s.ocupacion,
                    "cupo_disponible": s.cupo_disponible,
                    "porcentaje": round(
                        (s.ocupacion / s.cupo_max * 100) if s.cupo_max else 0, 1
                    ),
                }
                for s in salas
            ]
        )
