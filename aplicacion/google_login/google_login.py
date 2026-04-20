import os
from flask import (url_for, redirect,session)
from flask_dance.contrib.google import make_google_blueprint, google
from dotenv import load_dotenv
from pathlib import Path

# Raíz absoluta del proyecto (3 niveles arriba desde aplicacion/google_login/)
raiz = Path(__file__).resolve().parent.parent.parent
ruta_env = os.path.join(raiz, '.env')
load_dotenv(dotenv_path=ruta_env)
google_bp = make_google_blueprint(
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    scope=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/calendar.events"
    ],
    offline=True,
    redirect_to="google.google_authorize"
)
@google_bp.route("/perfil")
def google_authorize():
    if not google.authorized:
        return redirect(url_for("google.login"))
    
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        return "Error al obtener datos de Google", 400
        
    info = resp.json()
    
    # Guardamos los datos en la sesión de Flask para usarlos luego
    session['user_email'] = info.get('email')
    session['user_name'] = info.get('name')
    
    return f"""
        <h1>Conexión Exitosa</h1>
        <p>Bienvenido, {info.get('name')}</p>
        <p>Email: {info.get('email')}</p>
        <p>ID de Google: {info.get('id')}</p>
        <br>
        <a href="/">Ir al Inicio de VETKI</a>
    """