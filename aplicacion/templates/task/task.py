import functools
from flask import (Blueprint,flash,g,render_template,url_for,session,redirect,request)
from werkzeug.security import check_password_hash,generate_password_hash
from aplicacion.db import get_db
from datetime import datetime,timezone

bp = Blueprint('task',__name__)
@bp.route('/tasks',methods = ['GET','POST'])
def view_task():
    """Pagina de tareas"""
    if request.method == 'GET':
        error = None
        db , c = get_db()
        c.execute('SELECT * FROM task;')

        tareas = c.fetchall()
        print(tareas)
        return render_template('task/view_task.html',tasks = tareas)
@bp.route('/create_tasks',methods = ['GET','POST'])
def create_task():
    """Crear una nueva tarea"""
    if request.method == "POST":
        error = None
        task_title = request.form['title_task']
        text_task = request.form['text_task']
        date_create_task = datetime.now(timezone.utc)
        db , c = get_db()
        c.execute(
            "insert into task(" \
            "title_task," \
            "task," \
            "date_create_task," \
            "date_end_task," \
            "fk_user_id) " \
            "values (%s,%s,%s,%s,%s)",
             (task_title,text_task,date_create_task,None,session['user_id']) )
        db.commit()
        return redirect(url_for('task.view_task'))

    return render_template('task/create_task.html')