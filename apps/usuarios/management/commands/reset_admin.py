from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Resetea la contraseña del admin"

    def handle(self, *args, **options):
        import os
        from apps.usuarios.models import Usuario
        from django.contrib.auth.hashers import make_password

        email = os.getenv("ADMIN_EMAIL", "admin@guarderia.com")
        password = os.getenv("ADMIN_PASSWORD", "Admin1234!")

        try:
            u = Usuario.objects.get(email=email)
            # Bypasear el save() del modelo usando update()
            # para evitar el doble hasheo
            Usuario.objects.filter(email=email).update(
                password=make_password(password)
            )
            self.stdout.write(self.style.SUCCESS(
                f"Contraseña reseteada para {email}"
            ))
        except Usuario.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Usuario {email} no encontrado"))