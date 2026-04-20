"""Creamos la conexion de la base de datos"""
import psycopg2
from psycopg2.extras import RealDictCursor
import click
from flask import current_app,g
from flask.cli import with_appcontext
from .schema import esquema

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
            password = current_app.config['DATABASE_PASSWORD'],
            database = current_app.config['DATABASE']
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
def init_db():
    """Ejecuta el esquema que creamos en schema"""
    db,c = get_db()
    for i in esquema:
        c.execute(i)
    db.commit()
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Inicia la base de datos segun el esquema de init_db"""
    init_db()
    click.echo('Base de datos inicializada')
def init_app(app):
    """Cierra la conexion despues de cada contexto y creamos la inicializacion
    por comandos"""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
