from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MensajeViewSet, NotificacionViewSet

router = DefaultRouter()
router.register(r'mensajes',       MensajeViewSet,       basename='mensaje')
router.register(r'notificaciones', NotificacionViewSet,  basename='notificacion')

urlpatterns = [path('', include(router.urls))]