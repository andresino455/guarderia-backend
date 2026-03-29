from django.db import models
from apps.salas.models import Sala


class Camara(models.Model):
    id_camara  = models.AutoField(primary_key=True)
    id_sala    = models.ForeignKey(
        Sala, on_delete=models.CASCADE,
        db_column='id_sala', related_name='camaras'
    )
    url_stream = models.TextField()
    activo     = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'camara'

    def __str__(self):
        return f'Cámara {self.id_camara} — {self.id_sala}'