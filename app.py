import os
import json
from pprint import pprint
from flask import Flask, render_template, redirect, request, session
from flask_session import Session
import yagmail as yagmail
from flask import Flask, render_template, flash, request, redirect, url_for, jsonify
import utils
import yagmail
from db import close_db, get_db, update_password, update_values_on_edit, enable_user_edit, get_db_status, add_validated_user
from formulario import Contactenos
from code import create_validation_code, get_last_code, reset_code
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask( __name__ )
app.secret_key = os.urandom( 24 )
validRestoringEmail = False

@app.route( '/' )
def index():
    return render_template( 'login.html' )

@app.route('/newmessage', methods=['POST'] )
def newmessage():
         return "gg"

@app.route( '/register', methods=('GET', 'POST') )
def register():
    try:
        if request.method == 'POST':

            name= request.form['nombre']
            username = request.form['username']
            password = request.form['password']
            email = request.form['correo']
            error = None
            db = get_db()

            if not utils.isUsernameValid( username ):
                error = "El usuario debe ser alfanumerico o incluir solo '.','_','-'"
                flash( error )
                return render_template( 'register.html' )

            if not utils.isPasswordValid( password ):
                error = 'La contraseña debe contenir al menos una minúscula, una mayúscula, un número, un caracter especial y 8 caracteres'
                flash( error )
                return render_template( 'register.html' )

            if not utils.isEmailValid( email ):
                error = 'Correo invalido'
                flash( error )
                return render_template( 'register.html' )

            if db.execute( 'SELECT * FROM usuario WHERE usuario = ?', (username,) ).fetchone() is not None:
                error = 'El usuario {} ya existe'.format( username )
                flash( error )
                return render_template( 'register.html' )

            if db.execute( 'SELECT * FROM usuario WHERE correo = ?', (email,) ).fetchone() is not None:
                error = 'El correo {} ya existe'.format( email )
                flash( error )
                return render_template( 'register.html' )

            # FIXME Solve hash checking on logging method and hash should be separated
            # hash = generate_password_hash(password)

            # Avoiding user creation without auth
            enable_user_edit(True)
            update_values_on_edit(name, username, email, password)


            # db.executescript(
            #     "INSERT INTO usuario (nombre, usuario, correo, contraseña) VALUES ('%s','%s','%s','%s')" % (name, username, email, password)
            # )
            # db.commit()

            close_db()

            sent_code = create_validation_code()
            correo_electronico=yagmail.SMTP('ymfloresl@unal.edu.co','Lagrange45') #correo electronico es la variable que almacena el correo y la contraseña
            correo_electronico.send(
                to=email,
                subject='Plataforma de mensajeria: Validación de correo',
                contents='Este es su código de verificación para {}: {}'.format(username, sent_code)
            )
            return render_template( 'validation.html' )
        return render_template( 'register.html' )
    except:
        flash('Puede que requiera revisar el correo de remitente')
        return render_template( 'error.html' )


@app.route( '/login', methods=('GET', 'POST') )
def login():
        
    try:
        if request.method == 'POST':
            db = get_db()
            error = None
            username = request.form['username']
            password = request.form['password']

            if not username:
                error = 'Debes ingresar el usuario'
                flash( error )
                return render_template( 'login.html' )

            if not password:
                error = 'Contraseña requerida'
                flash( error )
                return render_template( 'login.html' )

            user = db.execute(
                'SELECT * FROM usuario WHERE usuario = ? AND contraseña = ? ', (username, password)
            ).fetchone()

            close_db()

            if user is None:
                error = 'Usuario o contraseña inválidos'
                flash( error )
                return render_template( 'login.html' )
            else:
                session["usuario"] = username
                return render_template( 'indexchat.html')

        return render_template( 'login.html' )
    except:
        return render_template( 'login.html' )

@app.route( '/indexchat', methods=('GET', 'POST'))
@app.route( '/indexchat/<string:usuario>', methods=('GET', 'POST'))
def send(usuario=""): #Mocking send message
    if usuario == "":
        try:
            if request.method == 'POST':
                    receiver = request.form['receiver']
                    asunto   = request.form['asunto']
                    mensaje  = request.form['mensaje']

                    flash('{}: Su nensaje fue enviado a <{}> con asunto <{}> y cuerpo: {}' .format(usuario, receiver, asunto, mensaje))
        except:
            flash("Sending fail")
        
        # return render_template('indexchat.html', usuario=usuario)
        return render_template('indexchat.html')
    else:
        flash("No hay sesion valida iniciada")
        return render_template('indexchat.html')

