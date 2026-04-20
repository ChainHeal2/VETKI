import pytest
from datetime import date, timedelta
from flask import Flask
from werkzeug.datastructures import MultiDict
from aplicacion.forms.pet.pet_create import PetForm
from aplicacion.forms.pet.pet_update import PetUpdate

@pytest.fixture
def app_context():
    app = Flask(__name__)
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_request_context('/'):
        yield app
casos_create = [
    ({
    "pet_names": " Ichir",
    "species_id" : "1",
    "pet_race": " Bulldog",
    "pet_datebirth": date.today(),
    "pet_microchip" : "123456789",
    "pet_gender": "Macho",
    "pet_color": "Blanco",
    "pet_rstatus": "Castrado"
    }, True, "Debe crear la mascota correctamente"),
    ({
    "pet_names": "Ma ",
    "species_id" : "1", 
    "pet_race": "Pug",
    "pet_datebirth": date.today(),
    "pet_microchip" : "123456789",
    "pet_gender": "Hembra",
    "pet_color": "Blanco",
    "pet_rstatus": "Activo"},
    False,
    "Debe fallar por nombre muy corto"),
    ({
    "pet_names": " KYoMi",
    "species_id" : "2",
    "pet_race": " Bulldog",
    "pet_datebirth":date.today() - timedelta(days=365),
    "pet_microchip" : "123456789",
    "pet_gender": "Macho",
    "pet_color": "Blanco",
    "pet_rstatus": "Castrado"},
    True,
    "Puede ser: a year ago"),
    ({
    "pet_names": "SulTan",
    "species_id" : "1",
    "pet_race": " Bulldog",
    "pet_datebirth": date.today(),
    "pet_microchip" : "123456789",
    "pet_gender": "",
    "pet_color": "Blanco",
    "pet_rstatus": "Castrado"},
    True, "Puede sin genero: vacio"),
    ({
    "pet_names": "Canela",
    "species_id" : "1",
    "pet_race": " Bulldog",
    "pet_datebirth": date.today(),
    "pet_microchip" : "123456789",
    "pet_gender": "Macho",
    "pet_color": "Bl",
    "pet_rstatus": "Castrado"},
    False,
    "Color no existe"),
    ({
    "pet_names": "Sirius",
    "species_id" : "",
    "pet_race": " ",
    "pet_datebirth": "",
    "pet_microchip" : "",
    "pet_gender": "",
    "pet_color": "",
    "pet_rstatus": ""},
    True,
    "Solo el nombre"),
    ({
    "pet_names": "Sirius",
    "species_id" : "",
    "pet_race": " ",
    "pet_datebirth": date.today() + timedelta(days=1),
    "pet_microchip" : "",
    "pet_gender": "",
    "pet_color": "",
    "pet_rstatus": ""},
    False,
    "No se permite fecha futura"),
    ({
    "pet_names": "GaAur'a",
    "species_id" : "",
    "pet_race": " ",
    "pet_datebirth": date.today(),
    "pet_microchip" : "",
    "pet_gender": "",
    "pet_color": "",
    "pet_rstatus": ""},
    True,
    "Limpia los nombres raros"
    ),
    ({
    "pet_names": "Soy Letra",
    "species_id" : "",
    "pet_race": " ",
    "pet_datebirth": date.today(),
    "pet_microchip" : "F600",
    "pet_gender": "",
    "pet_color": "",
    "pet_rstatus": ""},
    False,
    "No permite letras en numeros"
    )]

casos_update = [
    ({
    "pet_names": "Ic",
    "species_id" : "",
    "pet_race": "",
    "pet_datebirth": date.today(),
    "pet_microchip" : "",
    "pet_gender": "",
    "pet_color": "",
    "pet_rstatus": ""
    }, False, "En caso de:Nombre muy corto"),
    ({
    "pet_names": "Ma ",
    "species_id" : "1", 
    "pet_race": "Pug",
    "pet_datebirth": date.today(),
    "pet_microchip" : "123456789",
    "pet_gender": "Hembra",
    "pet_color": "Blanco",
    "pet_rstatus": "Activo"},
    False,
    "Debe fallar por nombre muy corto"),
    ({
    "pet_names": "Kyomi",
    "species_id" : "1",
    "pet_race": " Bulldog",
    "pet_datebirth":date.today() - timedelta(days=365),
    "pet_microchip" : "",
    "pet_gender": "Macho",
    "pet_color": "Blanco",
    "pet_rstatus": "Castrado"},
    True,
    "Puede ser: a year ago"),
    ({
    "pet_names": "Sultan",
    "species_id" : "1",
    "pet_race": " Bulldog",
    "pet_datebirth": date.today(),
    "pet_microchip" : "",
    "pet_gender": "",
    "pet_color": "Blanco",
    "pet_rstatus": "Castrado"},
    True, "Puede sin genero: vacio"),
    ({
    "pet_names": "Canela",
    "species_id" : "1",
    "pet_race": " Bulldog",
    "pet_datebirth": date.today(),
    "pet_microchip" : "123456789",
    "pet_gender": "Macho",
    "pet_color": "Bl",
    "pet_rstatus": "Castrado"},
    False,
    "Color no existe"),
    ({
    "pet_names": "Sirius",
    "species_id" : "",
    "pet_race": " ",
    "pet_datebirth": "",
    "pet_microchip" : "",
    "pet_gender": "",
    "pet_color": "",
    "pet_rstatus": ""},
    True,
    "Solo el nombre"),
    ({
    "pet_names": "Sirius",
    "species_id" : "",
    "pet_race": " ",
    "pet_datebirth": date.today() + timedelta(days=1),
    "pet_microchip" : "",
    "pet_gender": "",
    "pet_color": "",
    "pet_rstatus": ""},
    False,
    "No se permite fecha futura"),
    ({
    "pet_names": "GaAur'a",
    "species_id" : "",
    "pet_race": " ",
    "pet_datebirth": date.today(),
    "pet_microchip" : "",
    "pet_gender": "",
    "pet_color": "",
    "pet_rstatus": ""},
    True,
    "Limpia los nombres raros"
    ),
    ({
    "pet_names": "Soy Letra",
    "species_id" : "",
    "pet_race": " ",
    "pet_datebirth": date.today(),
    "pet_microchip" : "F600",
    "pet_gender": "",
    "pet_color": "",
    "pet_rstatus": ""},
    False,
    "No permite letras en numeros"
    ),
    ({
    "pet_names": "",
    "species_id" : "",
    "pet_race": " ",
    "pet_datebirth": "",
    "pet_microchip" : "",
    "pet_gender": "",
    "pet_color": "",
    "pet_rstatus": ""},
    False,
    "Sin datos vacios"
    )]

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
    form.species_id.choices = [(1, "Perro"), (2, "Gato"), (3, "Ave")]
    
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
    form = PetUpdate(formdata=mdict)
    
    form.species_id.choices = [(1, "Perro"), (2, "Gato"), (3, "Ave")]
    
    assert form.validate() == resultado_esperado, f"Fallo en Update: {descripcion}. Errores: {form.errors}"
