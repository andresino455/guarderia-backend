from django.urls import path
from .views import procesar_voz

urlpatterns = [
    path('voz/', procesar_voz, name='reporte-voz'),
]