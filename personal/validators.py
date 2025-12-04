# personal/validators.py
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class MinLengthValidator:
    def validate(self, password, user=None):
        if len(password) < 8: # >=8 caracteres
            raise ValidationError(
                _("La contraseña debe tener al menos 8 caracteres."),
                code='password_too_short',
            )
        
    def get_help_text(self):
        return _("Debe tener al menos 8 caracteres.")

class ComplexityValidator:
    def validate(self, password, user=None):
        # Mayor, minúscula, digito
        if not re.search(r'[A-Z]', password):
            raise ValidationError(_("La contraseña debe contener al menos una mayúscula."), code='no_uppercase')
        if not re.search(r'[a-z]', password):
            raise ValidationError(_("La contraseña debe contener al menos una minúscula."), code='no_lowercase')
        if not re.search(r'[0-9]', password): # >=1 número
            raise ValidationError(_("La contraseña debe contener al menos un número."), code='no_digit')
        
    def get_help_text(self):
        return _("Debe incluir mayúsculas, minúsculas y al menos un número.")

class NoSequenceValidator:
    # Prohíbe secuencias (ej. "ABC", "123") (RB-014)
    def validate(self, password, user=None):
        if re.search(r'(abc|123|qwe|zxc)', password.lower()):
            raise ValidationError(_("La contraseña no debe contener secuencias comunes."), code='contains_sequence')
        
    def get_help_text(self):
        return _("No debe usar secuencias de caracteres o números (ej. '123' o 'abc').")

class NoReuseValidator:
    # No permitir repetir la misma contraseña (RNF-006)
    def validate(self, password, user=None):
        if user and user.ultima_contrasena_hash and user.check_password(password):
            raise ValidationError(_("No puedes reutilizar tu última contraseña."), code='reuse_forbidden')

    def get_help_text(self):
        return _("La contraseña no debe ser igual a la última utilizada.")