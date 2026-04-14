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


def enviar_codigo_a_tutores(nino, nombre_persona_autorizada, codigo_seguridad):
    vinculos = TutorNino.objects.select_related("id_tutor").filter(
        id_nino=nino,
        activo=True,
        id_tutor__activo=True,
    )

    tutores_con_email = [
        vinculo.id_tutor
        for vinculo in vinculos
        if vinculo.id_tutor.email and str(vinculo.id_tutor.email).strip()
    ]

    if not tutores_con_email:
        return {
            "enviados": 0,
            "detalle": "No hay tutores activos con email registrado.",
            "errores": [],
        }

    email_service = BrevoEmailService()
    enviados = 0
    errores = []

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
                {
                    "tutor": tutor.nombre,
                    "email": tutor.email,
                    "error": str(e),
                }
            )

    return {
        "enviados": enviados,
        "errores": errores,
    }


def enviar_retiro_a_tutores(nino, persona, retiro):
    vinculos = TutorNino.objects.select_related("id_tutor").filter(
        id_nino=nino,
        activo=True,
        id_tutor__activo=True,
    )

    tutores_con_email = [
        vinculo.id_tutor
        for vinculo in vinculos
        if vinculo.id_tutor.email and str(vinculo.id_tutor.email).strip()
    ]

    if not tutores_con_email:
        return {
            "enviados": 0,
            "detalle": "No hay tutores activos con email registrado.",
            "errores": [],
        }

    email_service = BrevoEmailService()
    enviados = 0
    errores = []

    fecha_hora = timezone.localtime(retiro.fecha_hora_retiro).strftime("%d/%m/%Y %H:%M")

    for tutor in tutores_con_email:
        try:
            asunto = f"Retiro registrado de {nino.nombre}"

            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; background: #f8fafc; border-radius: 16px;">
                <div style="background: #ffffff; border-radius: 16px; padding: 32px; border: 1px solid #e5e7eb;">
                    <h2 style="color: #0f172a; margin-top: 0;">Hola {tutor.nombre}</h2>

                    <p style="color: #334155; font-size: 15px; line-height: 1.6;">
                        Se registró el retiro del niño:
                    </p>

                    <p style="font-size: 20px; font-weight: bold; color: #1e293b; margin: 8px 0 18px;">
                        {nino.nombre}
                    </p>

                    <div style="margin: 18px 0; padding: 18px; background: #f0fdf4; border: 1px solid #86efac; border-radius: 12px;">
                        <p style="margin: 0 0 8px; color: #166534;"><strong>Persona que retiró:</strong> {persona.nombre}</p>
                        <p style="margin: 0 0 8px; color: #166534;"><strong>CI:</strong> {persona.ci}</p>
                        <p style="margin: 0 0 8px; color: #166534;"><strong>Hora:</strong> {fecha_hora}</p>
                        <p style="margin: 0; color: #166534;"><strong>Observación:</strong> {retiro.observacion or 'Sin observación'}</p>
                    </div>

                    <p style="color: #475569; font-size: 14px; line-height: 1.6;">
                        Si no reconoces esta acción, comunícate inmediatamente con la guardería.
                    </p>

                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 24px 0;" />

                    <p style="color: #64748b; font-size: 12px; margin-bottom: 0;">
                        Este es un mensaje automático del sistema de guardería.
                    </p>
                </div>
            </div>
            """

            text_content = (
                f"Hola {tutor.nombre},\n\n"
                f"Se registró el retiro de {nino.nombre}.\n"
                f"Persona que retiró: {persona.nombre}\n"
                f"CI: {persona.ci}\n"
                f"Hora: {fecha_hora}\n"
                f"Observación: {retiro.observacion or 'Sin observación'}\n\n"
                f"Si no reconoces esta acción, comunícate con la guardería."
            )

            email_service.send_email(
                to_email=tutor.email,
                subject=asunto,
                html_content=html_content,
                text_content=text_content,
                to_name=tutor.nombre,
            )
            enviados += 1
        except Exception as e:
            errores.append(
                {
                    "tutor": tutor.nombre,
                    "email": tutor.email,
                    "error": str(e),
                }
            )

    return {
        "enviados": enviados,
        "errores": errores,
    }


class NinoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Nino.objects.filter(activo=True).order_by("nombre")

    def get_serializer_class(self):
        if self.action == "list":
            return NinoListSerializer
        return NinoSerializer

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
                {"detail": "id_tutor es requerido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        vinculo_existente = TutorNino.objects.filter(
            id_nino=nino,
            id_tutor_id=id_tutor,
        ).first()

        if vinculo_existente:
            vinculo_existente.activo = True
            vinculo_existente.relacion = relacion
            vinculo_existente.save()

            return Response(
                TutorNinoSerializer(vinculo_existente).data,
                status=status.HTTP_200_OK,
            )

        total_tutores_activos = TutorNino.objects.filter(
            id_nino=nino,
            activo=True,
        ).count()

        if total_tutores_activos >= 2:
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
            TutorNinoSerializer(vinculo).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"], url_path="buscar")
    def buscar(self, request):
        q = request.query_params.get("q", "")
        ninos = Nino.objects.filter(activo=True, nombre__icontains=q)[:10]
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
                    "detail": "CI o código de seguridad incorrectos para este niño.",
                    "autorizado": False,
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        hoy = timezone.now().date()

        ya_retirado_hoy = RetiroNino.objects.filter(
            id_nino=nino,
            fecha_hora_retiro__date=hoy,
        ).exists()

        if ya_retirado_hoy:
            return Response(
                {
                    "detail": "Este niño ya fue retirado hoy y no puede registrarse otro retiro.",
                    "autorizado": False,
                },
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
            correo = enviar_retiro_a_tutores(
                nino=nino,
                persona=persona,
                retiro=retiro,
            )
        except Exception as e:
            correo = {
                "enviados": 0,
                "errores": [str(e)],
            }

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

from .models import PersonaAutorizada
from .serializers import (
    PersonaAutorizadaSerializer,
    PersonaAutorizadaListSerializer,
    VerificarCodigoSerializer,
)


class PersonaAutorizadaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 1. Guardar persona autorizada
        persona = serializer.save()

        # 2. Generar código (si no lo haces en serializer)
        if not persona.codigo_seguridad:
            persona.codigo_seguridad = str(random.randint(100000, 999999))
            persona.save()

        # 3. Enviar correo 🔥
        try:
            correo = enviar_codigo_a_tutores(
                nino=persona.id_nino,
                nombre_persona_autorizada=persona.nombre,
                codigo_seguridad=persona.codigo_seguridad,
            )
        except Exception as e:
            correo = {
                "enviados": 0,
                "errores": [str(e)],
            }

        # 4. Respuesta como tu frontend espera
        return Response(
            {
                "codigo_seguridad": persona.codigo_seguridad,
                "correo": correo,
            },
            status=status.HTTP_201_CREATED,
        )
    def get_queryset(self):
        qs = PersonaAutorizada.objects.select_related("id_nino").filter(activo=True)
        nino = self.request.query_params.get("nino")
        if nino:
            qs = qs.filter(id_nino=nino)
        return qs.order_by("nombre")

    def get_serializer_class(self):
        if self.action == "list":
            return PersonaAutorizadaListSerializer
        return PersonaAutorizadaSerializer

    def destroy(self, request, *args, **kwargs):
        persona = self.get_object()
        persona.activo = False
        persona.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"], url_path="verificar")
    def verificar(self, request):
        """
        POST /api/v1/ninos/personas-autorizadas/verificar/
        Verifica si una persona puede recoger a un niño
        usando su CI y código de seguridad.

        Body: { "ci": "...", "codigo_seguridad": "..." }
        """
        serializer = VerificarCodigoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ci = serializer.validated_data["ci"]
        codigo = serializer.validated_data["codigo_seguridad"]

        try:
            persona = PersonaAutorizada.objects.select_related("id_nino").get(
                ci=ci, codigo_seguridad=codigo, activo=True
            )
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
                {
                    "autorizado": False,
                    "detail": "CI o código de seguridad incorrectos.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

    @action(detail=False, methods=["get"], url_path="por-nino")
    def por_nino(self, request):
        """
        GET /api/v1/ninos/personas-autorizadas/por-nino/?nino=<id>
        Lista todas las personas autorizadas de un niño específico.
        """
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



