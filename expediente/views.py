from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Q
from .models import Paciente, NotaConsulta, RecetaDigital, OrdenReferencia
from .serializers import PacienteSerializer, NotaConsultaSerializer, RecetaDigitalSerializer, OrdenReferenciaSerializer, PacientePublicSerializer
from personal.permissions import IsDoctorOrAdmin # Necesitaremos definir este permiso

# --- Permisos: Asegurar que solo personal autenticado pueda usar esta API ---
# Nota: La clase IsDoctorOrAdmin la definiremos después del código de las vistas.

# 1. API para Buscar y Crear Pacientes (CU-A02.5 y CU-A02.1)
class PacienteListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PacienteSerializer
    # Permiso: Solo Médicos y Administradores (Recepción) pueden acceder
    permission_classes = [permissions.IsAuthenticated, IsDoctorOrAdmin] 

    def get_queryset(self):
        """
        Permite buscar pacientes por nombre, CURP o expediente (id). (RF-M03)
        """
        queryset = Paciente.objects.all()
        query = self.request.query_params.get('search', None)
        
        if query:
            queryset = queryset.filter(
                Q(CURP__icontains=query) |
                Q(nombre__icontains=query) |
                Q(apellidos__icontains=query) |
                Q(id__iexact=query)
            )
        return queryset

# 2. API para Crear Nota de Consulta (Actualizar Expediente - RF-020)
class NotaConsultaCreateAPIView(generics.CreateAPIView):
    serializer_class = NotaConsultaSerializer
    # Permiso: Solo Médicos (MG/Especialidad) o Enfermería (Urgencias) (RB-010)
    permission_classes = [permissions.IsAuthenticated, IsDoctorOrAdmin] 

    def perform_create(self, serializer):
        """
        Asegura que la nota se guarde con el personal autenticado. (RF-020)
        """
        # Asegurar que el usuario autenticado (self.request.user) se guarda como 'medico'
        serializer.save(medico=self.request.user)

# 3. API para Crear Receta Digital (Emitir Receta - RF-026)
class RecetaCreateAPIView(generics.CreateAPIView):
    """
    API para la Emisión de Recetas Digitales (RF-025, RB-012).
    """
    queryset = RecetaDigital.objects.all()
    serializer_class = RecetaDigitalSerializer
    # Solo Médicos pueden emitir recetas
    permission_classes = [permissions.IsAuthenticated, IsDoctorOrAdmin]

    def perform_create(self, serializer):
        # Asegura que el médico de la receta sea el usuario autenticado
        # (Se pasa al serializador para el método create())
        serializer.save(medico=self.request.user)

class OrdenReferenciaCreateAPIView(generics.CreateAPIView):
    """
    API para que el Médico General emita una orden de referencia (RF-017, RB-006).
    """
    queryset = OrdenReferencia.objects.all()
    serializer_class = OrdenReferenciaSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctorOrAdmin]

    def perform_create(self, serializer):
        # Asegura que el médico emisor sea el usuario autenticado
        serializer.save(medico_general=self.request.user)

class NotaConsultaListAPIView(generics.ListAPIView):
    """
    API para listar el historial de Notas de Consulta de un paciente.
    """
    serializer_class = NotaConsultaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filtra solo las notas del paciente especificado en la URL
        paciente_id = self.kwargs['paciente_id']
        return NotaConsulta.objects.filter(paciente_id=paciente_id).order_by('-fecha_registro')

class RecetaDigitalListAPIView(generics.ListAPIView):
    """
    API para listar el historial de Recetas Digitales de un paciente.
    """
    serializer_class = RecetaDigitalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filtra solo las recetas del paciente especificado en la URL
        paciente_id = self.kwargs['paciente_id']
        return RecetaDigital.objects.filter(paciente_id=paciente_id).order_by('-fecha_emision')

class PacienteLookupAPIView(generics.ListAPIView):
    """
    API pública para que el PACIENTE valide su CURP y obtenga su ID. (CU-PAC-001)
    """
    serializer_class = PacientePublicSerializer
    # PERMISO CRÍTICO: Permitir a CUALQUIERA acceder para validar el CURP.
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        query = self.request.query_params.get('curp', None)
        # Búsqueda estricta por el CURP
        if query:
            return Paciente.objects.filter(CURP__iexact=query)
        return Paciente.objects.none() # No devolver nada si no hay CURP