from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = "Crea guardería, roles y admin inicial"

    def handle(self, *args, **options):
        import os
        from apps.guarderias.models import Guarderia
        from apps.usuarios.models import Rol, Usuario
        from django.contrib.auth.hashers import make_password

        # 1. Crear guardería inicial
        guarderia_nombre = os.getenv("GUARDERIA_NOMBRE", "Guardería Principal")
        guarderia, g_created = Guarderia.objects.get_or_create(
            nombre=guarderia_nombre, defaults={"activo": True}
        )
        if g_created:
            self.stdout.write(
                self.style.SUCCESS(f"Guardería creada: {guarderia_nombre}")
            )

        # 2. Crear roles vinculados a la guardería
        roles_iniciales = ["Administrador", "Personal", "Tutor"]
        for nombre in roles_iniciales:
            Rol.objects.get_or_create(
                nombre=nombre, id_guarderia=guarderia, defaults={"activo": True}
            )
        self.stdout.write(self.style.SUCCESS("Roles creados."))

        # 3. Crear admin
        admin_email = os.getenv("ADMIN_EMAIL", "admin@guarderia.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "Admin1234!")
        admin_nombre = os.getenv("ADMIN_NOMBRE", "Administrador")

        if not Usuario.objects.filter(email=admin_email).exists():
            rol_admin = Rol.objects.get(nombre="Administrador", id_guarderia=guarderia)
            Usuario.objects.create(
                nombre=admin_nombre,
                email=admin_email,
                password=make_password(admin_password),
                id_rol=rol_admin,
                id_guarderia=guarderia,
                activo=True,
            )
            self.stdout.write(self.style.SUCCESS(f"Admin creado: {admin_email}"))
