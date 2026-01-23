"""Para mi prometida con todo mi amor.
"""
import os
from flask import Flask


def create_app():
    """Creamos la APP
    si quieres evitar estar escribiendo esto puedes usar:
    (al final del archivo activate de tu entorno de desarrolo (VENV))
    export FLASK_DATABASE_HOST='127.0.0.1'
    export FLASK_DATABASE_USER='user'
    export FLASK_DATABASE_PASSWORD='password'
    export FLASK_DATABASE='tudatabase'
    export FLASK_APP='aplicacion:create_app'
    """
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY = "mikey",
        DATABASE_HOST = os.environ.get('FLASK_DATABASE_HOST'),
        DATABASE_PORT= os.environ.get('FLASK_DATABASE_PORT'),
        DATABASE_USER = os.environ.get('FLASK_DATABASE_USER'),
        DATABASE_PASSWORD = os.environ.get('FLASK_DATABASE_PASSWORD'),
        DATABASE = os.environ.get('FLASK_DATABASE'),
    )

    from . import db
    db.init_app(app)

    from .templates.auth import auth
    app.register_blueprint(auth.bp)

    from .templates.species import species
    app.register_blueprint(species.bp)

    return app