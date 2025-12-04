# personal/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Personal, Especialidad, Especialista
from django.db import transaction

class LoginSerializer(serializers.Serializer):
    # El usuario se autentica con el numero_empleado
    numero_empleado = serializers.CharField(write_only=True) 
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        empleado = None
        password = data.get('password')
        num_empleado = data.get('numero_empleado')
        
        try:
            empleado = Personal.objects.get(numero_empleado=num_empleado)
        except Personal.DoesNotExist:
            # No encontramos el empleado, lanzamos error estándar para no dar pistas
            raise serializers.ValidationError("Credenciales inválidas (E-ME-01)[cite: 249].")

        if not empleado.is_active:
            print("FALLO: Usuario inactivo.")
            raise serializers.ValidationError("Cuenta inactiva.")

        # --- Lógica de Seguridad de Bloqueo (RNF-004) ---
        if empleado.esta_bloqueado:
            raise serializers.ValidationError("Cuenta bloqueada por intentos fallidos (E-SA-02)[cite: 453].")

        user = authenticate(request=self.context.get('request'), **{empleado.USERNAME_FIELD: num_empleado, 'password': password})
        # Nota: Usamos {empleado.USERNAME_FIELD: num_empleado} para asegurar que 
        # la palabra clave coincida con el campo de login definido ('numero_empleado').

        if user:
            # Autenticación exitosa
            if empleado.intentos_fallidos > 0:
                empleado.intentos_fallidos = 0 # Reiniciar contador
                empleado.save()
            data['user'] = user
            return data
        
        # --- Lógica de Intento Fallido (TA-1 de CU-A01) ---
        else:
            # Fallo de autenticación
            with transaction.atomic():
                empleado.intentos_fallidos += 1
                
                # Bloquear al 3er intento fallido (RNF-004)
                if empleado.intentos_fallidos >= 3:
                    empleado.esta_bloqueado = True
                    # El sistema solicita cambio de contraseña al bloquear (RNF-004)
                    # En la vida real, se notificaría para forzar el cambio
                    
                empleado.save()

            raise serializers.ValidationError("Credenciales inválidas (E-ME-01)[cite: 249].")

class EspecialidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especialidad
        fields = ['id', 'nombre']