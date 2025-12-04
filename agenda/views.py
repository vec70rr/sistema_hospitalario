from django.shortcuts import render

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Q, F
from django.utils import timezone
from datetime import timedelta, time, datetime
import calendar

from personal.models import Personal, Especialista
from expediente.models import Paciente
from .models import Agenda, Cita
from .serializers import SolicitudCitaSerializer, CancelarCitaSerializer, ReagendarCitaSerializer, CitaReadSerializer, SlotSeleccionadoSerializer

def obtener_opciones_disponibles(min_options=3):
    """
    Genera una lista de slots de 30 minutos disponibles a partir de mañana,
    buscando en las agendas de los Médicos Generales (MG).
    """
    opciones = []
    hoy = timezone.now().date()
    manana = hoy + timedelta(days=1)
    
    # Obtener IDs de Médicos Generales
    medicos_generales_ids = Personal.objects.filter(rol='MEDICO').exclude(
        id__in=Especialista.objects.values('medico_id')
    ).values_list('id', flat=True)
    
    agendas_mg = Agenda.objects.filter(medico_id__in=medicos_generales_ids).order_by('dia')
    
    if not agendas_mg.exists():
        return False # No hay agendas configuradas

    dias_a_buscar = 14 # Limitar la búsqueda a 2 semanas
    for i in range(dias_a_buscar):
        fecha_actual = manana + timedelta(days=i)
        dia_semana_num = fecha_actual.weekday()

        agendas_del_dia = agendas_mg.filter(dia=dia_semana_num)

        for agenda in agendas_del_dia:
            inicio_bloque = timezone.make_aware(datetime.combine(fecha_actual, agenda.hora_inicio))
            fin_bloque = timezone.make_aware(datetime.combine(fecha_actual, agenda.hora_fin))
            
            slot_actual = inicio_bloque
            while slot_actual + timedelta(minutes=30) <= fin_bloque:
                
                # Criterio de Disponibilidad: SOLO si NO está PENDIENTE o CONFIRMADA
                cita_ocupada = Cita.objects.filter(
                    fecha_hora=slot_actual,
                    agenda__medico=agenda.medico,
                    estado__in=['PENDIENTE', 'CONFIRMADA']
                ).exists()
                
                if not cita_ocupada:
                    # Slot disponible encontrado
                    opciones.append({
                        "agenda_id": agenda.id,
                        "medico_nombre": agenda.medico.get_full_name(),
                        "consultorio": agenda.consultorio,
                        "fecha_hora": slot_actual.strftime("%Y-%m-%d %H:%M:%S")
                    })
                    
                    # Devolvemos un mínimo de opciones para la UI (RB-005 sugiere >3)
                    if len(opciones) >= min_options:
                        return opciones 
                        
                slot_actual += timedelta(minutes=30)
                
    return opciones # Devuelve todas las opciones si no alcanzó el mínimo

def intentar_autoasignar_cita(paciente_id):
    """
    Contiene la lógica central de búsqueda del primer slot MG disponible.
    Devuelve un Response (201, 404) simulado o el objeto Cita si es exitoso.
    """
    paciente = Paciente.objects.get(id=paciente_id)
    
    hoy = timezone.now().date()
    manana = hoy + timedelta(days=1)
    
    # Obtener Agendas de MÉDICOS GENERALES (MG)
    medicos_generales_ids = Personal.objects.filter(rol='MEDICO').exclude(
        id__in=Especialista.objects.values('medico_id')
    ).values_list('id', flat=True)
    
    agendas_mg = Agenda.objects.filter(medico_id__in=medicos_generales_ids).order_by('dia')
    
    if not agendas_mg.exists():
        return Response({"error": "E-P02", "message": "No hay agendas de Medicina General configuradas."}, status=status.HTTP_404_NOT_FOUND)

    # Iterar día por día
    dias_a_buscar = 14
    for i in range(dias_a_buscar):
        fecha_actual = manana + timedelta(days=i)
        dia_semana_num = fecha_actual.weekday()
        agendas_del_dia = agendas_mg.filter(dia=dia_semana_num)

        for agenda in agendas_del_dia:
            inicio_bloque = timezone.make_aware(datetime.combine(fecha_actual, agenda.hora_inicio))
            fin_bloque = timezone.make_aware(datetime.combine(fecha_actual, agenda.hora_fin))
            
            # Generar slots de 30 minutos
            slot_actual = inicio_bloque
            while slot_actual + timedelta(minutes=30) <= fin_bloque:
                
                cita_existente = Cita.objects.filter(
                    fecha_hora=slot_actual,
                    agenda__medico=agenda.medico,
                    estado__in=['PENDIENTE', 'CONFIRMADA']
                ).exists()
                
                if not cita_existente:
                    # ¡Slot encontrado! Crear la cita.
                    nueva_cita = Cita.objects.create(
                        agenda=agenda,
                        paciente=paciente,
                        fecha_hora=slot_actual,
                        tipo_cita='MG',
                        estado='PENDIENTE'
                    )
                    # Devolvemos la Cita para procesarla en la vista
                    return nueva_cita 
                        
                slot_actual += timedelta(minutes=30)

    # Si no se encuentra slot
    return None

