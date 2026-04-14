from django.db import models
from apps.ninos.models import Nino

class Actividad(models.Model):

    TIPO_CHOICES = [
        ('pedagogica',  'Pedagógica'),
        ('recreativa',  'Recreativa'),
        ('deportiva',   'Deportiva'),
        ('artistica',   'Artística'),
        ('social',      'Social'),
        ('otro',        'Otro'),
    ]

    id_actividad = models.AutoField(primary_key=True)
    id_nino      = models.ForeignKey(
        Nino, on_delete=models.CASCADE,
        db_column='id_nino', related_name='actividades'
    )
    tipo         = models.CharField(max_length=50, choices=TIPO_CHOICES)
    descripcion  = models.TextField()
    fecha        = models.DateField()
    activo       = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'actividad'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.id_nino} — {self.tipo} ({self.fecha})'
