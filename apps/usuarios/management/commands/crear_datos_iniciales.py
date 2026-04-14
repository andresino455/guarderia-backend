from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = 'Crea roles y usuario administrador inicial'

    def handle(self, *args, **options):
        from apps.usuarios.models import Rol, Usuario

        # ── Crear roles ────────────────────────────────────────────
        roles_iniciales = ['Administrador', 'Personal', 'Tutor']
        roles_creados   = []

        for nombre in roles_iniciales:
            rol, created = Rol.objects.get_or_create(nombre=nombre)
            if created:
                roles_creados.append(nombre)

        if roles_creados:
            self.stdout.write(self.style.SUCCESS(
                f'Roles creados: {", ".join(roles_creados)}'
            ))
        else:
            self.stdout.write('Roles ya existían, sin cambios.')

        # ── Crear usuario administrador inicial ────────────────────
        import os
        admin_email    = os.getenv('ADMIN_EMAIL',    'admin@guarderia.com')
        admin_password = os.getenv('ADMIN_PASSWORD', 'Admin1234!')
        admin_nombre   = os.getenv('ADMIN_NOMBRE',   'Administrador')

        if not Usuario.objects.filter(email=admin_email).exists():
            rol_admin = Rol.objects.get(nombre='Administrador')
            Usuario.objects.create(
                nombre=admin_nombre,
                email=admin_email,
                password=make_password(admin_password),
                id_rol=rol_admin,
                activo=True,
            )
            self.stdout.write(self.style.SUCCESS(
                f'Usuario admin creado: {admin_email}'
            ))
        else:
            self.stdout.write(f'Usuario {admin_email} ya existe, sin cambios.')