# agenda/urls.py
from django.urls import path
from .views import (AutoAsignarCitaAPIView, CancelarCitaAPIView, ReagendarCitaAPIView, CitasPacienteListAPIView, 
                    OpcionesCitaListAPIView, CrearCitaSlotElegidoAPIView)

urlpatterns = [
    # /api/agenda/solicitar/ -> POST: Autoasignación de Cita MG
    path('solicitar/', AutoAsignarCitaAPIView.as_view(), name='cita-auto-asignar'),

    # /api/agenda/cancelar/ -> POST: Cancelar Cita MG
    path('cancelar/', CancelarCitaAPIView.as_view(), name='cita-cancelar'),

    # /api/agenda/reagendar/ -> POST: Reagendar Cita MG
    path('reagendar/', ReagendarCitaAPIView.as_view(), name='cita-reagendar'),

    # RUTA DE LECTURA: /api/agenda/citas/paciente/{id}/
    path('citas/paciente/<int:paciente_id>/', CitasPacienteListAPIView.as_view(), name='citas-paciente-list'),

    # RUTA DE LECTURA DE OPCIONES: /api/agenda/opciones/
    path('opciones/', OpcionesCitaListAPIView.as_view(), name='opciones-list'),

    path('crear_elegido/', CrearCitaSlotElegidoAPIView.as_view(), name='crear-slot-elegido'),
]