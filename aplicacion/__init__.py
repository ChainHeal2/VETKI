"""Para mi prometida con todo mi amor."""
import os
import warnings
from flask import Flask
from flask_wtf.csrf import CSRFProtect
warnings.filterwarnings("ignore", category=UserWarning, module="flask_limiter")
csrf = CSRFProtect()


def create_app():
    """Creamos la APP"""
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("FLASK_SECRET_KEY"),
        DATABASE_HOST=os.environ.get("FLASK_DATABASE_HOST"),
        DATABASE_PORT=os.environ.get("FLASK_DATABASE_PORT", 5432),
        DATABASE_USER=os.environ.get("FLASK_DATABASE_USER"),
        DATABASE_PASSWORD=os.environ.get("FLASK_DATABASE_PASSWORD"),
        DATABASE=os.environ.get("FLASK_DATABASE"),
        COOKIE_SECURE=os.environ.get("FLASK_COOKIE_SECURE"),
    )
    
    # Inicializas CSRF aquí para que inyecte el token globalmente en Jinja
    csrf.init_app(app)

    # Base de datos
    from . import db
    db.init_app(app)

    # Blueprints
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
    
    from aplicacion.analytic import analytic
    app.register_blueprint(analytic.bp)

    from aplicacion.google_login.google_login import google_bp
    app.register_blueprint(google_bp, url_prefix="/login")
    
    from aplicacion.carnet_vacuna import carnet
    app.register_blueprint(carnet.bp)

    # API Blueprint, Limiter y CLI Command desde aplicacion.api
    from aplicacion.api import bp as api_bp, limiter as api_limiter, check_vaccination_alerts_command
    
    app.register_blueprint(api_bp)
    api_limiter.init_app(app)
    app.cli.add_command(check_vaccination_alerts_command)

    return app