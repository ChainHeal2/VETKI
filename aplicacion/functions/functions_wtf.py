from datetime import date
from wtforms.validators import ValidationError

def solo_pasado(form, field):
    """No permite fechas futuras"""
    if field.data and field.data > date.today():
        raise ValidationError("La fecha no puede ser futura.")
def limpiar_string(valor):
    """
    Toma lo que viene del formulario, quita espacios
    y si queda vacío, devuelve None (NULL para la DB).
    """
    if valor:
        texto = valor.strip()
        return texto if texto != "" else None
    return None
def solo_futuro(form, field):
    """No permite fechas pasadas"""
    if field.data and field.data < date.today():
        raise ValidationError("La fecha no puede ser pasada.")