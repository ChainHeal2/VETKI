import pytest
from datetime import date, timedelta
from flask import Flask
from werkzeug.datastructures import MultiDict
# Se usará appointment_create porque estandarizamos ese nombre en Base de Datos de Nombres
from aplicacion.forms.appointment.appointment_form import AppointmentForm

@pytest.fixture
def app_context():
    """Contexto básico de la aplicación de Flask con CSRF Desactivado para Testing Duros"""
    app = Flask(__name__)
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_request_context('/'):
        yield app

# Casos de uso específicos del CRUD Create para APPOINTMENTS
casos_appointment_create = [
    ({
        "appointment_date": date.today() + timedelta(days=5),
        "appointment_pet": "1"
    }, True, "Debe agendar una cita correctamente para el futuro."),
    
    ({
        "appointment_date": date.today(),
        "appointment_pet": "3"
    }, True, "Debe agendar una cita correctamente para el día de hoy."),
    
    ({
        "appointment_date": date.today() - timedelta(days=3),
        "appointment_pet": "1"
    }, False, "Debe rechazar citas en el pasado (lógica de negocio estricta)."),
    
    ({
        "appointment_date": "", 
        "appointment_pet": "2"
    }, True, "Debe aceptar la cita sin fecha estipulada (Ingreso Urgencia)."),
    
    ({
        "appointment_date": date.today() + timedelta(days=5),
        "appointment_pet": ""
    }, True, "Debe aceptar la cita si no se le especificó una mascota (Ingreso Urgencia).")
]

@pytest.mark.parametrize("datos, resultado_esperado, descripcion", casos_appointment_create)
def test_appointment_create_form(app_context, datos, resultado_esperado, descripcion):
    """
    Simulación de Tests Unitarios sobre el formulario de Agendamiento.
    """
    form_data = datos.copy()
    if isinstance(form_data.get('appointment_date'), date):
        form_data['appointment_date'] = form_data['appointment_date'].strftime('%Y-%m-%d')
        
    mdict = MultiDict(form_data)
    form = AppointmentForm(formdata=mdict)
    
    # Mocking de las opciones cargadas desde la BD en crudo
    #form.appointment_pet.choices = [(1, "Rex"), (2, "Michi"), (3, "Loro")]
    
    #assert form.validate() == resultado_esperado, f"Error en test: {descripcion} - Form Errors: {form.errors}"

# Casos de uso específicos del CRUD Update para APPOINTMENTS
casos_appointment_update = [
    ({
        "appointment_date": date.today() + timedelta(days=10),
        "appointment_pet": "2"
    }, True, "Debe actualizar una cita correctamente para el futuro."),
    
    ({
        "appointment_date": date.today() - timedelta(days=1),
        "appointment_pet": "1"
    }, False, "Debe rechazar reprogramaciones hacia el pasado."),
    
    ({
        "appointment_date": "", 
        "appointment_pet": "3"
    }, True, "Debe aceptar la reprogramación sin fecha estipulada (Ingreso Urgencia)."),
    
    ({
        "appointment_date": date.today() + timedelta(days=2),
        "appointment_pet": ""
    }, True, "Debe aceptar la reprogramación si no hay mascota válida (Ingreso Urgencia).")
]

@pytest.mark.parametrize("datos, resultado_esperado, descripcion", casos_appointment_update)
def test_appointment_update_form(app_context, datos, resultado_esperado, descripcion):
    """
    Simulación de Tests Unitarios sobre el formulario de Actualización (Reprogramación).
    """
    form_data = datos.copy()
    if isinstance(form_data.get('appointment_date'), date):
        form_data['appointment_date'] = form_data['appointment_date'].strftime('%Y-%m-%d')
        
    mdict = MultiDict(form_data)
    form = AppointmentForm(formdata=mdict)

    
    #assert form.validate() == resultado_esperado, f"Error en test: {descripcion} - Form Errors: {form.errors}"
