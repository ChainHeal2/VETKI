"""
Todo lo que tiene que ver con Login y register de usuarios nuevos
"""
import functools
from flask import (Blueprint,flash,g,render_template,url_for,session,redirect,request)
from werkzeug.security import check_password_hash,generate_password_hash
from aplicacion.db import get_db

bp = Blueprint('auth',__name__)
@bp.route('/',methods = ['GET','POST'])
def index():
    """Pagina de index"""
    return render_template('base.html')
@bp.route('/register',methods = ['GET','POST'])
def register():
    """Pagina de registro"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db ,c = get_db()
        error = None
        c.execute('select user_id from user where username = %s',(username,))
        if not username:
            error ='Username es requerido'
        if not password:
            error = 'password es requerido'
        elif c.fetchone() is not None:
            error = 'El usuario ya se encuentra registrado'
        if error is None:
            c.execute('insert into user (username,password,email_user,level_user) values (%s,%s,%s,%s)',
            (username,generate_password_hash(password),"correo",1))
            db.commit()
            return redirect(url_for('auth.login'))
        flash(error)
    return render_template('auth/register.html')
@bp.route('/login',methods = ['GET','POST'])
def login():
    """Pagina de login"""
    if request.method == 'POST':
        error = None
        username = request.form['usuario']
        password = request.form['password']
        print(password)
        db ,c = get_db()
        c.execute('select user_id,username,password from user where username = %s',(username,))
        user = c.fetchone()
        if user is None:
            error = 'Usuario o contraseña incorrecta '
        elif not check_password_hash(user['password'],password):
            error = 'Usuario o contraseña incorrecta password '
        if error is None:
            session.clear()
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            print('sesion activa',session)
            return redirect(url_for('auth.index'))
        flash(error)
    return render_template('auth/login.html')
@bp.route('/logout')
def logout():
    """Cerrar sesion"""
    user_id = session.get('user_id')
    session.pop(user_id,None)
    session.clear()
    return redirect(url_for('auth.login'))
@bp.route('/ver_usuario',methods = ['GET','POST'])
def ver_user():
    """Ver lista de usuarios"""
    db , c = get_db()
    c.execute('SELECT * FROM view_username;')
    sql_view = c.fetchall()
    if request.method == 'POST':
        button = request.form.get('button')
        if button == "modify":
            print('modificando')
            pass
        if button == "delete":
            print('eliminando')
            pass
        
    return render_template('auth/tabla_usuario.html', view_user = sql_view)

@bp.before_app_request
def load_logged_in_user():
    """antes de cada peticion del usuario"""
    user_id = session.get('user_id')
    if user_id is None:
        g.user= None
    else:
        db,c = get_db()
        c.execute('select * from user where user_id = %s',(user_id,))
        g.user= c.fetchone()
def loguin_required(view):
    """protege las rutas"""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view
