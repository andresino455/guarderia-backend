from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TutorViewSet,mi_dashboard

router = DefaultRouter()

router.register(r'', TutorViewSet, basename='tutor')

urlpatterns = [
    path('mi_dashboard/', mi_dashboard, name='dashboard'),
    path('', include(router.urls))]