from django.db import models
from apps.ninos.models import Nino

class Servicio(models.Model):

    TIPO_CHOICES = [
        ('mensual',    'Mensual'),
        ('eventual',   'Eventual'),
        ('alimentacion', 'Alimentación'),
        ('transporte', 'Transporte'),
        ('otro',       'Otro'),
    ]

    id_servicio  = models.AutoField(primary_key=True)
    nombre       = models.CharField(max_length=100)
    descripcion  = models.TextField(blank=True, null=True)
    precio       = models.DecimalField(max_digits=10, decimal_places=2)
    tipo         = models.CharField(max_length=50, choices=TIPO_CHOICES, default='mensual')
    activo       = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'servicio'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} (Bs. {self.precio})'


class NinoServicio(models.Model):
    id_nino     = models.ForeignKey(
        Nino, on_delete=models.CASCADE,
        db_column='id_nino', related_name='servicios'
    )
    id_servicio = models.ForeignKey(
        Servicio, on_delete=models.CASCADE,
        db_column='id_servicio', related_name='ninos'
    )
    activo      = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table        = 'nino_servicio'
        unique_together = ('id_nino', 'id_servicio')

    def __str__(self):
        return f'{self.id_nino} — {self.id_servicio}'


class Pago(models.Model):

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('pagado',    'Pagado'),
        ('anulado',   'Anulado'),
    ]

    id_pago    = models.AutoField(primary_key=True)
    id_nino    = models.ForeignKey(
        Nino, on_delete=models.CASCADE,
        db_column='id_nino', related_name='pagos'
    )
    fecha      = models.DateField()
    total      = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado     = models.CharField(
        max_length=50, choices=ESTADO_CHOICES, default='pendiente'
    )
    activo     = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pago'
        ordering = ['-fecha']

    def __str__(self):
        return f'Pago {self.id_pago} — {self.id_nino} ({self.estado})'


class DetallePago(models.Model):
    id_detalle  = models.AutoField(primary_key=True)
    id_pago     = models.ForeignKey(
        Pago, on_delete=models.CASCADE,
        db_column='id_pago', related_name='detalles'
    )
    id_servicio = models.ForeignKey(
        Servicio, on_delete=models.CASCADE,
        db_column='id_servicio', related_name='detalles_pago'
    )
    monto       = models.DecimalField(max_digits=10, decimal_places=2)
    activo      = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'detalle_pago'

    def __str__(self):
        return f'Detalle {self.id_detalle} — {self.id_servicio} Bs.{self.monto}'
