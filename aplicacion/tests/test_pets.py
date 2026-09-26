"""
Pruebas de CRUD Mascota
pytest aplicacion/tests/test_pets.py -vv -s --showlocals
"""
import pytest
from .test_pet_form import casos_create,casos_update
#Recordar que el usuario siempre manda STRINGS
#(input, esperado, boolean, mensaje_error_esperado)
#(' Ichiro','Ichiro',True),
# Combinamos tus listas en escenarios completos
@pytest.mark.parametrize('case,boolean,motivo',casos_create)
def test_pet_create(client,case,boolean,motivo):
    """
    Casos de prueba
    1.STATUS 200
    2.STATUS 302
    3.ERROR 200

        * assert 200 == 300
        Esto fuerza a fallar el TEST
     
    """
    response = client.post('/pet_create',data = case)

    if boolean and response.status_code != 302:
        #Caso Quedar atrapado en el formulario
        print(f"\n--- ERROR EN CASO: {motivo} ---")
    if boolean:
        #Caso de solicitud aceptada
        assert response.status_code == 302
        print(f"\n--- SOLICITUD: {motivo} {case} ---")
    else:
        #Error de la solicitud
        assert response.status_code == 200
        print(f"\nError en caso de: '{motivo}': {case}")

@pytest.mark.parametrize('case,boolean,motivo', casos_update)
def test_pet_update(client, db_context, case, boolean, motivo):
    """(conecta_db, inserta_base, extrae_id_llave, envia_post, aserta ->)"""
    db, cursor = db_context
    insert_sql = "INSERT INTO pet_data (pet_names) VALUES (%s) RETURNING pet_id"
    cursor.execute(insert_sql, ("Nombre inicial",))
    resultado = cursor.fetchone()
    if resultado is None:
        pytest.fail("Error: No se generó el registro inicial")
    try:
        id_pet = resultado['pet_id']
    except (TypeError, KeyError):
        id_pet = resultado[0]
    db.commit()
    url = f"/pet_update_form/{id_pet}"
    response = client.post(url, data=case)
    if boolean and response.status_code != 302:
        #Caso Quedar atrapado en el formulario
        print(f"\n--- ERROR EN CASO: {motivo} ---")
    if boolean:
        #Caso de solicitud aceptada
        assert response.status_code == 302
        print(f"\n--- SOLICITUD: {motivo} {case} ---")
    else:
        #Error de la solicitud
        assert response.status_code == 200
        print(f"\nError en caso de: '{motivo}': {case}")
