from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.utils.translation import gettext_lazy as _

ROLES = (
    ('MEDICO', 'Médico (MG/Especialidad)'),
    ('ENFERMERO', 'Enfermero (Urgencias)'),
    ('ADMIN_SUPER', 'Super Administrador'),
    ('ADMIN_RECEPCION', 'Administrador de Recepción'),
    ('ADMIN_ESTUDIOS', 'Administrador de Estudios'),
    ('ADMIN_FARMACIA', 'Administrador de Farmacia'),
)

# ----------------- Custom Manager -----------------


class PersonalManager(DjangoUserManager):
    
    def create_user(self, numero_empleado, email=None, password=None, **extra_fields):
        if not numero_empleado:
            raise ValueError(_('El Número de Empleado es obligatorio.'))
        
        # Creamos la instancia del modelo.
        user = self.model(
            # ASIGNACIÓN CORREGIDA: Se guarda el valor en ambos campos
            numero_empleado=numero_empleado, # <-- NUESTRO CAMPO CUSTOM
            username=numero_empleado,        # <-- CAMPO HEREDADO DE AbstractUser
            email=self.normalize_email(email),
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, numero_empleado, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('rol', 'ADMIN_SUPER')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        # Se llama al método create_user que ahora guarda ambos campos.
        return self.create_user(numero_empleado, password=password, **extra_fields)


# ----------------- Modelo Personal -----------------

class Personal(AbstractUser):
    
    # Campo personalizado para el login (RF-007)
    numero_empleado = models.CharField(max_length=50, unique=True, verbose_name='Número de Empleado')
    
    # Sobrescribir el campo username por defecto de AbstractUser
    username = models.CharField(max_length=50, unique=False, default='') # Lo dejamos sin usar/sin unicidad
    
    # Hacemos los campos de AbstractUser explícitamente blank=True, null=True 
    # si se presentan problemas de validación en el Admin (aunque por defecto ya deberían serlo).
    # Sin embargo, la forma más limpia es hacer los campos inherentes opcionales:
    
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    email = models.EmailField(_('email address'), blank=True)

    # Requerimos que el login sea con numero_empleado
    USERNAME_FIELD = 'numero_empleado'
    
    # Quitamos el email de los campos requeridos, el password ya es requerido por create_user
    REQUIRED_FIELDS = [] 
    
    # Campo para el rol (RNF-001)
    rol = models.CharField(max_length=50, choices=ROLES, default='MEDICO')
    
    # ... (otros campos permanecen iguales) ...
    cedula_profesional = models.CharField(max_length=50, unique=True, null=True, blank=True)
    intentos_fallidos = models.IntegerField(default=0)
    esta_bloqueado = models.BooleanField(default=False)
    ultima_contrasena_hash = models.CharField(max_length=128, blank=True, null=True)
    
    # Asignar el Manager personalizado
    objects = PersonalManager() 

    def __str__(self):
        return f"{self.numero_empleado} - {self.rol}"

class Especialidad(models.Model):
    # Catálogo de 10 especialidades (RF-005)
    nombre = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.nombre

class Especialista(models.Model):
    # Relación con el Personal (Médico) (RF-006)
    medico = models.OneToOneField(Personal, on_delete=models.CASCADE, primary_key=True)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.PROTECT)
    
    # Se registran 2 especialistas por especialidad (Regla de Negocio implícita en RF-006)
    
    def __str__(self):
        return f"{self.medico.get_full_name()} - {self.especialidad.nombre}"