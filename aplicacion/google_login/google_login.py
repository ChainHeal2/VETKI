import os
from flask import (url_for, redirect,session)
from flask_dance.contrib.google import make_google_blueprint, google
from aplicacion.db import get_db
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
        'openid',
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/calendar.events"
    ],
    offline=True,
    reprompt_consent=False,          # <-- IMPORTANTE: Evita que Google pida confirmación si ya tiene acceso
    reprompt_select_account=False,
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
    session['google_id'] = info.get('id')
    db, cursor = get_db()
    cursor.execute("select user_id,user_role from user_data where user_google_id = %s", (session['google_id'],))
    user_data = cursor.fetchone()
    if user_data is not None:
        session['user_id'] = user_data['user_id']
        session['user_role'] = user_data['user_role']
        return redirect(url_for('index.index'))
    cursor.execute("""
        INSERT INTO vetki.user_data (user_google_id, user_names, user_email) 
        VALUES (%s, %s, %s)
    """, (session['google_id'], session['user_name'], session['user_email']))
    db.commit()
    return redirect(url_for('index.index'))