class GuaderiaMixin:
    """
    Mixin para ViewSets que filtra y asigna id_guarderia automáticamente.

    La guardería se obtiene en este orden:
      1. request.guarderia  (seteado por el middleware si llegó a tiempo)
      2. request.user.id_guarderia (fallback directo desde el usuario JWT)
    """

    guarderia_field = "id_guarderia"

    def get_guarderia(self):
        """
        Retorna la guardería del request actual.
        Usa el middleware si está disponible, sino cae al usuario directamente.
        """
        # Primero intentar desde el middleware
        guarderia = getattr(self.request, "guarderia", None)
        if guarderia:
            return guarderia

        # Fallback: leer directo del usuario autenticado por DRF
        usuario = getattr(self.request, "user", None)
        if usuario and hasattr(usuario, "id_guarderia"):
            return usuario.id_guarderia

        return None

    def filtrar_por_guarderia(self, qs):
        """Filtra un queryset por la guardería del usuario autenticado."""
        guarderia = self.get_guarderia()
        if guarderia:
            return qs.filter(**{self.guarderia_field: guarderia})
        return qs

    def get_queryset(self):
        qs = super().get_queryset()
        return self.filtrar_por_guarderia(qs)

    def perform_create(self, serializer):
        guarderia = self.get_guarderia()
        kwargs = {}
        if guarderia:
            kwargs[self.guarderia_field] = guarderia
        serializer.save(**kwargs)

    def perform_update(self, serializer):
        serializer.save()
