from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.apps import apps


TABLAS_AUDITADAS = [
    'nino', 'tutor', 'usuario', 'sala', 'personal',
    'asistencia', 'salud', 'medicacion', 'alimentacion',
    'servicio', 'pago', 'actividad',
]


def registrar_bitacora(sender, instance, accion, **kwargs):
    """Crea un registro en Bitacora para el modelo dado."""
    try:
        from apps.auditoria.models import Bitacora
        tabla = sender._meta.db_table

        if tabla not in TABLAS_AUDITADAS:
            return

        pk = getattr(instance, instance._meta.pk.name, None)

        Bitacora.objects.create(
            accion=accion,
            tabla=tabla,
            id_registro=pk,
            descripcion=f'{accion} en {tabla} — registro {pk}',
        )
    except Exception:
        pass  # Nunca romper la operación principal por un error de auditoría


@receiver(post_save)
def on_save(sender, instance, created, **kwargs):
    accion = 'INSERT' if created else 'UPDATE'
    registrar_bitacora(sender, instance, accion)


@receiver(post_delete)
def on_delete(sender, instance, **kwargs):
    registrar_bitacora(sender, instance, 'DELETE')