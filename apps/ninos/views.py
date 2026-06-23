import random

from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.servicios.brevo_service import BrevoEmailService
from .models import Nino, TutorNino, PersonaAutorizada, RetiroNino
from .serializers import (
    NinoSerializer,
    NinoListSerializer,
    TutorNinoSerializer,
    PersonaAutorizadaSerializer,
    PersonaAutorizadaListSerializer,
    VerificarCodigoSerializer,
    RegistrarRetiroSerializer,
    RetiroNinoSerializer,
)
from apps.guarderias.mixins import GuaderiaMixin


def enviar_codigo_a_tutores(nino, nombre_persona_autorizada, codigo_seguridad):
    vinculos = TutorNino.objects.select_related("id_tutor").filter(
        id_nino=nino,
        activo=True,
        id_tutor__activo=True,
    )
    tutores_con_email = [
        v.id_tutor
        for v in vinculos
        if v.id_tutor.email and str(v.id_tutor.email).strip()
    ]
    if not tutores_con_email:
        return {
            "enviados": 0,
            "detalle": "No hay tutores activos con email registrado.",
            "errores": [],
        }

    email_service = BrevoEmailService()
    enviados, errores = 0, []
    for tutor in tutores_con_email:
        try:
            email_service.send_codigo_seguridad(
                to_email=tutor.email,
                nombre_destinatario=tutor.nombre,
                nombre_nino=nino.nombre,
                nombre_persona_autorizada=nombre_persona_autorizada,
                codigo_seguridad=codigo_seguridad,
            )
            enviados += 1
        except Exception as e:
            errores.append(
                {"tutor": tutor.nombre, "email": tutor.email, "error": str(e)}
            )

    return {"enviados": enviados, "errores": errores}


