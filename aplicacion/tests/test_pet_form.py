import pytest
from datetime import date, timedelta
from flask import Flask
from werkzeug.datastructures import MultiDict
from aplicacion.forms.pet.pet_form import PetForm

@pytest.fixture
def app_context():
    app = Flask(__name__)
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_request_context('/'):
        yield app
casos_create = [
    ({
        "pet_names": "Ichir",
        "pet_species_name": "1",
        "pet_race": "Bulldog",
        "pet_datebirth": date.today(),
        "pet_microchip": "123456789",
        "pet_gender": "Macho",
        "pet_color": "Blanco",
        "pet_rstatus": "Castrado",
        "pet_tutor_name": "Juan Perez",  # Corregido de pet_tutor_names a pet_tutor_name
        "pet_tutor_email": "juan.perez@example.com",
        "pet_tutor_phone": "1234567890",
    }, True, "Debe crear la mascota correctamente"),
    ({
        "pet_names": "Ma ",
        "pet_species_name": "1", 
        "pet_race": "Pug",
        "pet_datebirth": date.today(),
        "pet_microchip": "123456789",
        "pet_gender": "Hembra",
        "pet_color": "Blanco",
        "pet_rstatus": "Activo",
        "pet_tutor_name": "Juan Perez"
    }, False, "Debe fallar por nombre muy corto"),
    ({
        "pet_names": "KYoMi",
        "pet_species_name": "2",
        "pet_race": "Bulldog",
        "pet_datebirth": date.today() - timedelta(days=365),
        "pet_microchip": "123456789",
        "pet_gender": "Macho",
        "pet_color": "Blanco",
        "pet_rstatus": "Castrado",
        "pet_tutor_name": "Juan Perez"
    }, True, "Puede ser: a year ago"),
    ({
        "pet_names": "SulTan",
        "pet_species_name": "1",
        "pet_race": "Bulldog",
        "pet_datebirth": date.today(),
        "pet_microchip": "123456789",
        "pet_gender": "",
        "pet_color": "Blanco",
        "pet_rstatus": "Castrado",
        "pet_tutor_name": "Juan Perez"
    }, True, "Puede sin genero: vacio"),
    ({
        "pet_names": "Canela",
        "pet_species_name": "1",
        "pet_race": "Bulldog",
        "pet_datebirth": date.today(),
        "pet_microchip": "123456789",
        "pet_gender": "Macho",
        "pet_color": "Bl",
        "pet_rstatus": "Castrado",
        "pet_tutor_name": "Juan Perez"
    }, False, "Color no existe"),
    ({
        "pet_names": "Sirius",
        "pet_species_name": "1",
        "pet_race": "",
        "pet_datebirth": "",
        "pet_microchip": "",
        "pet_gender": "",
        "pet_color": "",
        "pet_rstatus": "",
        "pet_tutor_name": "Juan Perez"
    }, True, "Solo el nombre y tutor"),
    ({
        "pet_names": "Sirius",
        "pet_species_name": "1",
        "pet_race": "",
        "pet_datebirth": date.today() + timedelta(days=1),
        "pet_microchip": "",
        "pet_gender": "",
        "pet_color": "",
        "pet_rstatus": "",
        "pet_tutor_name": "Juan Perez"
    }, False, "No se permite fecha futura"),
    ({
        "pet_names": "GaAur'a",
        "pet_species_name": "1",
        "pet_race": "",
        "pet_datebirth": date.today(),
        "pet_microchip": "",
        "pet_gender": "",
        "pet_color": "",
        "pet_rstatus": "",
        "pet_tutor_name": "Juan Perez"
    }, True, "Limpia los nombres raros"),
    ({
        "pet_names": "Soy Letra",
        "pet_species_name": "1",
        "pet_race": "",
        "pet_datebirth": date.today(),
        "pet_microchip": "F600",
        "pet_gender": "",
        "pet_color": "",
        "pet_rstatus": "",
        "pet_tutor_name": "Juan Perez"
    }, False, "No permite letras en numeros")
]

