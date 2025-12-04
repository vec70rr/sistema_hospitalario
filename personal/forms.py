from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Personal
from django import forms

class PersonalCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Personal
        # Incluimos todos los campos que el AbstractUser hereda y los que son custom (rol, numero_empleado)
        fields = ('numero_empleado', 'rol', 'first_name', 'last_name', 'email', 'username')

    def clean(self):
        cleaned_data = super().clean()
        
        # Este es el punto de error. Si la validación falla, imprimimos los datos.
        if self.errors:
            print("\n--- ERROR DE VALIDACIÓN CRÍTICO EN FORMULARIO ---")
            print("Datos recibidos:", cleaned_data)
            print("Errores detectados:", self.errors)
            print("----------------------------------------------------\n")
        
        return cleaned_data

class PersonalChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = Personal
        fields = ('numero_empleado', 'rol', 'first_name', 'last_name', 'email', 'is_active', 'is_staff')