from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crea superusuario de Django para acceder al admin"

    def handle(self, *args, **options):
        import os
        from django.contrib.auth.models import User

        email    = os.getenv("SUPER_EMAIL",    "super@guarderia.com")
        password = os.getenv("SUPER_PASSWORD", "12345")
        username = os.getenv("SUPER_USERNAME", "superadmin")

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(
                f"Superusuario ya existe: {username}"
            ))
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(
            f"Superusuario creado: {username} / {email}"
        ))