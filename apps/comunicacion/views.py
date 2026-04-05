from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q

from apps.usuarios.models import Usuario
from apps.usuarios.permissions import IsAdmin
from .models import Mensaje, Notificacion
from .serializers import (
    MensajeSerializer, MensajeListSerializer,
    NotificacionSerializer, NotificacionBulkSerializer,
)


def get_usuario_id(request):
    """Extrae el id_usuario del usuario autenticado."""

    return request.user.id_usuario

class MensajeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return MensajeListSerializer
        return MensajeSerializer

    def get_queryset(self):
        user_id = get_usuario_id(self.request)
        # Cada usuario solo ve sus propios mensajes
        return Mensaje.objects.filter(
            activo=True
        ).filter(
            Q(id_emisor=user_id) | Q(id_receptor=user_id)
        ).select_related('id_emisor', 'id_receptor').order_by('-fecha')

    def perform_create(self, serializer):
        user_id = get_usuario_id(self.request)
        serializer.save(id_emisor_id=user_id)

    def destroy(self, request, *args, **kwargs):
        mensaje        = self.get_object()
        mensaje.activo = False
        mensaje.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='conversacion')
    def conversacion(self, request):
        """
        GET /api/v1/comunicacion/mensajes/conversacion/?con=<id_usuario>
        Historial de mensajes entre el usuario autenticado y otro usuario.
        """
        user_id  = get_usuario_id(request)
        con_id   = request.query_params.get('con')

        if not con_id:
            return Response(
                {'detail': 'Parámetro "con" es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        mensajes = Mensaje.objects.filter(
            activo=True
        ).filter(
            Q(id_emisor=user_id,  id_receptor=con_id) |
            Q(id_emisor=con_id,   id_receptor=user_id)
        ).select_related('id_emisor', 'id_receptor').order_by('fecha')

        return Response(MensajeSerializer(mensajes, many=True).data)

    @action(detail=False, methods=['get'], url_path='no-leidos')
    def no_leidos(self, request):
        """GET /api/v1/comunicacion/mensajes/no-leidos/ — mensajes recibidos."""
        user_id  = get_usuario_id(request)
        mensajes = Mensaje.objects.filter(
            id_receptor=user_id, activo=True
        ).select_related('id_emisor').order_by('-fecha')

        return Response({
            'total':    mensajes.count(),
            'mensajes': MensajeListSerializer(mensajes, many=True).data,
        })


class NotificacionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class   = NotificacionSerializer

    def get_queryset(self):
        user_id = get_usuario_id(self.request)
        qs      = Notificacion.objects.filter(
            id_usuario=user_id, activo=True
        ).order_by('-fecha')

        leido = self.request.query_params.get('leido')
        if leido is not None:
            qs = qs.filter(leido=leido.lower() == 'true')

        return qs

    def destroy(self, request, *args, **kwargs):
        notif        = self.get_object()
        notif.activo = False
        notif.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['patch'], url_path='marcar-leido')
    def marcar_leido(self, request, pk=None):
        """PATCH /api/v1/comunicacion/notificaciones/{id}/marcar-leido/"""
        notif       = self.get_object()
        notif.leido = True
        notif.save()
        return Response(NotificacionSerializer(notif).data)

    @action(detail=False, methods=['patch'], url_path='marcar-todas-leidas')
    def marcar_todas_leidas(self, request):
        """PATCH /api/v1/comunicacion/notificaciones/marcar-todas-leidas/"""
        user_id = get_usuario_id(request)
        total   = Notificacion.objects.filter(
            id_usuario=user_id, leido=False, activo=True
        ).update(leido=True)
        return Response({'detail': f'{total} notificaciones marcadas como leídas.'})

    @action(detail=False, methods=['get'], url_path='no-leidas')
    def no_leidas(self, request):
        """GET /api/v1/comunicacion/notificaciones/no-leidas/ — contador."""
        user_id = get_usuario_id(request)
        total   = Notificacion.objects.filter(
            id_usuario=user_id, leido=False, activo=True
        ).count()
        return Response({'total_no_leidas': total})

    @action(
        detail=False, methods=['post'],
        url_path='enviar-masiva',
        permission_classes=[IsAuthenticated, IsAdmin]
    )
    def enviar_masiva(self, request):
        """
        POST /api/v1/comunicacion/notificaciones/enviar-masiva/
        Solo admin. Envía una notificación a múltiples usuarios.
        """
        serializer = NotificacionBulkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        usuarios_ids = serializer.validated_data['usuarios']
        mensaje      = serializer.validated_data['mensaje']
        usuarios     = Usuario.objects.filter(
            id_usuario__in=usuarios_ids, activo=True
        )

        creadas = Notificacion.objects.bulk_create([
            Notificacion(id_usuario=u, mensaje=mensaje)
            for u in usuarios
        ])

        return Response({
            'detail':  f'Notificación enviada a {len(creadas)} usuarios.',
            'enviadas': len(creadas),
        }, status=status.HTTP_201_CREATED)
