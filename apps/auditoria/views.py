from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.usuarios.permissions import IsAdmin
from .models import Bitacora, HistorialCambios
from .serializers import BitacoraSerializer, HistorialCambiosSerializer


class BitacoraViewSet(viewsets.ReadOnlyModelViewSet):
    """Solo lectura — la bitácora no se edita manualmente."""
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class   = BitacoraSerializer

    def get_queryset(self):
        qs      = Bitacora.objects.select_related('id_usuario').all()
        tabla   = self.request.query_params.get('tabla')
        accion  = self.request.query_params.get('accion')
        usuario = self.request.query_params.get('usuario')
        desde   = self.request.query_params.get('desde')
        hasta   = self.request.query_params.get('hasta')

        if tabla:
            qs = qs.filter(tabla=tabla)
        if accion:
            qs = qs.filter(accion=accion)
        if usuario:
            qs = qs.filter(id_usuario=usuario)
        if desde:
            qs = qs.filter(fecha__date__gte=desde)
        if hasta:
            qs = qs.filter(fecha__date__lte=hasta)

        return qs.order_by('-fecha')

    @action(detail=False, methods=['get'], url_path='resumen')
    def resumen(self, request):
        """GET /api/v1/auditoria/bitacora/resumen/ — conteo por tabla y acción."""
        from django.db.models import Count
        por_tabla  = Bitacora.objects.values('tabla').annotate(
            total=Count('id_bitacora')
        ).order_by('-total')
        por_accion = Bitacora.objects.values('accion').annotate(
            total=Count('id_bitacora')
        ).order_by('-total')

        return Response({
            'total_registros': Bitacora.objects.count(),
            'por_tabla':       list(por_tabla),
            'por_accion':      list(por_accion),
        })


class HistorialCambiosViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class   = HistorialCambiosSerializer

    def get_queryset(self):
        qs    = HistorialCambios.objects.select_related('id_usuario').all()
        tabla = self.request.query_params.get('tabla')
        campo = self.request.query_params.get('campo')
        pk    = self.request.query_params.get('id_registro')

        if tabla:
            qs = qs.filter(tabla=tabla)
        if campo:
            qs = qs.filter(campo=campo)
        if pk:
            qs = qs.filter(id_registro=pk)

        return qs.order_by('-fecha')