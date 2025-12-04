from django.db import models
from personal.models import Personal
from expediente.models import Paciente

class Agenda(models.Model):
    # Relación con el Médico (Personal)
    medico = models.ForeignKey(Personal, on_delete=models.CASCADE, limit_choices_to={'rol': 'MEDICO'})
    
    # Días y Horarios de Trabajo (RF-009, RF-010)
    DIA_SEMANA = [
        (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), (3, 'Jueves'), 
        (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo')
    ]
    dia = models.IntegerField(choices=DIA_SEMANA)
    hora_inicio = models.TimeField(verbose_name="Hora de Inicio (ej: 09:00)")
    hora_fin = models.TimeField(verbose_name="Hora de Fin (ej: 14:00)")
    
    # Campo para el consultorio (RF-004) - Se asume que el médico tiene un consultorio asignado
    consultorio = models.CharField(max_length=50, verbose_name="Consultorio Asignado")

    def __str__(self):
        return f"Agenda de {self.medico.numero_empleado} - {self.get_dia_display()} ({self.hora_inicio}-{self.hora_fin})"

    class Meta:
        # Asegurar que un médico no tenga dos agendas solapadas en el mismo día
        unique_together = ('medico', 'dia', 'hora_inicio', 'hora_fin')

class Cita(models.Model):
    # Relaciones
    agenda = models.ForeignKey(Agenda, on_delete=models.PROTECT, related_name='citas')
    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT)
    
    # Campo de tiempo (debe ser un slot de 30 minutos - RF-011)
    fecha_hora = models.DateTimeField()
    
    ESTADO_CITA = [
        ('PENDIENTE', 'Pendiente de Pago'), # RB-007
        ('CONFIRMADA', 'Confirmada/Pagada'),
        ('CANCELADA', 'Cancelada por Paciente'), # RF-015
        ('COMPLETADA', 'Consulta Completada')
    ]
    estado = models.CharField(max_length=10, choices=ESTADO_CITA, default='PENDIENTE')
    
    # Tipo de cita para aplicar reglas específicas (RB-001 vs RB-002)
    TIPO_CITA = [
        ('MG', 'Medicina General'),
        ('ESP', 'Especialidad')
    ]
    tipo_cita = models.CharField(max_length=3, choices=TIPO_CITA)

    def __str__(self):
        return f"Cita de {self.paciente.apellidos} con {self.agenda.medico.numero_empleado} en {self.fecha_hora}"