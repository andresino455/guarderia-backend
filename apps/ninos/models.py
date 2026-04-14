from django.db import models
from apps.tutores.models import Tutor
from apps.usuarios.models import Usuario

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
        if self.fecha_nacimiento:
            from django.utils import timezone
            hoy = timezone.now().date()
        
            # 1. Diferencia inicial de años
            edad = hoy.year - self.fecha_nacimiento.year
        
            # 2. Ajuste: Si hoy es antes del cumpleaños de este año, resta 1
            # Creamos una fecha para el cumple de este año
            cumple_este_ano = self.fecha_nacimiento.replace(year=hoy.year)
        
            if hoy < cumple_este_ano:
                edad -= 1
            
            # 3. Validación de seguridad (mínimo 0 años)
            self.edad = max(0, edad)
        
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


class PersonaAutorizada(models.Model):
    id_persona = models.AutoField(primary_key=True)
    id_nino = models.ForeignKey(
        Nino,
        on_delete=models.CASCADE,
        db_column="id_nino",
        related_name="personas_autorizadas",
    )
    nombre = models.CharField(max_length=100)
    ci = models.CharField(max_length=20)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    codigo_seguridad = models.CharField(max_length=50)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "persona_autorizada"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} (CI: {self.ci}) — autorizado para {self.id_nino}"


class RetiroNino(models.Model):
    id_retiro = models.AutoField(primary_key=True)

    id_nino = models.ForeignKey(
        Nino, on_delete=models.CASCADE, db_column="id_nino", related_name="retiros"
    )

    id_persona_autorizada = models.ForeignKey(
        PersonaAutorizada,
        on_delete=models.CASCADE,
        db_column="id_persona_autorizada",
        related_name="retiros",
    )

    registrado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="retiros_registrados",
    )

    codigo_seguridad_usado = models.CharField(max_length=50)
    observacion = models.TextField(blank=True, null=True)
    fecha_hora_retiro = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "retiro_nino"
        ordering = ["-fecha_hora_retiro"]

    def __str__(self):
        return (
            f"Retiro de {self.id_nino.nombre} por {self.id_persona_autorizada.nombre}"
        )
