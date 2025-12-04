from django.db import models
# Importamos el modelo de Personal para la relación Médico -> Nota
from personal.models import Personal 

class Paciente(models.Model):
    # Campos de Registro (RF-001, RF-002)
    CURP = models.CharField(max_length=18, unique=True, verbose_name='CURP')
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255, verbose_name='Dirección') # RF-001
    fecha_nacimiento = models.DateField(verbose_name='Fecha de Nacimiento') # RF-001
    
    # Campo de antecedentes se omite por simplicidad inicial, pero se debe agregar
    
    # Tipo de paciente (RF-002)
    TIPOS_PACIENTE = [
        ('A', 'Asegurado'),
        ('N', 'No Asegurado'),
    ]
    tipo = models.CharField(max_length=1, choices=TIPOS_PACIENTE, default='N', verbose_name='Tipo de Paciente')
    
    # RFC es requerido en RF-001, pero lo haremos opcional ya que no todos lo tienen.
    RFC = models.CharField(max_length=13, unique=True, null=True, blank=True)
    
    def __str__(self):
        return f"Expediente No. {self.pk}: {self.nombre} {self.apellidos}"

class NotaConsulta(models.Model):
    # Relaciones
    # CASCADE: Si se elimina el paciente, se elimina la nota (Historial)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='notas') 
    # PROTECT: No permite eliminar al personal si tiene notas asociadas (trazabilidad)
    medico = models.ForeignKey(Personal, on_delete=models.PROTECT, limit_choices_to={'rol__in': ['MEDICO', 'ENFERMERO']}) 
    
    # Contenido de la nota (NOM-004 y RB-009) - Campos obligatorios
    # Los hacemos TextField para permitir contenido extenso
    diagnostico = models.TextField(verbose_name='Diagnóstico (NOM-004)') # RB-009
    tratamiento = models.TextField(verbose_name='Tratamiento (NOM-004)') # RB-009
    evolucion = models.TextField(verbose_name='Evolución y Notas (NOM-004)') # RB-009
    procedimientos = models.TextField(verbose_name='Procedimientos', blank=True, null=True) # RF-019
    observaciones = models.TextField(verbose_name='Observaciones', blank=True, null=True) # RF-019
    
    # Trazabilidad
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Nota de {self.paciente.CURP} por Dr(a). {self.medico.get_full_name()} - {self.fecha_registro.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        ordering = ['-fecha_registro'] # Las notas más recientes aparecerán primero (RF-020)
        verbose_name_plural = "Notas de Consulta"

class RecetaDigital(models.Model):
    # Relaciones y Trazabilidad
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(Personal, on_delete=models.PROTECT, limit_choices_to={'rol__in': ['MEDICO']}) # Solo Médicos pueden recetar
    fecha_emision = models.DateTimeField(auto_now_add=True)
    
    # Contenido Obligatorio de la NOM-024 (RB-012, RF-026)
    diagnostico = models.CharField(max_length=255, verbose_name='Diagnóstico') # Requerido
    
    # Datos del médico (cédula, especialidad, teléfonos) se toman del modelo Personal
    talla = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Talla (m)') # RB-012
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Peso (kg)') # RB-012
    
    # Campo para la firma digital o indicación de firma electrónica obligatoria (RB-012)
    requiere_firma = models.BooleanField(default=True) 

    # Se usará un campo separado para los medicamentos y dosificación (relación uno a muchos)
    
    def __str__(self):
        return f"Receta de {self.paciente.apellidos} - {self.fecha_emision.strftime('%Y-%m-%d')}"

class DetalleMedicamento(models.Model):
    # Detalle de cada medicamento en la receta
    receta = models.ForeignKey(RecetaDigital, on_delete=models.CASCADE, related_name='detalles')
    medicamento = models.CharField(max_length=255, verbose_name='Medicamento')
    presentacion = models.CharField(max_length=100, verbose_name='Presentación')
    dosificacion = models.TextField(verbose_name='Dosificación e Indicaciones') # Requerido (RB-012)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.medicamento} ({self.dosificacion})"
    
class OrdenReferencia(models.Model):
    # Relaciones
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico_general = models.ForeignKey(
        Personal, 
        on_delete=models.PROTECT, 
        limit_choices_to={'rol': 'MEDICO'}, # Solo Médicos pueden referir
        verbose_name='Médico General Emisor'
    )
    # Requerimiento: Debe especificar la especialidad (RF-017)
    especialidad_solicitada = models.CharField(max_length=100) 
    motivo_referencia = models.TextField()
    fecha_emision = models.DateTimeField(auto_now_add=True)
    
    # Estado: Necesario para el flujo (RB-006)
    ESTADOS = [('PENDIENTE', 'Pendiente de Agendar'), ('AGENDADA', 'Cita Agendada')]
    estado = models.CharField(max_length=10, choices=ESTADOS, default='PENDIENTE')

    def __str__(self):
        return f"Orden para {self.especialidad_solicitada} de {self.paciente.apellidos}"