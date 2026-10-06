"""Creamos la conexion de la base de datos"""
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import current_app, g
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from .schema import metadata


orm_db = SQLAlchemy(metadata=metadata)


def _include_migration_name(name, object_type, parent_names):
    """Limita las migraciones al esquema vetki de esta aplicación."""
    if object_type == "schema":
        return name == "vetki"
    if object_type == "table":
        return parent_names.get("schema_name") == "vetki"
    return True


migrate = Migrate(
    compare_type=True,
    include_schemas=True,
    include_name=_include_migration_name,
    version_table_schema="vetki",#añadido para que las migraciones se guarden en el esquema vetki
)

def get_db():
    """funcion que crea db en g
    g = es como una variable "global" una instancia cada usuario tiene su g.
    una vez que g hace su peticion y la bd responde y g se destruye.
    """
    if 'db' not in g:
        # Si no existe, creamos la conexión y el cursor una sola vez por petición
        conn = psycopg2.connect(
            host = current_app.config['DATABASE_HOST'],
            user = current_app.config['DATABASE_USER'],
            port = current_app.config['DATABASE_PORT'],
            password = current_app.config['DATABASE_PASSWORD'],
            database = current_app.config['DATABASE'],
            connect_timeout=5
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
        # Agrega esta línea para que Postgres encuentre tus tablas automáticamente
        cur.execute("SET search_path TO vetki, public")
        g.db = conn
        g.c = cur
    return g.db, g.c

def close_db(e=None):
    """Cierra la conexion con la base de datos"""
    db = g.pop('db',None)
    if db is not None:
        db.close()


def init_app(app):
    """Inicializa Flask-SQLAlchemy, Flask-Migrate y la conexión psycopg2."""
    orm_db.init_app(app)
    migrate.init_app(app, orm_db)
    app.teardown_appcontext(close_db)
