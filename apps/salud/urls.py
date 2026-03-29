from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SaludViewSet, MedicacionViewSet, AlimentacionViewSet

router = DefaultRouter()
router.register(r'registros',    SaludViewSet,        basename='salud')
router.register(r'medicacion',   MedicacionViewSet,   basename='medicacion')
router.register(r'alimentacion', AlimentacionViewSet, basename='alimentacion')

urlpatterns = [path('', include(router.urls))]