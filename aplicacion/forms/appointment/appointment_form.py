"""
WTF de appointment
"""
from flask_wtf import FlaskForm
from wtforms import DateTimeLocalField, SelectField, StringField,SubmitField
from wtforms.validators import Optional, Regexp, data_required
from aplicacion.functions.functions_wtf import solo_futuro
class AppointmentForm(FlaskForm):
    """
    Formulario de appointment
    """
    #PARA VALIDAR SOLO STRINGS
    solo_letras = Regexp(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\'\-]*$',message="El dato solo debe contener letras.")
    #CAMPOS
    date = DateTimeLocalField('Fecha de cita',validators=[solo_futuro,data_required()], format=[
            '%Y-%m-%dT%H:%M',       # Estándar HTML5 móvil sin segundos (ej: 2026-09-02T18:30)
            '%Y-%m-%dT%H:%M:%S',    # Algunos navegadores móviles incluyen segundos (ej: 2026-09-02T18:30:00)
            '%Y-%m-%d %H:%M',       # Formato PC con espacio
            '%Y-%m-%d %H:%M:%S'     # Formato PC con espacio y segundos
        ])
    g_id = StringField('ID de Google Calendar', validators=[Optional()])
    submit = SubmitField('Guardar Datos')
