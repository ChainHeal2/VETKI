"""
WTF de appointment
"""
from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, SubmitField
from wtforms.validators import Optional, Regexp
from aplicacion.functions.functions_wtf import solo_futuro
class AppointmentForm(FlaskForm):
    """
    Formulario de appointment
    """
    #PARA VALIDAR SOLO STRINGS
    solo_letras = Regexp(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\'\-]*$',message="El dato solo debe contener letras.")
    #CAMPOS
    appointment_pet = SelectField('Especie',validators=[], coerce=int)
    appointment_date = DateField('Fecha de Nacimiento',validators=[solo_futuro], format='%Y-%m-%d')
    submit = SubmitField('Guardar Datos')