casos_update = [
    ({
        "pet_names": "Ic",
        "pet_species_name": "1",
        "pet_race": "",
        "pet_datebirth": date.today(),
        "pet_microchip": "",
        "pet_gender": "",
        "pet_color": "",
        "pet_rstatus": "",
        "pet_tutor_name": "Juan Perez"
    }, False, "En caso de:Nombre muy corto"),
    ({
        "pet_names": "Ma ",
        "pet_species_name": "1", 
        "pet_race": "Pug",
        "pet_datebirth": date.today(),
        "pet_microchip": "123456789",
        "pet_gender": "Hembra",
        "pet_color": "Blanco",
        "pet_rstatus": "Activo",
        "pet_tutor_name": "Juan Perez"
    }, False, "Debe fallar por nombre muy corto"),
    ({
        "pet_names": "Kyomi",
        "pet_species_name": "1",
        "pet_race": "Bulldog",
        "pet_datebirth": date.today() - timedelta(days=365),
        "pet_microchip": "",
        "pet_gender": "Macho",
        "pet_color": "Blanco",
        "pet_rstatus": "Castrado",
        "pet_tutor_name": "Juan Perez"
    }, True, "Puede ser: a year ago"),
    ({
        "pet_names": "Sultan",
        "pet_species_name": "1",
        "pet_race": "Bulldog",
        "pet_datebirth": date.today(),
        "pet_microchip": "",
        "pet_gender": "",
        "pet_color": "Blanco",
        "pet_rstatus": "Castrado",
        "pet_tutor_name": "Juan Perez"
    }, True, "Puede sin genero: vacio"),
    ({
        "pet_names": "Canela",
        "pet_species_name": "1",
        "pet_race": "Bulldog",
        "pet_datebirth": date.today(),
        "pet_microchip": "123456789",
        "pet_gender": "Macho",
        "pet_color": "Bl",
        "pet_rstatus": "Castrado",
        "pet_tutor_name": "Juan Perez"
    }, False, "Color no existe"),
    ({
        "pet_names": "Sirius",
        "pet_species_name": "1",
        "pet_race": "",
        "pet_datebirth": "",
        "pet_microchip": "",
        "pet_gender": "",
        "pet_color": "",
        "pet_rstatus": "",
        "pet_tutor_name": "Juan Perez"
    }, True, "Solo el nombre y tutor"),
    ({
        "pet_names": "Sirius",
        "pet_species_name": "1",
        "pet_race": "",
        "pet_datebirth": date.today() + timedelta(days=1),
        "pet_microchip": "",
        "pet_gender": "",
        "pet_color": "",
        "pet_rstatus": "",
        "pet_tutor_name": "Juan Perez"
    }, False, "No se permite fecha futura"),
    ({
        "pet_names": "GaAur'a",
        "pet_species_name": "1",
        "pet_race": "",
        "pet_datebirth": date.today(),
        "pet_microchip": "",
        "pet_gender": "",
        "pet_color": "",
        "pet_rstatus": "",
        "pet_tutor_name": "Juan Perez"
    }, True, "Limpia los nombres raros"),
    ({
        "pet_names": "Soy Letra",
        "pet_species_name": "1",
        "pet_race": "",
        "pet_datebirth": date.today(),
        "pet_microchip": "F600",
        "pet_gender": "",
        "pet_color": "",
        "pet_rstatus": "",
        "pet_tutor_name": "Juan Perez"
    }, False, "No permite letras en numeros"),
    ({
        "pet_names": "",
        "pet_species_name": "",
        "pet_race": "",
        "pet_datebirth": "",
        "pet_microchip": "",
        "pet_gender": "",
        "pet_color": "",
        "pet_rstatus": "",
        "pet_tutor_name": ""
    }, False, "Sin datos vacios"),
    ({
    "pet_names": "Ichir",
    "pet_species_name": "1",
    "pet_datebirth": date.today(),
    "pet_tutor_name": "Juan Perez",
    "pet_tutor_email": "juan@example.com",
    "pet_tutor_phone": "+56912345678"  # <-- TELÉFONO VÁLIDO CON PREFIJO
}, True, "Debe aceptar teléfonos con formato internacional correcto"),
]

# --- EJECUCIÓN DE LOS TESTS DE PYTEST --- #
@pytest.mark.parametrize("datos, resultado_esperado, descripcion", casos_create)
def test_pet_create_form(app_context, datos, resultado_esperado, descripcion):
    """
    Test de Formulario Create de Mascota usando los Casos de Uso.
    Convierte el diccionario crudo en un MultiDict para simular envío de datos HTML.
    """
    # HTML forms transmit dates as strings: YYYY-MM-DD
    form_data = datos.copy()
    if isinstance(form_data.get('pet_datebirth'), date):
        form_data['pet_datebirth'] = form_data['pet_datebirth'].strftime('%Y-%m-%d')
        
    mdict = MultiDict(form_data)
    form = PetForm(formdata=mdict)
    
    # Mocking choices to pass 'coerce=int' internal validations for SelectFields
    form.pet_species_name.choices = [(1, "Perro"), (2, "Gato"), (3, "Ave")]
    
    # Assert que el formulario responda lo que esperamos
    assert form.validate() == resultado_esperado, f"Fallo en: {descripcion}. Errores: {form.errors}"


@pytest.mark.parametrize("datos, resultado_esperado, descripcion", casos_update)
def test_pet_update_form(app_context, datos, resultado_esperado, descripcion):
    """
    Test de Formulario Update de Mascota usando los Casos de Uso.
    """
    form_data = datos.copy()
    if isinstance(form_data.get('pet_datebirth'), date):
        form_data['pet_datebirth'] = form_data['pet_datebirth'].strftime('%Y-%m-%d')
        
    mdict = MultiDict(form_data)
    form = PetForm(formdata=mdict)
    
    form.pet_species_name.choices = [(1, "Perro"), (2, "Gato"), (3, "Ave")]
    
    assert form.validate() == resultado_esperado, f"Fallo en Update: {descripcion}. Errores: {form.errors}"
