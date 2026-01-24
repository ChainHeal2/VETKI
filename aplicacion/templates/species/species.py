import functools
from flask import (Blueprint,flash,g,render_template,url_for,session,redirect,request)
from werkzeug.security import check_password_hash,generate_password_hash
from aplicacion.db import get_db
from aplicacion.functions.function import limpiar_datos,limpiar_formulario
from aplicacion.templates.auth.auth import login_required


bp = Blueprint('species',__name__)
@bp.before_request # 1. Este decorador le dice a Flask: "Ejecuta esto antes de cada ruta de este archivo"
@login_required   # 2. Este decorador aplica tu lógica de seguridad (si g.user es None, redirige)
def proteger_rutas():
    """Protege el Blueprint"""
    pass
@bp.route('/especies',methods = ['GET','POST'])
def especies():
    """Pagina tabla de especies"""
    if request.method == 'GET':
        db,c = get_db()
        c.execute('select species_id,name_species from species;')
        tabla_especie = c.fetchall()
        c.close()
        return render_template('species/tabla_especie.html',tabla = limpiar_datos(tabla_especie))
    elif request.method == 'POST':
        error = None
        formulario_usuario = request.form.to_dict()
        formulario_bueno = limpiar_formulario((formulario_usuario))
        if len(formulario_bueno) == 0 or formulario_bueno['species_user'] in '1234567890' :
            error = 'no ingreso ninguna especie'
            flash(error)
        else:
            especie_nueva = formulario_bueno['species_user']
            db,c = get_db()
            c.execute('select name_species from species where name_species = %s', (especie_nueva,))
            if c.fetchone() is not None:
                error = 'La especie ya existe'
                flash(error)
            else:
                c.execute('insert into species(name_species) values (%s)',(especie_nueva,))
                db.commit()
                return redirect(url_for('species.especies'))
    return redirect(url_for('species.especies'))
@bp.route('/species/del_species/<int:species_id>',methods = ['POST','GET'])
def delete_specie(species_id):
    """Elimina la especie"""
    db,c = get_db()
    c.execute("delete from species where species_id = %s",(species_id,))
    db.commit()
    return(redirect(url_for('species.especies')))
@bp.route('/species/mod_species/<int:species_id>',methods = ['POST','GET'])
def update_specie(species_id):
    """Modifica la especie"""
    #pedimos la BD para asegurarnos de que nuestra tabla exista
    db,c = get_db()
    c.execute("select * from species where species_id = %s",(species_id,))
    tabla_especie = c.fetchall()
    db.commit()
    error = None
    if not tabla_especie:
        error = "No existe la tabla"
    if error is not None:
        flash(error)
    else:
        if request.method == 'POST':
            species_user= request.form['species_user']
            db,c = get_db()
            c.execute("update species set name_species = %s where species_id = %s",(species_user,species_id))
            db.commit()
            return redirect(url_for('species.especies'))