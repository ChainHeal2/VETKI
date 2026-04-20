"""
WTF de pet
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired,Length,Optional,Regexp
from aplicacion.functions.functions_wtf import solo_pasado,limpiar_string
class PetUpdate(FlaskForm):
    """
    Formulario de pet
    """
    solo_letras = Regexp(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\'\-]*$',message="El nombre solo debe contener letras.")
    species_id = SelectField('Especie',validators=[Optional()], coerce=int)
    pet_names = StringField('Nombre de la mascota', validators=[DataRequired(),Length(min=3,max=30),solo_letras],
                            filters=[limpiar_string])
    pet_race = StringField('Raza',validators=[  Optional(),Length(min=3, max=30),solo_letras],
                                                filters=[limpiar_string])
    pet_datebirth = DateField('Fecha de Nacimiento',validators=[Optional(),solo_pasado], format='%Y-%m-%d')
    pet_microchip = StringField('Microchip',validators=[Optional(),
                                                        Length(min=15,max=15)],filters=[limpiar_string])
    pet_gender = StringField('Genero',validators=[ Optional(),Length(min=3, max=20),solo_letras],filters = [limpiar_string])
    pet_color = StringField('Color', validators=[Optional(),Length(min=3,max=30),solo_letras],filters=[limpiar_string])
    pet_rstatus = StringField('Estado reproductivo',validators=[Optional(),Length(min=0,max=30),solo_letras],filters=[limpiar_string])
    submit = SubmitField('Guardar Datos')
