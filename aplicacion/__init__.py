"""Para mi prometida con todo mi amor."""
import os
import warnings
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.engine import URL
from werkzeug.middleware.proxy_fix import ProxyFix

warnings.filterwarnings("ignore", category=UserWarning, module="flask_limiter")
csrf = CSRFProtect()


def create_app():
    """Creamos la APP"""
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("FLASK_SECRET_KEY"),
        DATABASE_HOST=os.environ.get("FLASK_DATABASE_HOST"),
        DATABASE_PORT=os.environ.get("FLASK_DATABASE_PORT", 5432),
        DATABASE_USER=os.environ.get("FLASK_DATABASE_USER"),
        DATABASE_PASSWORD=os.environ.get("FLASK_DATABASE_PASSWORD"),
        DATABASE=os.environ.get("FLASK_DATABASE"),
        COOKIE_SECURE=os.environ.get("FLASK_COOKIE_SECURE"),
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = URL.create(
        drivername="postgresql+psycopg2",
        username=app.config["DATABASE_USER"],
        password=app.config["DATABASE_PASSWORD"],
        host=app.config["DATABASE_HOST"],
        port=int(app.config["DATABASE_PORT"]) if app.config["DATABASE_PORT"] else None,
        database=app.config["DATABASE"],
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Inicializas CSRF aquí para que inyecte el token globalmente en Jinja
    csrf.init_app(app)

    # Base de datos
    from . import db
    db.init_app(app)

    # Blueprints
    from aplicacion.blueprints.index import index
    app.register_blueprint(index.bp)

    from aplicacion.blueprints.pet import pet
    app.register_blueprint(pet.bp)

    from aplicacion.blueprints.appointment import appointment
    app.register_blueprint(appointment.bp)

    from aplicacion.blueprints.user import user
    app.register_blueprint(user.bp)

    from aplicacion.blueprints.auth import auth
    app.register_blueprint(auth.bp)

    from aplicacion.blueprints.medical import medical
    app.register_blueprint(medical.bp)

    from aplicacion.blueprints.analytic import analytic
    app.register_blueprint(analytic.bp)

    from aplicacion.blueprints.google_login.google_login import google_bp
    app.register_blueprint(google_bp, url_prefix="/login")

    from aplicacion.blueprints.carnet_vacuna import carnet
    app.register_blueprint(carnet.bp)

    from aplicacion.blueprints.vaccination import vaccination
    app.register_blueprint(vaccination.bp)
    
    from aplicacion.limiter import limiter as api_limiter
    
    from aplicacion.blueprints.api_routes import qr
    app.register_blueprint(qr.bp)
    
    api_limiter.init_app(app)

    return app
