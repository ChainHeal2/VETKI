"""
WTF de expediente clínico

Aca nos encargamos de la integridad de los datos

* Clase hereda de FlaskForm (Buena documentacion)
* Creamos los campos del HTML  

"""
# pyrefly: ignore [missing-import]
from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField,IntegerField,FloatField,DateField,TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Regexp,Optional

class MedicalRecordForm(FlaskForm):
    """
    Formulario de expediente clínico (Registro)
    """
    solo_letras = Regexp(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\'\-]*$',
                         message="El nombre solo debe contener letras.")
    solo_numeros_enteros = Regexp(r'^[0-9]*$', message="El microchip solo debe contener números.")
    date = DateField('Fecha de la consulta',default=datetime.today)
    reason = SelectField('Especies',choices=[('preventiva','Preventiva')
                                                            ,('control','Control'),
                                                            ('urgencia','Urgencia')])
    weigth = FloatField('Peso del animal',validators=[Optional(),NumberRange(min=0.05,max=100.0)],filters=[])
    temperature = FloatField('Temperatura del animal',validators=[Optional()])
    heart = FloatField('Frecuencia cardiaca del animal',validators=[Optional(),NumberRange(min=0,max=100)],filters=[])
    respiratory = FloatField('Frecuencia respiratoria del animal',validators=[Optional(), NumberRange(min=0,max=100)],
                            filters=[])
    water = IntegerField('Cantidad de agua del animal',validators=[Optional(), NumberRange(min=0,max=100)],
                            filters=[])
    capillary = FloatField('Tiempo de llenado capilar del animal',validators=[Optional(), NumberRange(min=0,max=100)],
                            filters=[])
    arterial = FloatField('Presion arterial del animal',validators=[Optional(), NumberRange(min=0,max=100)],
                            filters=[])
    history = TextAreaField('Historia clinica de la mascota',
                            validators=[Optional(), Length(min=0,max=255)],
                            filters=[])
    diagnosis = TextAreaField('Diagnostico de la mascota',
                            validators=[Optional(), Length(min=0,max=255)],
                            filters=[])
    tratment = TextAreaField('tratamiento de la mascota',
                            validators=[Optional(), Length(min=0,max=255)],
                            filters=[])
    submit = SubmitField('Registrar Expediente Clinico')
