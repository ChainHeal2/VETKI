"""Para mi prometida con todo mi amor.
"""
import os
from flask import Flask
def create_app():
    """Creamos la APP
    Recuerda tus variables de entorno

    FLASK_DATABASE_HOST='127.0.0.1'
    FLASK_DATABASE_USER='user'
    FLASK_DATABASE_PASSWORD='password'
    FLASK_DATABASE='tudatabase'
    FLASK_APP='aplicacion:create_app'
    """
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY = os.environ.get('FLASK_SECRET_KEY'),
        DATABASE_HOST = os.environ.get('FLASK_DATABASE_HOST'),
        DATABASE_PORT= os.environ.get('FLASK_DATABASE_PORT' or 5432),
        DATABASE_USER = os.environ.get('FLASK_DATABASE_USER'),
        DATABASE_PASSWORD = os.environ.get('FLASK_DATABASE_PASSWORD'),
        DATABASE = os.environ.get('FLASK_DATABASE'),
    )

    from . import db
    db.init_app(app)

    from aplicacion.index import index
    app.register_blueprint(index.bp)

    from aplicacion.pet import pet
    app.register_blueprint(pet.bp)

    from aplicacion.appointment import appointment
    app.register_blueprint(appointment.bp)    
    
    from aplicacion.user import user
    app.register_blueprint(user.bp)
    
    from aplicacion.auth import auth
    app.register_blueprint(auth.bp)

    from aplicacion.medical import medical
    app.register_blueprint(medical.bp)

    from aplicacion import api
    app.register_blueprint(api.bp)
    api.limiter.init_app(app)
    app.cli.add_command(api.check_vaccination_alerts_command)

    from aplicacion.google_login.google_login import google_bp
    app.register_blueprint(google_bp, url_prefix="/login")
    
    return app
