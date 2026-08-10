"""
WTF de appointment
"""
from flask_wtf import FlaskForm
from wtforms import DateTimeLocalField, SelectField,SubmitField
from wtforms.validators import Optional, Regexp
from aplicacion.functions.functions_wtf import solo_futuro
class AppointmentForm(FlaskForm):
    """
    Formulario de appointment
    """
    #PARA VALIDAR SOLO STRINGS
    solo_letras = Regexp(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\'\-]*$',message="El dato solo debe contener letras.")
    #CAMPOS
    date = DateTimeLocalField('Fecha de cita',validators=[solo_futuro], format='%Y-%m-%dT%H:%M')
    submit = SubmitField('Guardar Datos')