@app.route( '/validation', methods=('GET', 'POST'))
@app.route( '/validation/<string:usuario>', methods=('GET', 'POST'))
def validation(usuario=""):
    global validRestoringEmail
    try:
        if request.method == 'POST':
            code = request.form['code']
            sent_code = get_last_code()
            if(code == sent_code):
                reset_code()

                if validRestoringEmail == True:
                    validRestoringEmail = False
                    if usuario=="":
                        # return render_template('change_pass.html', usuario=usuario)
                        return render_template('new_pass.html')
                    else:
                        return render_template('new_pass.html')
                else:
                    if(get_db_status()):
                        add_validated_user()
                        flash('Usuario creado y validado')
                        

                    else:
                        flash('Registro no exitoso')
                        return render_template('register.html')
            
                    return render_template('login.html')
    
        return render_template('validation.html')    
    except:
        flash( 'Revisa tu correo para activar tu cuenta' )
        return render_template('validation.html')

    
@app.route( '/change_pass', methods=('GET', 'POST'))
@app.route( '/change_pass/<string:usuario>', methods=('GET', 'POST'))
def change_pass(usuario=""):
    if usuario!="":
        db = get_db()
        user_data = db.execute(
                'SELECT * FROM usuario WHERE usuario = ?', (usuario,)
        ).fetchone()
        close_db()

        if user_data is None:
            flash('Usuario inválido')
            return render_template( 'new_pass.html')
        else:
            return render_template( 'new_pass.html')
            # return render_template( 'new_pass.html', usuario = usuario)
    else:
        try:
            user    = request.form['username']
            oldpass = request.form['password']
            newpass = request.form['newpass']

            if request.method == 'POST':
                db = get_db()
                message = None

                if not user:
                    message = 'Debes ingresar el usuario'
                    flash( message )
                    return render_template( 'change_pass.html')

                if not oldpass:
                    message = 'Contraseña requerida'
                    flash( message )
                    return render_template( 'change_pass.html')

                if not newpass:
                    message = 'Nueva ontraseña requerida'
                    flash( message )
                    return render_template( 'change_pass.html')

                user_data = db.execute(
                    'SELECT * FROM usuario WHERE usuario = ? AND contraseña = ? ', (user, oldpass)
                ).fetchone()

                close_db()

                if user_data is None:
                    message = 'Usuario o contraseña inválidos'
                else:
                    update_password(newpass, user)
                    message = 'Contraseña modificada'

                flash(message)
                return render_template('change_pass.html')
            return render_template('change_pass.html')
        except:
            return render_template('change_pass.html')

    
@app.route( '/restore_pass', methods=('GET', 'POST'), )
def restore_pass():
    global validRestoringEmail
    try:
        if request.method == 'POST':
            correo    = request.form['restoreCorreo']
            message = None
            validRestoringEmail = False

            if not utils.isEmailValid( correo ):
                message = 'Correo invalido'
                flash( message )
                return render_template( 'restore_pass.html' )

            db = get_db()

            user_data = db.execute( 'SELECT * FROM usuario WHERE correo = ?', (correo,) ).fetchone()
            
            if user_data is not None:
                validRestoringEmail  = True   
            close_db

            if validRestoringEmail == True:
                nombre = user_data[1]
                usuario = user_data[2]
                pass_code = create_validation_code()
                set_restoring_user(usuario)
                correo_electronico=yagmail.SMTP('ymfloresl@unal.edu.co','Lagrange45') #correo electronico es la variable que almacena el correo y la contraseña
                correo_electronico.send(
                    to=correo,
                    subject='Recuperación de contraseña',
                    contents='Hola {}. Digite este codigo {} para poder recuperar la contrseña del usuario {}'.format(nombre, pass_code, usuario)
                )
                message = 'Correo de verificación enviado'
                flash( message )
                # return render_template( 'validation.html', usuario = usuario)
                return render_template( 'validation.html')

        # flash( message )
    except:
        flash('Issue on restoring password')
        return render_template( 'restore_pass.html' )

    return render_template('restore_pass.html')

@app.route( '/new_pass', methods=('GET', 'POST'))
@app.route( '/new_pass/<string:usuario>', methods=('GET', 'POST'))
def new_pass(usuario=""):
    # return render_template( 'new_pass.html', usuario = usuario)
    if usuario == "":
        try:
            if request.method == 'POST':
                user = get_restoring_user()
                newpass    = request.form['newpass']
                update_password(newpass, user)
                flash('Contraseña modificada exitosamente')
            return render_template( 'new_pass.html')
        except:
            return render_template( 'new_pass.html')
    # else:
        # user = usuario
        # Logic required on usuario as parameter
        # db = get_db()
        # user_data = db.execute(
        #         'SELECT * FROM usuario WHERE usuario = ?', (user,)
        # ).fetchone()
        # close_db()
        # if user_data is None:
        #     flash('Usuario inválido')
        #     return render_template( 'new_pass.html')
        # else:
        #     return render_template( 'new_pass.html')
        #     return render_template( 'new_pass.html', usuario = usuario)       


def set_restoring_user(user):
    global last_user
    last_user = user
    return

def get_restoring_user():
    return last_user