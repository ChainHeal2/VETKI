"""
WTF de user

Aca nos encargamos de la integridad de los datos

* Clase hereda de FlaskForm (Buena documentacion)
* Creamos los campos del HTML  

"""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, Email
from wtforms.validators import DataRequired, Length, Regexp, Email, Optional
from aplicacion.functions.functions_wtf import limpiar_string

class UserForm(FlaskForm):
    """
    Formulario de user (Registro)
    """
    user_rut = StringField('RUT',
                           validators=[Optional(), Length(min=8, max=20)],
                           filters=[limpiar_string])
                           
    user_email = StringField('Correo Electrónico',
                             validators=[DataRequired(message="El email es obligatorio para Iniciar Sesión."), Email(message="Ingrese correo válido."), Length(min=5,max=100)],
                             filters=[limpiar_string])
    
    user_names = StringField('Nombres',
                            validators=[DataRequired(message="El nombre es obligatorio."), Length(min=3,max=100)],
                            filters=[limpiar_string])
    
    user_password = PasswordField('Contraseña',
                                 validators=[DataRequired(message="Debe ingresar una contraseña."), Length(min=6,max=50)])
    
    submit = SubmitField('Registrar Usuario')
