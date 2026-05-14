from django.urls import path
from . import views

urlpatterns = [
    path("descargar/",  views.descargar_backup,  name="descargar-backup"),
    path("restaurar/",  views.restaurar_backup,  name="restaurar-backup"),
]