from django.db import models
from apps.niños.models import Nino


class Asistencia(models.Model):

    ESTADO_CHOICES = [
        ('presente', 'Presente'),
        ('ausente',  'Ausente'),
        ('tardanza', 'Tardanza'),
    ]

    id_asistencia = models.AutoField(primary_key=True)
    id_nino       = models.ForeignKey(
        Nino, on_delete=models.CASCADE,
        db_column='id_nino', related_name='asistencias'
    )
    fecha         = models.DateField()
    hora_ingreso  = models.TimeField(blank=True, null=True)
    hora_salida   = models.TimeField(blank=True, null=True)
    estado        = models.CharField(
        max_length=50, choices=ESTADO_CHOICES, default='presente'
    )
    activo        = models.BooleanField(default=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        db_table        = 'asistencia'
        unique_together = ('id_nino', 'fecha')  # un registro por niño por día

    def __str__(self):
        return f'{self.id_nino} — {self.fecha} ({self.estado})'