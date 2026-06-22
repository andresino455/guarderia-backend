from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

TABLAS_AUDITADAS = [
    "nino",
    "tutor",
    "usuario",
    "sala",
    "personal",
    "asistencia",
    "salud",
    "medicacion",
    "alimentacion",
    "servicio",
    "pago",
    "actividad",
]


def _obtener_guarderia(instance):
    """
    Intenta obtener la guardería del objeto para registrarla en la bitácora.
    Busca el campo id_guarderia directamente o via relaciones.
    """
    # Directo en el modelo
    if hasattr(instance, "id_guarderia_id") and instance.id_guarderia_id:
        return instance.id_guarderia

    # Via nino (ej: asistencia, actividad, salud)
    if hasattr(instance, "id_nino") and instance.id_nino:
        nino = instance.id_nino
        if hasattr(nino, "id_guarderia") and nino.id_guarderia:
            return nino.id_guarderia

    return None


def registrar_bitacora(sender, instance, accion):
    """Crea un registro en Bitacora para el modelo dado."""
    try:
        from apps.auditoria.models import Bitacora

        tabla = sender._meta.db_table
        if tabla not in TABLAS_AUDITADAS:
            return

        pk = getattr(instance, instance._meta.pk.name, None)
        guarderia = _obtener_guarderia(instance)

        Bitacora.objects.create(
            accion=accion,
            tabla=tabla,
            id_registro=pk,
            descripcion=f"{accion} en {tabla} — registro {pk}",
            id_guarderia=guarderia,
        )
    except Exception:
        # Nunca romper la operación principal por error de auditoría
        pass


@receiver(post_save)
def on_save(sender, instance, created, **kwargs):
    accion = 'INSERT' if created else 'UPDATE'
    registrar_bitacora(sender, instance, accion)


@receiver(post_delete)
def on_delete(sender, instance, **kwargs):
    registrar_bitacora(sender, instance, 'DELETE')
