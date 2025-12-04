# personal/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token # Usaremos Tokens para el login
from .serializers import LoginSerializer, EspecialidadSerializer
from .models import Especialidad

class LoginAPIView(generics.GenericAPIView):
    """
    API para Iniciar Sesión de Personal (Médicos, Enfermeros, Admins)
    Aplica la lógica de bloqueo al 3er intento fallido (RNF-004).
    """
    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Generar o obtener el token de autenticación
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            "token": token.key,
            "numero_empleado": user.numero_empleado,
            "rol": user.rol,
            "message": "Inicio de sesión exitoso[cite: 154]."
        }, status=status.HTTP_200_OK)

class EspecialidadListAPIView(generics.ListAPIView):
    """
    API para devolver el catálogo de especialidades (RF-005).
    """
    queryset = Especialidad.objects.all()
    serializer_class = EspecialidadSerializer
    # Solo personal autenticado puede ver el catálogo
    permission_classes = [permissions.IsAuthenticated]