def enviar_retiro_a_tutores(nino, persona, retiro):
    vinculos = TutorNino.objects.select_related("id_tutor").filter(
        id_nino=nino,
        activo=True,
        id_tutor__activo=True,
    )
    tutores_con_email = [
        v.id_tutor
        for v in vinculos
        if v.id_tutor.email and str(v.id_tutor.email).strip()
    ]
    if not tutores_con_email:
        return {
            "enviados": 0,
            "detalle": "No hay tutores activos con email registrado.",
            "errores": [],
        }

    email_service = BrevoEmailService()
    enviados, errores = 0, []
    fecha_hora = timezone.localtime(retiro.fecha_hora_retiro).strftime("%d/%m/%Y %H:%M")

    for tutor in tutores_con_email:
        try:
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px;">
                <h2>Hola {tutor.nombre}</h2>
                <p>Se registró el retiro del niño: <strong>{nino.nombre}</strong></p>
                <div style="padding: 18px; background: #f0fdf4; border: 1px solid #86efac; border-radius: 12px;">
                    <p><strong>Persona que retiró:</strong> {persona.nombre}</p>
                    <p><strong>CI:</strong> {persona.ci}</p>
                    <p><strong>Hora:</strong> {fecha_hora}</p>
                    <p><strong>Observación:</strong> {retiro.observacion or 'Sin observación'}</p>
                </div>
                <p>Si no reconoces esta acción, comunícate con la guardería.</p>
            </div>
            """
            text_content = (
                f"Hola {tutor.nombre},\n\n"
                f"Se registró el retiro de {nino.nombre}.\n"
                f"Persona: {persona.nombre} — CI: {persona.ci}\n"
                f"Hora: {fecha_hora}\n"
                f"Observación: {retiro.observacion or 'Sin observación'}\n"
            )
            email_service.send_email(
                to_email=tutor.email,
                subject=f"Retiro registrado de {nino.nombre}",
                html_content=html_content,
                text_content=text_content,
                to_name=tutor.nombre,
            )
            enviados += 1
        except Exception as e:
            errores.append(
                {"tutor": tutor.nombre, "email": tutor.email, "error": str(e)}
            )

    return {"enviados": enviados, "errores": errores}


class NinoViewSet(GuaderiaMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Nino.objects.filter(activo=True).order_by("nombre")
        # filtrar_por_guarderia aplica el filtro de tenant
        qs = self.filtrar_por_guarderia(qs)

        # Filtros adicionales opcionales
        nombre = self.request.query_params.get("nombre")
        if nombre:
            qs = qs.filter(nombre__icontains=nombre)
        return qs

    def get_serializer_class(self):
        return NinoListSerializer if self.action == "list" else NinoSerializer

    def destroy(self, request, *args, **kwargs):
        nino = self.get_object()
        nino.activo = False
        nino.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"], url_path="tutores")
    def tutores(self, request, pk=None):
        vinculos = TutorNino.objects.filter(id_nino=pk, activo=True).select_related(
            "id_tutor"
        )
        return Response(TutorNinoSerializer(vinculos, many=True).data)

    @action(detail=True, methods=["post"], url_path="vincular-tutor")
    def vincular_tutor(self, request, pk=None):
        nino = self.get_object()
        id_tutor = request.data.get("id_tutor")
        relacion = request.data.get("relacion", "").strip()

        if not id_tutor:
            return Response(
                {"detail": "id_tutor es requerido."}, status=status.HTTP_400_BAD_REQUEST
            )

        vinculo_existente = TutorNino.objects.filter(
            id_nino=nino, id_tutor_id=id_tutor
        ).first()
        if vinculo_existente:
            vinculo_existente.activo = True
            vinculo_existente.relacion = relacion
            vinculo_existente.save()
            return Response(
                TutorNinoSerializer(vinculo_existente).data, status=status.HTTP_200_OK
            )

        if TutorNino.objects.filter(id_nino=nino, activo=True).count() >= 2:
            return Response(
                {"detail": "Máximo tutores admitidos: 2."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        vinculo = TutorNino.objects.create(
            id_nino=nino,
            id_tutor_id=id_tutor,
            relacion=relacion,
            activo=True,
        )
        return Response(
            TutorNinoSerializer(vinculo).data, status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=["get"], url_path="buscar")
    def buscar(self, request):
        q = request.query_params.get("q", "")
        ninos = self.get_queryset().filter(nombre__icontains=q)[:10]
        return Response(NinoListSerializer(ninos, many=True).data)

    @action(detail=True, methods=["post"], url_path="registrar-retiro")
    def registrar_retiro(self, request, pk=None):
        nino = self.get_object()
        serializer = RegistrarRetiroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ci = serializer.validated_data["ci"]
        codigo = serializer.validated_data["codigo_seguridad"]
        observacion = serializer.validated_data.get("observacion")

        try:
            persona = PersonaAutorizada.objects.get(
                id_nino=nino,
                ci=ci,
                codigo_seguridad=codigo,
                activo=True,
            )
        except PersonaAutorizada.DoesNotExist:
            return Response(
                {
                    "detail": "CI o código de seguridad incorrectos.",
                    "autorizado": False,
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        hoy = timezone.now().date()
        if RetiroNino.objects.filter(
            id_nino=nino, fecha_hora_retiro__date=hoy
        ).exists():
            return Response(
                {"detail": "Este niño ya fue retirado hoy.", "autorizado": False},
                status=status.HTTP_400_BAD_REQUEST,
            )

        retiro = RetiroNino.objects.create(
            id_nino=nino,
            id_persona_autorizada=persona,
            registrado_por=request.user if request.user.is_authenticated else None,
            codigo_seguridad_usado=codigo,
            observacion=observacion,
        )

        correo = None
        try:
            correo = enviar_retiro_a_tutores(nino=nino, persona=persona, retiro=retiro)
        except Exception as e:
            correo = {"enviados": 0, "errores": [str(e)]}

        return Response(
            {
                "detail": "Retiro registrado correctamente.",
                "autorizado": True,
                "retiro": RetiroNinoSerializer(retiro).data,
                "correo": correo,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"], url_path="retiros")
    def retiros(self, request, pk=None):
        nino = self.get_object()
        retiros = RetiroNino.objects.filter(id_nino=nino).select_related(
            "id_persona_autorizada",
            "id_nino",
            "registrado_por",
        )
        return Response(RetiroNinoSerializer(retiros, many=True).data)


# ── Dashboard ─────────────────────────────────────────────────────────────────


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_resumen(request):
    from django.db.models import Sum, Count
    from django.db.models.functions import TruncDay
    from apps.asistencia.models import Asistencia
    from apps.salud.models import Salud
    from apps.servicios.models import Pago

    guarderia = getattr(request, "guarderia", None)
    hoy = timezone.now().date()
    mes_actual = hoy.month
    anio_actual = hoy.year

    # Base querysets filtrados por guardería
    ninos_qs = Nino.objects.filter(activo=True)
    asistencia_qs = Asistencia.objects.filter(activo=True)
    salud_qs = Salud.objects.filter(activo=True)
    pagos_qs = Pago.objects.filter(activo=True)

    if guarderia:
        ninos_qs = ninos_qs.filter(id_guarderia=guarderia)
        asistencia_qs = asistencia_qs.filter(id_guarderia=guarderia)
        salud_qs = salud_qs.filter(id_guarderia=guarderia)
        pagos_qs = pagos_qs.filter(id_guarderia=guarderia)

    total_ninos = ninos_qs.count()
    asistencia_hoy = asistencia_qs.filter(fecha=hoy, estado="presente").count()
    pagos_mes = pagos_qs.filter(
        fecha__month=mes_actual, fecha__year=anio_actual
    ).count()
    alertas_salud = salud_qs.filter(fecha=hoy).values("id_nino").distinct().count()

    pagos_grafico = [
        {
            "dia": p["dia"].strftime("%d/%m"),
            "total": float(p["total"] or 0),
            "cantidad": p["cantidad"],
        }
        for p in pagos_qs.filter(fecha__month=mes_actual, fecha__year=anio_actual)
        .annotate(dia=TruncDay("fecha"))
        .values("dia")
        .annotate(total=Sum("total"), cantidad=Count("id_pago"))
        .order_by("dia")
    ]

    return Response(
        {
            "total_ninos": total_ninos,
            "asistencia_hoy": asistencia_hoy,
            "pagos_mes": pagos_mes,
            "alertas_salud": alertas_salud,
            "pagos_grafico": pagos_grafico,
        }
    )


# ── Personas Autorizadas ──────────────────────────────────────────────────────


class PersonaAutorizadaViewSet(GuaderiaMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = PersonaAutorizada.objects.select_related("id_nino").filter(activo=True)

        # SOLUCIÓN: Quitamos self.filtrar_por_guarderia(...)
        guarderia_id = self.get_guarderia()
        if guarderia_id:
            qs = qs.filter(id_nino__id_guarderia=guarderia_id)

        nino = self.request.query_params.get("nino")
        if nino:
            qs = qs.filter(id_nino=nino)

        return qs.order_by("nombre")

    def get_serializer_class(self):
        return (
            PersonaAutorizadaListSerializer
            if self.action == "list"
            else PersonaAutorizadaSerializer
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        persona = serializer.save()

        if not persona.codigo_seguridad:
            persona.codigo_seguridad = str(random.randint(100000, 999999))
            persona.save()

        correo = None
        try:
            correo = enviar_codigo_a_tutores(
                nino=persona.id_nino,
                nombre_persona_autorizada=persona.nombre,
                codigo_seguridad=persona.codigo_seguridad,
            )
        except Exception as e:
            correo = {"enviados": 0, "errores": [str(e)]}

        return Response(
            {"codigo_seguridad": persona.codigo_seguridad, "correo": correo},
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, *args, **kwargs):
        persona = self.get_object()
        persona.activo = False
        persona.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"], url_path="verificar")
    def verificar(self, request):
        serializer = VerificarCodigoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ci = serializer.validated_data["ci"]
        codigo = serializer.validated_data["codigo_seguridad"]

        # Filtrar también por guardería
        guarderia = self.get_guarderia()
        qs = PersonaAutorizada.objects.select_related("id_nino").filter(
            ci=ci,
            codigo_seguridad=codigo,
            activo=True,
        )
        if guarderia:
            qs = qs.filter(id_nino__id_guarderia=guarderia)

        try:
            persona = qs.get()
            return Response(
                {
                    "autorizado": True,
                    "nombre": persona.nombre,
                    "ci": persona.ci,
                    "telefono": persona.telefono,
                    "nino": persona.id_nino.nombre,
                    "id_nino": persona.id_nino.id_nino,
                }
            )
        except PersonaAutorizada.DoesNotExist:
            return Response(
                {"autorizado": False, "detail": "CI o código incorrectos."},
                status=status.HTTP_403_FORBIDDEN,
            )

    @action(detail=False, methods=["get"], url_path="por-nino")
    def por_nino(self, request):
        nino_id = request.query_params.get("nino")
        if not nino_id:
            return Response(
                {"detail": 'Parámetro "nino" es requerido.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        personas = PersonaAutorizada.objects.filter(
            id_nino=nino_id, activo=True
        ).order_by("nombre")
        return Response(PersonaAutorizadaListSerializer(personas, many=True).data)
