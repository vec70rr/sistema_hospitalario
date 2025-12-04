from django.urls import path
from .views import (PacienteListCreateAPIView, NotaConsultaCreateAPIView, RecetaCreateAPIView, OrdenReferenciaCreateAPIView, 
                    NotaConsultaListAPIView, RecetaDigitalListAPIView, PacienteLookupAPIView)

urlpatterns = [
    # /api/expediente/pacientes/ -> GET: Buscar, POST: Crear Paciente
    path('pacientes/', PacienteListCreateAPIView.as_view(), name='paciente-list-create'),
    
    # /api/expediente/notas/ -> POST: Crear Nota de Consulta
    path('notas/', NotaConsultaCreateAPIView.as_view(), name='nota-create'),

    # /api/expediente/recetas/ -> POST: Emitir Receta Digital 
    path('recetas/', RecetaCreateAPIView.as_view(), name='receta-create'),

    # /api/expediente/ordenes/ -> POST: Emitir Orden de Referencia
    path('ordenes/', OrdenReferenciaCreateAPIView.as_view(), name='orden-referencia-create'),

    # Historial de Lectura: /api/expediente/historial/notas/{paciente_id}/
    path('historial/notas/<int:paciente_id>/', NotaConsultaListAPIView.as_view(), name='historial-notas'),
    
    # Historial de Lectura: /api/expediente/historial/recetas/{paciente_id}/
    path('historial/recetas/<int:paciente_id>/', RecetaDigitalListAPIView.as_view(), name='historial-recetas'),

    # RUTA PÚBLICA: Para que el paciente valide su CURP
    path('lookup/', PacienteLookupAPIView.as_view(), name='paciente-lookup'),
]