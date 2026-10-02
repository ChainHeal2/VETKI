"""
CRUD-MASCOTA
"""
from flask import (Blueprint,flash,render_template,url_for,redirect,request, session)

bp = Blueprint('index',__name__)

@bp.route('/',methods = ['GET','POST'])
def index():
    """Pagina de index"""
    return render_template('base.html')

@bp.route('/privacidad',methods = ['GET'])
def privacidad():
    """Pagina de privacidad"""
    return render_template('/aboutme/1.html')

@bp.route('/terminos',methods = ['GET'])
def terminos():
    """Pagina de términos"""
    return render_template('/aboutme/2.html')