class GuaderiaMixin:
    """
    Mixin para ViewSets. Filtra automáticamente por guardería
    y asigna la guardería al crear objetos.
    """

    guarderia_field = 'id_guarderia'

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request, 'guarderia') and self.request.guarderia:
            return qs.filter(**{self.guarderia_field: self.request.guarderia})
        return qs

    def perform_create(self, serializer):
        if hasattr(self.request, 'guarderia') and self.request.guarderia:
            serializer.save(**{self.guarderia_field: self.request.guarderia})
        else:
            serializer.save()