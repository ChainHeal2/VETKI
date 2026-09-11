"""
WTF de vaccination

Aca nos encargamos de la integridad de los datos

* Clase hereda de FlaskForm (Buena documentacion)
* Creamos los campos del HTML
"""
from flask_wtf import FlaskForm
from wtforms import DateField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, Regexp, ValidationError
from aplicacion.functions.functions_wtf import solo_pasado


class VaccinationForm(FlaskForm):
    """
    Formulario de vacunación
    """
    # 1. Cambiado '*' por '+' para exigir coincidencia estricta de inicio a fin
    solo_letras = Regexp(
        r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\'\-]+$',
        message="El nombre de la vacuna solo debe contener letras."
    )
    solo_alfanumerico = Regexp(
        r'^[a-zA-Z0-9\-]*$',
        message="El lote solo debe contener letras, números y guiones sin espacios."
    )

    vaccine_name = StringField(
        "Nombre de la vacuna",
        validators=[
            DataRequired(message="El nombre de la vacuna es obligatorio."), 
            Length(min=2, max=120), 
            solo_letras
        ],
        filters=[lambda x: x.strip() if x else x],
    )
    application_date = DateField(
        "Fecha de aplicación",
        validators=[DataRequired(message="La fecha de aplicación es obligatoria."), solo_pasado],
        format="%Y-%m-%d",  # esto nos dice en que formato nos traera el HTML.
    )
    next_due_date = DateField(
        "Próxima dosis", 
        validators=[Optional()], 
        format="%Y-%m-%d"
    )
    lot_number = StringField(
        "Lote",
        validators=[Optional(), Length(min=0, max=80), solo_alfanumerico],
        filters=[lambda x: x.strip() if x else x],
    )
    veterinarian_notes = TextAreaField(
        "Notas del veterinario",
        validators=[Optional(), Length(min=0, max=4000)],
        filters=[lambda x: x.strip() if x else x],
    )

    submit = SubmitField("Guardar vacuna")

    def validate_vaccine_name(self, field):
        """
        Validación explícita de seguridad:
        Rechaza el campo si contiene cualquier dígito numérico (0-9).
        """
        if field.data and any(char.isdigit() for char in field.data):
            raise ValidationError("El nombre de la vacuna no puede contener números.")

    def validate_next_due_date(self, field):
        """
        Validación personalizada:
        Garantiza que la próxima dosis no sea anterior a la fecha de aplicación.
        """
        if field.data and self.application_date.data:
            if field.data < self.application_date.data:
                raise ValidationError(
                    "La fecha de la próxima dosis no puede ser anterior a la fecha de aplicación."
                )