"""
WTF de pet

Aca nos encargamos de la integridad de los datos

* Clase hereda de FlaskForm (Buena documentacion)
* Creamos los campos del HTML  

"""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired,Length,Optional,Regexp
from aplicacion.functions.functions_wtf import solo_pasado,limpiar_string

class PetForm(FlaskForm):
    """
    Formulario de pet
    """
    solo_letras = Regexp(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\'\-]*$',message="El nombre solo debe contener letras.")
    solo_numeros_enteros = Regexp(r'^[0-9]*$', message="El microchip solo debe contener números.")

    pet_species_name = SelectField('Especies',choices=[('canina','Canina'),('felina','Felina')])
    pet_names = StringField('Nombre de la mascota',
                            validators=[DataRequired(),Length(min=3,max=30),solo_letras],
                            filters=[lambda x: x.strip() if x else x])
    pet_race = StringField('Raza',validators=[Optional(),Length(min=3,max=30)],filters=[limpiar_string])
    pet_datebirth = DateField('Fecha de Nacimiento',validators=[Optional(),solo_pasado],
                               format='%Y-%m-%d')#esto nos dice en que formato nos traera el HTML.
    pet_microchip = StringField('Microchip',validators=[Optional(),Length(min=0,max=30),
                                                        solo_numeros_enteros],filters=[limpiar_string])
    pet_gender = StringField('Genero',validators=[Optional(),Length(min=0,max=30) ])
    pet_color = StringField('Color', validators=[Optional(),Length(min=3,max=30)],filters=[limpiar_string])
    pet_rstatus = StringField('Estado reproductivo',validators=[Optional(),Length(min=0,max=30)],filters=[limpiar_string])

    pet_tutor_name = StringField('Nombre del tutor',validators=[DataRequired(),Length(min=3,max=30),solo_letras],filters=[limpiar_string])
    pet_tutor_address = StringField('Direccion del tutor',validators=[Optional(),Length(min=3,max=30)],filters=[limpiar_string])
    pet_tutor_phone = StringField('Telefono del tutor',validators=[Optional(),Length(min=0,max=10)],filters=[limpiar_string])
    
    submit = SubmitField('Guardar Datos')
