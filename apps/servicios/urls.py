from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServicioViewSet, PagoViewSet

router = DefaultRouter()
router.register(r'servicios', ServicioViewSet, basename='servicio')
router.register(r'pagos',     PagoViewSet,     basename='pago')

urlpatterns = [path('', include(router.urls))]