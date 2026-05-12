from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GuarderiaViewSet

router = DefaultRouter()
router.register(r'', GuarderiaViewSet, basename='guarderia')

urlpatterns = [path('', include(router.urls))]