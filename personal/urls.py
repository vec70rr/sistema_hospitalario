from django.urls import path
from .views import LoginAPIView, EspecialidadListAPIView

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),

    # Ruta para el catálogo
    path('especialidades/', EspecialidadListAPIView.as_view(), name='especialidad-list'),
]