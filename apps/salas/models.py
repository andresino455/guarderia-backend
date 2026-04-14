from django.db import models
from apps.ninos.models import Nino

class Personal(models.Model):

    TIPO_CHOICES = [
        ('maestra',    'Maestra'),
        ('auxiliar',   'Auxiliar'),
        ('enfermera',  'Enfermera'),
        ('cocinera',   'Cocinera'),
        ('seguridad',  'Seguridad'),
        ('otro',       'Otro'),
    ]

    id_personal = models.AutoField(primary_key=True)
    nombre      = models.CharField(max_length=100)
    telefono    = models.CharField(max_length=20, blank=True, null=True)
    tipo        = models.CharField(max_length=50, choices=TIPO_CHOICES, default='maestra')
    activo      = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'personal'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.tipo})'


class Sala(models.Model):
    id_sala   = models.AutoField(primary_key=True)
    nombre    = models.CharField(max_length=100)
    edad_min  = models.IntegerField()
    edad_max  = models.IntegerField()
    cupo_max  = models.IntegerField()
    activo    = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sala'
        ordering = ['edad_min']

    def __str__(self):
        return f'{self.nombre} ({self.edad_min}-{self.edad_max} años)'

    @property
    def cupo_disponible(self):
        ocupados = self.asignaciones.filter(activo=True).count()
        return self.cupo_max - ocupados

    @property
    def ocupacion(self):
        return self.asignaciones.filter(activo=True).count()


class PersonalSala(models.Model):
    id_personal = models.ForeignKey(
        Personal, on_delete=models.CASCADE,
        db_column='id_personal', related_name='salas'
    )
    id_sala     = models.ForeignKey(
        Sala, on_delete=models.CASCADE,
        db_column='id_sala', related_name='personal'
    )
    activo      = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table        = 'personal_sala'
        unique_together = ('id_personal', 'id_sala')

    def __str__(self):
        return f'{self.id_personal} → {self.id_sala}'


class AsignacionNinoSala(models.Model):
    id_asignacion = models.AutoField(primary_key=True)
    id_nino       = models.ForeignKey(
        Nino, on_delete=models.CASCADE,
        db_column='id_nino', related_name='asignaciones_sala'
    )
    id_sala       = models.ForeignKey(
        Sala, on_delete=models.CASCADE,
        db_column='id_sala', related_name='asignaciones'
    )
    fecha         = models.DateField()
    activo        = models.BooleanField(default=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'asignacion_nino_sala'

    def __str__(self):
        return f'{self.id_nino} → {self.id_sala} ({self.fecha})'
