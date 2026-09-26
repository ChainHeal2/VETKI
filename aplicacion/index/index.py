"""
CRUD-MASCOTA
"""
from flask import (Blueprint,flash,render_template,url_for,redirect,request, session)

bp = Blueprint('index',__name__)

@bp.route('/',methods = ['GET','POST'])
def index():
    """Pagina de index"""
    return render_template('base.html')