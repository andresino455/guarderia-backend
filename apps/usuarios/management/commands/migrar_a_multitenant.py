"""
Management command: python manage.py migrar_a_multitenant

Ejecutar UNA SOLA VEZ después de desplegar los cambios multi-tenant.
"""
from django.core.management.base import BaseCommand
from django.db import transaction


MODELOS = [
    ('ninos',        'Nino'),
    ('tutores',      'Tutor'),
    ('salas',        'Sala'),
    ('salas',        'Personal'),
    ('asistencia',   'Asistencia'),
    ('salud',        'Salud'),
    ('salud',        'Medicacion'),
    ('salud',        'Alimentacion'),
    ('servicios',    'Servicio'),
    ('servicios',    'Pago'),
    ('actividades',  'Actividad'),
    ('camaras',      'Camara'),
    ('comunicacion', 'Mensaje'),
    ('comunicacion', 'Notificacion'),
]


class Command(BaseCommand):
    help = 'Migra datos existentes al modelo multi-tenant'

    def handle(self, *args, **options):
        from apps.guarderias.models import Guarderia

        guarderias = Guarderia.objects.filter(activo=True)

        if not guarderias.exists():
            self.stdout.write(self.style.ERROR(
                'No hay guarderías registradas. Creá una primero.'
            ))
            return

        if guarderias.count() > 1:
            self.stdout.write(self.style.WARNING(
                f'Hay {guarderias.count()} guarderías. '
                f'Se usará la primera para registros sin guardería.'
            ))

        guarderia_default = guarderias.first()
        self.stdout.write(
            f'Guardería por defecto: {guarderia_default.nombre} '
            f'(id={guarderia_default.id_guarderia})'
        )

        with transaction.atomic():
            self._migrar_roles(guarderia_default)
            self._migrar_usuarios(guarderia_default)

            for app_label, model_name in MODELOS:
                self._migrar_modelo(app_label, model_name, guarderia_default)

        self.stdout.write(self.style.SUCCESS('✓ Migración multi-tenant completada.'))

    def _migrar_roles(self, guarderia_default):
        from apps.usuarios.models import Rol
        count = Rol.objects.filter(id_guarderia__isnull=True).update(
            id_guarderia=guarderia_default
        )
        self.stdout.write(f'  Roles sin guardería actualizados: {count}')

    def _migrar_usuarios(self, guarderia_default):
        from apps.usuarios.models import Usuario
        count = Usuario.objects.filter(id_guarderia__isnull=True).update(
            id_guarderia=guarderia_default
        )
        self.stdout.write(f'  Usuarios sin guardería actualizados: {count}')

    def _migrar_modelo(self, app_label, model_name, guarderia_default):
        try:
            from django.apps import apps
            Model = apps.get_model(app_label, model_name)

            if not hasattr(Model, 'id_guarderia'):
                self.stdout.write(f'  {model_name}: no tiene campo id_guarderia, omitido.')
                return

            count = Model.objects.filter(id_guarderia__isnull=True).update(
                id_guarderia=guarderia_default
            )
            self.stdout.write(f'  {model_name}: {count} registros actualizados.')

        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  {model_name}: {e}'))