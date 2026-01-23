import functools
from flask import (Blueprint,flash,g,render_template,url_for,session,redirect,request)
from werkzeug.security import check_password_hash,generate_password_hash
from aplicacion.db import get_db

bp = Blueprint('personal',__name__)
@bp.route('/especies',methods = ['GET','POST'])
def especies():
    """Pagina tabla de especies"""
    if request.method == 'GET':
        db,c = get_db()
        c.execute('select * from species;')
        tabla_especie = c.fetchall()
        c.close()
        return render_template('species/tabla_especie.html',tabla = tabla_especie)
    elif request.method == 'POST':
        especie_nueva = request.form['species_user']
        db,c = get_db()
        c.execute('select name_species from species where name_species = %s', (especie_nueva,))
        if c.fetchone() is not None:
            'La especie ya existe'
        else:
            c.execute('insert into species(name_species) values (%s)',(especie_nueva,))
            db.commit()
            return redirect(url_for('species.especies'))
    return render_template('base.html')
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
