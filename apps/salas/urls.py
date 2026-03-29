from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PersonalViewSet, SalaViewSet

router = DefaultRouter()
router.register(r'personal', PersonalViewSet, basename='personal')
router.register(r'',         SalaViewSet,     basename='sala')

urlpatterns = [path('', include(router.urls))]