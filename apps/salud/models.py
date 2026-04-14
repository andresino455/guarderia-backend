from django.db import models
from apps.ninos.models import Nino

class Salud(models.Model):
    id_salud      = models.AutoField(primary_key=True)
    id_nino       = models.ForeignKey(
        Nino, on_delete=models.CASCADE,
        db_column='id_nino', related_name='registros_salud'
    )
    fecha         = models.DateField()
    sintomas      = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    activo        = models.BooleanField(default=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'salud'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.id_nino} — {self.fecha}'


class Medicacion(models.Model):
    id_medicacion = models.AutoField(primary_key=True)
    id_nino       = models.ForeignKey(
        Nino, on_delete=models.CASCADE,
        db_column='id_nino', related_name='medicaciones'
    )
    medicamento   = models.CharField(max_length=100)
    dosis         = models.CharField(max_length=50)
    hora          = models.TimeField()
    activo        = models.BooleanField(default=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'medicacion'

    def __str__(self):
        return f'{self.id_nino} — {self.medicamento} {self.dosis}'


class Alimentacion(models.Model):
    id_alimentacion = models.AutoField(primary_key=True)
    id_nino         = models.ForeignKey(
        Nino, on_delete=models.CASCADE,
        db_column='id_nino', related_name='alimentaciones'
    )
    tipo_comida     = models.CharField(max_length=100)
    horario         = models.TimeField()
    observaciones   = models.TextField(blank=True, null=True)
    activo          = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'alimentacion'

    def __str__(self):
        return f'{self.id_nino} — {self.tipo_comida} a las {self.horario}'
