"""
WTF de vaccination

Aca nos encargamos de la integridad de los datos

* Clase hereda de FlaskForm (Buena documentacion)
* Creamos los campos del HTML
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, Regexp, ValidationError


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
