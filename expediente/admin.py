from django.contrib import admin
from .models import Paciente, NotaConsulta, RecetaDigital, DetalleMedicamento, OrdenReferencia

# Clase de administración para Paciente
class PacienteAdmin(admin.ModelAdmin):
    # Campos que se muestran en la vista de lista (lectura)
    list_display = ('id', 'CURP', 'nombre_completo', 'tipo', 'fecha_nacimiento')
    
    # Campos que permiten la búsqueda (crucial para el Super Admin)
    search_fields = ('CURP', 'nombre', 'apellidos', 'id')
    
    # Filtros laterales para clasificar pacientes
    list_filter = ('tipo',)
    
    # Definir los campos que aparecen en el formulario de creación/edición
    fieldsets = (
        ('Información de Acceso y Contacto (RF-001)', {
            'fields': ('CURP', 'RFC', 'nombre', 'apellidos', 'email', 'direccion', 'telefono')
        }),
        ('Información Clínica y Tipo (RF-002)', {
            'fields': ('fecha_nacimiento', 'tipo')
        }),
    )

    # Función para combinar nombre y apellido en la lista
    def nombre_completo(self, obj):
        return f"{obj.nombre} {obj.apellidos}"
    nombre_completo.short_description = 'Nombre Completo'
    
    # Si quieres que el Admin muestre un botón para agregar dependientes, 
    # puedes usar inlines (esto es solo un ejemplo avanzado, no necesario ahora)
    # inlines = [DependienteInline] 

# ----------------------------------------------------
# REGISTRAR MODELOS
# ----------------------------------------------------

admin.site.register(Paciente, PacienteAdmin)
admin.site.register(NotaConsulta)
admin.site.register(RecetaDigital)
admin.site.register(DetalleMedicamento)
admin.site.register(OrdenReferencia)

# Nota: Si el modelo Paciente ya tenía email y teléfono, 
# se muestran en el formulario; si no, deberías agregarlos al modelo Paciente.