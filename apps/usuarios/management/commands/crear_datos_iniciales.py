from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crea guardería inicial, roles y admin — solo para setup inicial"

    def handle(self, *args, **options):
        import os
        from apps.guarderias.models import Guarderia
        from apps.usuarios.models import Rol, Usuario

        guarderia_nombre = os.getenv("GUARDERIA_NOMBRE", "Guardería Principal")

        guarderia, g_created = Guarderia.objects.get_or_create(
            nombre=guarderia_nombre,
            defaults={"activo": True},
        )
        if g_created:
            self.stdout.write(
                self.style.SUCCESS(f"Guardería creada: {guarderia_nombre}")
            )
        else:
            self.stdout.write(f"Guardería ya existe: {guarderia_nombre}")

        # Roles asociados a esta guardería
        roles_iniciales = ["Administrador", "Personal", "Tutor"]
        for nombre in roles_iniciales:
            _, created = Rol.objects.get_or_create(
                nombre=nombre,
                id_guarderia=guarderia,
                defaults={"activo": True},
            )
            if created:
                self.stdout.write(f"  Rol creado: {nombre}")

        # Admin inicial
        admin_email = os.getenv("ADMIN_EMAIL", "admin@guarderia.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "Admin1234!")
        admin_nombre = os.getenv("ADMIN_NOMBRE", "Administrador")

        rol_admin = Rol.objects.get(nombre="Administrador", id_guarderia=guarderia)

        if not Usuario.objects.filter(email=admin_email).exists():
            usuario = Usuario(
                nombre=admin_nombre,
                email=admin_email,
                password=admin_password,  # save() lo hashea
                id_rol=rol_admin,
                id_guarderia=guarderia,
                activo=True,
            )
            usuario.save()
            self.stdout.write(self.style.SUCCESS(f"Admin creado: {admin_email}"))
        else:
            usuario = Usuario.objects.get(email=admin_email)
            usuario.password = admin_password
            usuario.id_guarderia = guarderia
            usuario.save()
            self.stdout.write(self.style.WARNING(f"Admin actualizado: {admin_email}"))
