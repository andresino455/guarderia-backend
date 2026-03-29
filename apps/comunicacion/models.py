from django.db import models
from apps.usuarios.models import Usuario


class Mensaje(models.Model):
    id_mensaje  = models.AutoField(primary_key=True)
    id_emisor   = models.ForeignKey(
        Usuario, on_delete=models.CASCADE,
        db_column='id_emisor', related_name='mensajes_enviados'
    )
    id_receptor = models.ForeignKey(
        Usuario, on_delete=models.CASCADE,
        db_column='id_receptor', related_name='mensajes_recibidos'
    )
    mensaje     = models.TextField()
    fecha       = models.DateTimeField(auto_now_add=True)
    activo      = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mensaje'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.id_emisor} → {self.id_receptor} ({self.fecha})'


class Notificacion(models.Model):
    id_notificacion = models.AutoField(primary_key=True)
    id_usuario      = models.ForeignKey(
        Usuario, on_delete=models.CASCADE,
        db_column='id_usuario', related_name='notificaciones'
    )
    mensaje         = models.TextField()
    fecha           = models.DateTimeField(auto_now_add=True)
    leido           = models.BooleanField(default=False)
    activo          = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notificacion'
        ordering = ['-fecha']

    def __str__(self):
        return f'Notif → {self.id_usuario} (leído: {self.leido})'