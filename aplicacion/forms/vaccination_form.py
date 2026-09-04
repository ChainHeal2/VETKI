from flask_wtf import FlaskForm
from wtforms import DateField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class VaccinationForm(FlaskForm):
    vaccine_name = StringField(
        "Vacuna", validators=[DataRequired(), Length(min=2, max=120)]
    )
    application_date = DateField(
        "Fecha de aplicación", validators=[DataRequired()], format="%Y-%m-%d"
    )
    next_due_date = DateField(
        "Próxima dosis", validators=[Optional()], format="%Y-%m-%d"
    )
    lot_number = StringField("Lote", validators=[Optional(), Length(max=80)])
    veterinarian_notes = TextAreaField(
        "Notas del veterinario", validators=[Optional(), Length(max=4000)]
    )
    submit = SubmitField("Guardar vacuna")
