from dataclasses import field
from datetime import datetime,date
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
        texto = valor
        return texto if texto != "" else None
    return None
def solo_futuro(form, field):
    """No permite fechas ni horas pasadas"""
    if field.data:
        # Si el valor viene como datetime (ej: DateTimeLocalField)
        if isinstance(field.data, datetime):
            if field.data < datetime.now():
                raise ValidationError("La fecha no puede ser pasada.")
        
        # Si viene como date (ej: DateField)
        elif isinstance(field.data, date):
            if field.data < date.today():
                raise ValidationError("La fecha no puede ser pasada.")