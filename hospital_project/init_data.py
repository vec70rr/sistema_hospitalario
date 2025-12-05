# hospital_project/init_data.py

import os
from django.contrib.auth import get_user_model
from personal.models import Especialidad

User = get_user_model()

def create_initial_data():
    # --- 1. CREAR SUPER ADMINISTRADOR (Si no existe) ---
    if not User.objects.filter(numero_empleado='SA001').exists():
        User.objects.create_superuser(
            numero_empleado='SA001',
            password='Admin2001', # Usa una contraseña que recuerdes para el entorno Docker
            first_name='Super',
            last_name='Admin',
            email='admin@hospital.com',
            rol='ADMIN_SUPER'
        )
        print("✅ Super Administrador 'SA001' creado.")
    else:
        print("Super Administrador 'SA001' ya existe.")

    # --- 2. CARGAR ESPECIALIDADES (RF-005) ---
    especialidades = [
        "Maxilofacial", "Cardiología", "Hematología", "Pediatría", "ORL", 
        "Plástica", "Nefrología", "Neumología", "Neurología", "Gastroenterología"
    ]
    
    for nombre in especialidades:
        if not Especialidad.objects.filter(nombre=nombre).exists():
            Especialidad.objects.create(nombre=nombre)
            print(f"✅ Especialidad '{nombre}' cargada.")
    else:
        print("Especialidades cargadas.")


if __name__ == "__main__":
    create_initial_data()