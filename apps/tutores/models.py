from django.db import models
from apps.usuarios.models import Usuario


class Tutor(models.Model):
    id_tutor    = models.AutoField(primary_key=True)
    nombre      = models.CharField(max_length=100)
    ci          = models.CharField(max_length=20)
    telefono    = models.CharField(max_length=20)
    direccion   = models.TextField(blank=True, null=True)
    email       = models.CharField(max_length=100, blank=True, null=True)
    activo      = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tutor'

    def __str__(self):
        return f'{self.nombre} (CI: {self.ci})'


class UsuarioTutor(models.Model):
    id_usuario  = models.ForeignKey(
        Usuario, on_delete=models.CASCADE,
        db_column='id_usuario', related_name='tutores'
    )
    id_tutor    = models.ForeignKey(
        Tutor, on_delete=models.CASCADE,
        db_column='id_tutor', related_name='usuarios'
    )
    activo      = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'usuario_tutor'
        unique_together = ('id_usuario', 'id_tutor')

    def __str__(self):
        return f'{self.id_usuario} → {self.id_tutor}'