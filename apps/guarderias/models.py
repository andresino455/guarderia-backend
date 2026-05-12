from django.db import models


class Guarderia(models.Model):
    id_guarderia = models.AutoField(primary_key=True)
    nombre       = models.CharField(max_length=100)
    direccion    = models.TextField(blank=True, null=True)
    telefono     = models.CharField(max_length=20, blank=True, null=True)
    email        = models.EmailField(blank=True, null=True)
    logo         = models.TextField(blank=True, null=True)
    activo       = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'guarderia'

    def __str__(self):
        return self.nombre