class AutoAsignarCitaAPIView(generics.CreateAPIView):
    """
    API para la Solicitud de Cita (CU-PAC-002).
    Implementa la lógica de autoasignación de primer slot disponible (RF-013, RB-003).
    """
    serializer_class = SolicitudCitaSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        paciente_id = serializer.validated_data['paciente_id']
        
        nueva_cita = intentar_autoasignar_cita(paciente_id)
        
        if nueva_cita is False:
            return Response({"error": "E-P02", "message": "No hay agendas de Medicina General configuradas."}, status=status.HTTP_404_NOT_FOUND)
        
        if nueva_cita:
            # Respuesta detallada de la cita asignada (CU-PAC-002)
            return Response({
                "message": "Cita asignada automáticamente.",
                "cita_id": nueva_cita.id,
                "fecha_hora": nueva_cita.fecha_hora.strftime("%Y-%m-%d %H:%M"),
                "medico": nueva_cita.agenda.medico.get_full_name(),
                "consultorio": nueva_cita.agenda.consultorio 
            }, status=status.HTTP_201_CREATED)
        else:
            # Si nueva_cita es None
            return Response({"error": "E-P02", "message": "No se encontraron slots disponibles para la cita."}, status=status.HTTP_404_NOT_FOUND)

class CancelarCitaAPIView(generics.UpdateAPIView):
    """
    API para la Cancelación de Cita (CU-PAC-004).
    Implementa la lógica de las 2 horas y la restricción a solo MG (RB-004).
    """
    queryset = Cita.objects.all()
    serializer_class = CancelarCitaSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['post'] # Usamos POST para la acción de cancelar

    def post(self, request, *args, **kwargs):
        # 1. Validar usando el serializador (verifica MG y las 2 horas)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cita_id = serializer.validated_data['cita_id']
        
        try:
            cita = Cita.objects.get(id=cita_id)
        except Cita.DoesNotExist:
            return Response({"error": "Cita no encontrada."}, status=status.HTTP_404_NOT_FOUND)
            
        # 2. Si la validación pasa (faltan >= 2 horas), se cancela (RB-004)
        cita.estado = 'CANCELADA'
        cita.save()
        
        return Response({
            "message": "Cita cancelada exitosamente.",
            "cita_id": cita.id,
            "fecha_hora": cita.fecha_hora.strftime("%Y-%m-%d %H:%M")
        }, status=status.HTTP_200_OK)

class ReagendarCitaAPIView(generics.CreateAPIView):
    """
    API para Reagendar Cita (CU-PAC-005).
    Implica: 1. Cancelar cita actual. 2. Autoasignar nueva (RB-005).
    """
    serializer_class = ReagendarCitaSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cita_id = serializer.validated_data['cita_id']
        
        cita_original = Cita.objects.get(id=cita_id)
        
        # 1. Cancelar la cita original (RB-005)
        cita_original.estado = 'CANCELADA'
        cita_original.save()

        # 2. Intentar Autoasignar una nueva cita
        nueva_cita = intentar_autoasignar_cita(cita_original.paciente.id)
        
        if nueva_cita:
            # Reagendación exitosa (201 Created)
            return Response({
                "message": "Cita reagendada exitosamente. La cita anterior fue cancelada.",
                "cita_original_id": cita_id,
                "cita_id": nueva_cita.id,
                "fecha_hora": nueva_cita.fecha_hora.strftime("%Y-%m-%d %H:%M"),
                "medico": nueva_cita.agenda.medico.get_full_name(),
                "consultorio": nueva_cita.agenda.consultorio
            }, status=status.HTTP_201_CREATED)
        else:
            # No se encontraron slots disponibles (E-P02), pero la original ya está cancelada.
            # (202 Accepted indica que la cancelación sí ocurrió, pero la reasignación falló)
            return Response({
                "message": "Cita original cancelada. Error: No se encontraron slots para reasignar automáticamente.",
                "error": "E-P02",
                "cita_original_id": cita_id
            }, status=status.HTTP_202_ACCEPTED)

class CitasPacienteListAPIView(generics.ListAPIView):
    """
    API para listar todas las citas de un paciente específico (CU-PAC-003).
    """
    serializer_class = CitaReadSerializer
    # NOTA: Solo pacientes autenticados/logeados (sin token) pueden ver esto.
    # Dado que el Paciente se autentica por CURP, mantenemos AllowAny, 
    # pero el frontend debe pasar el ID.
    permission_classes = [permissions.AllowAny] 

    def get_queryset(self):
        paciente_id = self.kwargs['paciente_id']
        return Cita.objects.filter(paciente_id=paciente_id).order_by('fecha_hora')

class OpcionesCitaListAPIView(generics.ListAPIView):
    """
    API para devolver las opciones de slots disponibles para reagendar (RB-005).
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        opciones = obtener_opciones_disponibles(min_options=5)
        
        if not opciones or opciones is False:
            return Response({"error": "E-P02", "message": "No hay slots de Medicina General disponibles."}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(opciones, status=status.HTTP_200_OK)

class CrearCitaSlotElegidoAPIView(generics.CreateAPIView):
    """
    API final para crear una cita con un slot elegido por el paciente (CU-PAC-005 final).
    """
    serializer_class = SlotSeleccionadoSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        data = serializer.validated_data
        
        # Recuperar objetos
        paciente = Paciente.objects.get(id=data['paciente_id'])
        agenda = Agenda.objects.get(id=data['agenda_id'])
        
        # Crear la cita final (tipo MG)
        nueva_cita = Cita.objects.create(
            agenda=agenda,
            paciente=paciente,
            fecha_hora=data['fecha_hora'],
            tipo_cita='MG',
            estado='PENDIENTE' 
        )
        return nueva_cita
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        nueva_cita = self.perform_create(serializer)
        
        # Respuesta detallada
        return Response({
            "message": "Cita asignada exitosamente.",
            "cita_id": nueva_cita.id,
            "fecha_hora": nueva_cita.fecha_hora.strftime("%Y-%m-%d %H:%M"),
            "medico": nueva_cita.agenda.medico.get_full_name(),
            "consultorio": nueva_cita.agenda.consultorio 
        }, status=status.HTTP_201_CREATED)