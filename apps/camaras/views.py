from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.usuarios.permissions import IsAdmin, IsPersonal
from .models import Camara
from .serializers import CamaraSerializer, CamaraListSerializer


class CamaraViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs   = Camara.objects.select_related('id_sala').filter(activo=True)
        sala = self.request.query_params.get('sala')
        if sala:
            qs = qs.filter(id_sala=sala)
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return CamaraListSerializer
        return CamaraSerializer

    def destroy(self, request, *args, **kwargs):
        camara        = self.get_object()
        camara.activo = False
        camara.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='por-sala')
    def por_sala(self, request):
        """
        GET /api/v1/camaras/por-sala/
        Devuelve todas las salas con sus cámaras agrupadas.
        """
        from apps.salas.models import Sala
        salas   = Sala.objects.filter(activo=True)
        result  = []

        for sala in salas:
            camaras = Camara.objects.filter(id_sala=sala, activo=True)
            result.append({
                'id_sala':    sala.id_sala,
                'sala_nombre': sala.nombre,
                'camaras':    CamaraListSerializer(camaras, many=True).data,
            })

        return Response(result)

    @action(detail=True, methods=['get'], url_path='stream')
    def stream(self, request, pk=None):
        """
        GET /api/v1/camaras/{id}/stream/
        Devuelve la URL de stream de la cámara.
        Solo personal y admin pueden acceder.
        """
        camara = self.get_object()
        return Response({
            'id_camara':  camara.id_camara,
            'sala':       camara.id_sala.nombre,
            'url_stream': camara.url_stream,
        })