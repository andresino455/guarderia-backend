from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NinoViewSet, dashboard_resumen, PersonaAutorizadaViewSet

router = DefaultRouter()
router.register(
    r"personas-autorizadas", PersonaAutorizadaViewSet, basename="persona-autorizada"
)
router.register(r'', NinoViewSet, basename='nino')

urlpatterns = [
    path('dashboard/', dashboard_resumen, name='dashboard-resumen'),
    path('', include(router.urls)),
]
