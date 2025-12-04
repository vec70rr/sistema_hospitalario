from rest_framework import serializers
from .models import Cita, Agenda
from expediente.models import Paciente
from django.utils import timezone

class SolicitudCitaSerializer(serializers.Serializer):
    """
    Serializador de entrada para la solicitud de cita.
    Solo necesita el ID del paciente, ya que la asignación es automática.
    """
    paciente_id = serializers.IntegerField(write_only=True)
    
    def validate_paciente_id(self, value):
        try:
            Paciente.objects.get(id=value)
        except Paciente.DoesNotExist:
            # Aunque la autenticación del paciente es por CURP, la BD usa el ID.
            # Este error simula que el paciente no está registrado.
            raise serializers.ValidationError("Paciente no encontrado. Asegúrese de estar registrado.")
        return value

class CancelarCitaSerializer(serializers.Serializer):
    """
    Serializador de entrada para la cancelación.
    """
    cita_id = serializers.IntegerField(write_only=True)
    
    def validate_cita_id(self, value):
        try:
            cita = Cita.objects.get(id=value)
        except Cita.DoesNotExist:
            raise serializers.ValidationError("Cita no encontrada.")

        # Lógica para verificar si es una cita de Especialidad (no cancelable por el paciente)
        if cita.tipo_cita == 'ESP':
            raise serializers.ValidationError("La cancelación no aplica a citas de Especialidad (RB-004).")

        # Lógica de las 2 horas (RB-004)
        tiempo_restante = cita.fecha_hora - timezone.now()
        horas_restantes = tiempo_restante.total_seconds() / 3600
        
        if horas_restantes < 2:
            # Error E-P03 (Cancelación fuera de tiempo)
            raise serializers.ValidationError("Cancelación fuera de tiempo. Debe hacerse con al menos 2 horas de anticipación (E-P03).") 
            
        if cita.estado == 'CANCELADA':
            raise serializers.ValidationError("La cita ya está cancelada.")
            
        return value

class ReagendarCitaSerializer(serializers.Serializer):
    """
    Serializador de entrada para reagendar. Valida que solo sea MG.
    """
    cita_id = serializers.IntegerField(write_only=True)
    
    def validate_cita_id(self, value):
        try:
            cita = Cita.objects.get(id=value)
        except Cita.DoesNotExist:
            raise serializers.ValidationError("Cita no encontrada.")

        # Reagendar solo aplica a MG (RB-005, E-P04)
        if cita.tipo_cita == 'ESP':
            raise serializers.ValidationError("Operación de reagendar no disponible para citas de Especialidad (E-P04).")

        if cita.estado == 'CANCELADA':
            raise serializers.ValidationError("No se puede reagendar una cita ya cancelada.")
            
        return value

class CitaReadSerializer(serializers.ModelSerializer):
    # Campo de lectura para mostrar el consultorio y médico de la Agenda
    consultorio = serializers.ReadOnlyField(source='agenda.consultorio')
    medico_nombre = serializers.ReadOnlyField(source='agenda.medico.get_full_name')

    class Meta:
        model = Cita
        fields = ['id', 'fecha_hora', 'tipo_cita', 'estado', 'consultorio', 'medico_nombre']

class SlotSeleccionadoSerializer(serializers.Serializer):
    """ Serializador para crear una cita con slot elegido por el paciente. """
    paciente_id = serializers.IntegerField()
    agenda_id = serializers.IntegerField()
    fecha_hora = serializers.DateTimeField()
    
    # Validación simple: Asegurar que el slot elegido esté dentro de la Agenda.
    def validate(self, data):
        try:
            agenda = Agenda.objects.get(id=data['agenda_id'])
        except Agenda.DoesNotExist:
            raise serializers.ValidationError("Agenda no válida.")

        # Verificar si la fecha_hora está ya ocupada por otra cita activa
        cita_ocupada = Cita.objects.filter(
            fecha_hora=data['fecha_hora'],
            agenda__medico=agenda.medico,
            estado__in=['PENDIENTE', 'CONFIRMADA']
        ).exists()

        if cita_ocupada:
            raise serializers.ValidationError("Slot ya ocupado.")

        return data