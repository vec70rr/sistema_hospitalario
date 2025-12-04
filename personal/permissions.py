from rest_framework import permissions

# Roles que tienen permitido modificar/consultar historial (RB-010, RNF-001)
DOCTOR_ROLES = ['MEDICO'] 
CLINICAL_STAFF_ROLES = ['MEDICO', 'ENFERMERO']
ADMIN_ROLES = ['ADMIN_SUPER', 'ADMIN_RECEPCION', 'ADMIN_ESTUDIOS', 'ADMIN_FARMACIA']

class IsDoctorOrAdmin(permissions.BasePermission):
    """
    Permite el acceso si el usuario es Médico o Administrador.
    """
    def has_permission(self, request, view):
        user = request.user
        # Verificar si el usuario está autenticado y tiene un rol clínico o administrativo
        if user and user.is_authenticated:
            return user.rol in DOCTOR_ROLES or user.rol in ADMIN_ROLES
        return False

class IsClinicalStaff(permissions.BasePermission):
    """
    Permite el acceso si el usuario es Médico o Enfermero.
    """
    def has_permission(self, request, view):
        user = request.user
        if user and user.is_authenticated:
            return user.rol in CLINICAL_STAFF_ROLES
        return False