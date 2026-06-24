"""
WTF de expediente clínico

Aca nos encargamos de la integridad de los datos

* Clase hereda de FlaskForm (Buena documentacion)
* Creamos los campos del HTML  

"""
# pyrefly: ignore [missing-import]
from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp,Optional
from aplicacion.functions.functions_wtf import limpiar_string

class MedicalRecordForm(FlaskForm):
    """
    Formulario de expediente clínico (Registro)
    """
    solo_letras = Regexp(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\'\-]*$',
                         message="El nombre solo debe contener letras.")
    solo_numeros_enteros = Regexp(r'^[0-9]*$', message="El microchip solo debe contener números.")
    reason = SelectField('Especies',choices=[('preventiva','Preventiva')
                                                            ,('control','Control'),
                                                            ('urgencia','Urgencia')])
    
    weigth = StringField('Peso del animal',validators=[Optional(), Length(min=0,max=100),solo_numeros_enteros],
                            filters=[limpiar_string])
    
    date = StringField('Fecha de la consulta',default=datetime.today)
    diagnosis = StringField('Diagnostico de la mascota',
                            validators=[Optional(), Length(min=0,max=255)],
                            filters=[limpiar_string])
    tratment = StringField('tratamiento de la mascota',
                            validators=[Optional(), Length(min=0,max=255)],
                            filters=[limpiar_string])
    
    submit = SubmitField('Registrar Expediente Clinico')
