"""
Una fixture 
es una función que proporciona un entorno fijo y repetible
para ejecutar pruebas.
Su objetivo principal es separar la lógica de preparación
(o limpieza) de la lógica de la prueba en sí misma.

* SETUP: codigo antes del yield (preparar objetos o conexiones)
* INYECCION:objeto despues del yield lo que la funcion de prueba
recibe como argumento
* Teardown:todo el codigo despues de la sentencia yield
se ejecuta automaticamente aunque el test falle y permite
cerrar conexiones o borrar registros.

entonces lo que se muestra es lo siguiente
"""
import pytest
from aplicacion import create_app
from ..db import get_db

@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,#solo para casos de prueba
    })
    yield app

@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

@pytest.fixture()
def db_context(app):
    """(crea_contexto, obtiene_db, cede_conexion, cierra_db)"""
    with app.app_context():
        db, cursor = get_db()
        yield db, cursor
        db.close()