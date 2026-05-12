from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Guarderia
from .serializers import GuarderiaSerializer


class GuarderiaViewSet(viewsets.ModelViewSet):
    queryset           = Guarderia.objects.filter(activo=True)
    serializer_class   = GuarderiaSerializer
    # Solo superadmin puede crear guarderías
    # Para simplificar, dejamos AllowAny en create
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    def destroy(self, request, *args, **kwargs):
        g        = self.get_object()
        g.activo = False
        g.save()
        return Response(status=status.HTTP_204_NO_CONTENT)