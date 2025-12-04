from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Especialidad, Especialista, Personal 
from .forms import PersonalCreationForm, PersonalChangeForm

admin.site.register(Especialidad)
admin.site.register(Especialista)


class PersonalAdmin(UserAdmin):
    form = PersonalChangeForm
    add_form = PersonalCreationForm
    
    # 1. Definir los fieldsets para la EDICIÓN (Change User)
    fieldsets = (
        (None, {'fields': ('numero_empleado', 'password', 'rol', 'is_staff', 'is_active', 'intentos_fallidos', 'esta_bloqueado')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'cedula_profesional')}),
        ('Permissions', {'fields': ('is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # 2. Definir los fieldsets para la CREACIÓN (Add User)
    # Requerimiento: Debe incluir password y password2 para el hashing.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('numero_empleado', 'password1', 'password2', 'rol', 'is_staff', 'is_active', 'first_name', 'last_name', 'username'),
        }),
    )
    
    # 3. Campos de Listado
    list_display = ('numero_empleado', 'rol', 'is_staff', 'is_active')
    search_fields = ('numero_empleado', 'first_name', 'last_name')
    ordering = ('numero_empleado',)

# Desregistrar y registrar la clase PersonalAdmin
try:
    admin.site.unregister(Personal)
except admin.sites.NotRegistered:
    pass
    
admin.site.register(Personal, PersonalAdmin)