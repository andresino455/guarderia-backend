from django.db import models
from apps.tutores.models import Tutor


class Nino(models.Model):
    id_nino          = models.AutoField(primary_key=True)
    nombre           = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    edad             = models.IntegerField(blank=True, null=True)
    foto             = models.TextField(blank=True, null=True)
    info_medica      = models.TextField(blank=True, null=True)
    activo           = models.BooleanField(default=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'nino'

    def save(self, *args, **kwargs):
        # Calcular edad automáticamente
        if self.fecha_nacimiento:
            from django.utils import timezone
            hoy = timezone.now().date()
            self.edad = (
                hoy.year - self.fecha_nacimiento.year
                - ((hoy.month, hoy.day) 
                   (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class TutorNino(models.Model):
    id_tutor   = models.ForeignKey(
        Tutor, on_delete=models.CASCADE,
        db_column='id_tutor', related_name='ninos'
    )
    id_nino    = models.ForeignKey(
        Nino, on_delete=models.CASCADE,
        db_column='id_nino', related_name='tutores'
    )
    relacion   = models.CharField(max_length=50, blank=True, null=True)
    activo     = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table     = 'tutor_nino'
        unique_together = ('id_tutor', 'id_nino')

    def __str__(self):
        return f'{self.id_nino} — {self.id_tutor} ({self.relacion})'