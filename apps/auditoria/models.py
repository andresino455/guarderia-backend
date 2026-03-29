from django.db import models
from apps.usuarios.models import Usuario


class Bitacora(models.Model):

    ACCION_CHOICES = [
        ('INSERT', 'Inserción'),
        ('UPDATE', 'Actualización'),
        ('DELETE', 'Eliminación'),
    ]

    id_bitacora = models.AutoField(primary_key=True)
    id_usuario  = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL,
        null=True, db_column='id_usuario',
        related_name='bitacoras'
    )
    accion      = models.CharField(max_length=50, choices=ACCION_CHOICES)
    tabla       = models.CharField(max_length=50)
    id_registro = models.IntegerField(null=True, blank=True)
    fecha       = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'bitacora'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.accion} en {self.tabla} por {self.id_usuario} ({self.fecha})'


class HistorialCambios(models.Model):
    id_historial   = models.AutoField(primary_key=True)
    tabla          = models.CharField(max_length=50)
    id_registro    = models.IntegerField()
    campo          = models.CharField(max_length=50)
    valor_anterior = models.TextField(blank=True, null=True)
    valor_nuevo    = models.TextField(blank=True, null=True)
    fecha          = models.DateTimeField(auto_now_add=True)
    id_usuario     = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL,
        null=True, db_column='id_usuario',
        related_name='historial_cambios'
    )

    class Meta:
        db_table = 'historial_cambios'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.tabla}.{self.campo} [{self.id_registro}] ({self.fecha})'