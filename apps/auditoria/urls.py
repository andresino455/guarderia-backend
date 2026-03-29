from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BitacoraViewSet, HistorialCambiosViewSet

router = DefaultRouter()
router.register(r'bitacora',  BitacoraViewSet,        basename='bitacora')
router.register(r'historial', HistorialCambiosViewSet, basename='historial')

urlpatterns = [path('', include(router.urls))]