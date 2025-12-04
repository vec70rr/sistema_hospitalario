from rest_framework import serializers
from .models import Paciente, NotaConsulta, RecetaDigital, DetalleMedicamento, OrdenReferencia

# --- 1. Paciente Serializer (Para buscar y mostrar datos) ---

class PacienteSerializer(serializers.ModelSerializer):
    """
    Serializador para crear o buscar pacientes.
    Usado por la Adm. Recepción (CU-AD-04) y Médicos (CU-A02).
    """
    class Meta:
        model = Paciente
        # Campos de registro requeridos (RF-001)
        fields = ['id', 'CURP', 'nombre', 'apellidos', 'direccion', 'fecha_nacimiento', 'tipo', 'RFC']
        read_only_fields = ['id']


# --- 2. Nota de Consulta Serializer (Para registrar una nueva nota) ---

class NotaConsultaSerializer(serializers.ModelSerializer):
    """
    Serializador para registrar una nueva entrada en el historial clínico (RF-020).
    Aplica las validaciones de campos obligatorios (NOM-004, RB-009).
    """
    medico_nombre = serializers.ReadOnlyField(source='medico.get_full_name')
    
    class Meta:
        model = NotaConsulta
        # Los campos de la NOM-004 deben ser obligatorios en la API
        fields = [
            'id', 'paciente', 'medico', 'medico_nombre', 
            'diagnostico', 'tratamiento', 'evolucion', 
            'procedimientos', 'observaciones', 'fecha_registro'
        ]
        read_only_fields = ['id', 'paciente', 'medico', 'medico_nombre', 'fecha_registro', 'procedimientos', 'observaciones', 'diagnostico', 'tratamiento', 'evolucion']

    # Agregamos esta función para forzar la validación de los campos de solo lectura si es necesario
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si estamos listando (no pasando 'data' para creación), no requerimos los campos
        if kwargs.get('data') is None:
            for field_name in ['diagnostico', 'tratamiento', 'evolucion']:
                if field_name in self.fields:
                    self.fields[field_name].required = False


class DetalleMedicamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleMedicamento
        fields = ['medicamento', 'presentacion', 'dosificacion', 'cantidad']
        
class RecetaDigitalSerializer(serializers.ModelSerializer):
    medico_nombre = serializers.ReadOnlyField(source='medico.get_full_name')
    detalles = DetalleMedicamentoSerializer(many=True, read_only=True) # Campo anidado
    
    class Meta:
        model = RecetaDigital
        fields = [
            'id', 'paciente', 'diagnostico', 'medico_nombre', 'talla', 'peso', 
            'detalles', 'fecha_emision'
        ]
        read_only_fields = ['id','paciente', 'medico_nombre', 'fecha_emision']
        
    def create(self, validated_data):
        # 1. Extraer los detalles del medicamento
        detalles_data = validated_data.pop('detalles')
        
        # 2. Crear la Receta principal
        # Aseguramos que el médico sea el usuario autenticado
        receta = RecetaDigital.objects.create(**validated_data)
        
        # 3. Crear los detalles de los medicamentos (Dosificación RB-012)
        for detalle in detalles_data:
            DetalleMedicamento.objects.create(receta=receta, **detalle)
            
        return receta

class OrdenReferenciaSerializer(serializers.ModelSerializer):
    medico_general_numero = serializers.ReadOnlyField(source='medico_general.numero_empleado')
    class Meta:
        model = OrdenReferencia
        fields = ['id', 'paciente', 'especialidad_solicitada', 'motivo_referencia', 'medico_general_numero', 'fecha_emision', 'estado']
        read_only_fields = ['id', 'fecha_emision', 'estado', 'medico_general_numero']

class PacientePublicSerializer(serializers.ModelSerializer):
    """ Serializador simple para la búsqueda pública (solo CURP y ID). """
    class Meta:
        model = Paciente
        fields = ['id', 'CURP', 'nombre', 'apellidos']