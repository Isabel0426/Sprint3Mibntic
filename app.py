import os

import yagmail as yagmail
from flask import Flask, render_template, flash, request, redirect, url_for, jsonify
import utils
import yagmail
from db import close_db, get_db
from formulario import Contactenos
from code import create_validation_code, get_last_code, reset_code
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask( __name__ )
app.secret_key = os.urandom( 24 )


@app.route( '/' )
def index():
    return render_template( 'login.html' )


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

            # FIXME Solve hash checking on logging method and hash should be separated
            # hash = generate_password_hash(password)

            db.executescript(
                "INSERT INTO usuario (nombre, usuario, correo, contraseña) VALUES ('%s','%s','%s','%s')" % (name, username, email, password)
            )
            db.commit()

            close_db()

            sent_code = create_validation_code()
            correo_electronico=yagmail.SMTP('floresy@uninorte.edu.co','cocodruLLo45') #correo electronico es la variable que almacena el correo y la contraseña
            correo_electronico.send(
                to=email,
                subject='Plataforma de mensajeria: Validación de correo',
                contents='Este es su código de verificación para {}: {}'.format(username, sent_code)
            )
            return redirect( 'validation' )
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
            else:
                return redirect( 'send' )
            flash( error )
            return render_template( 'login.html' )

        return render_template( 'login.html' )
    except:
        return render_template( 'login.html' )

@app.route( '/send', methods=('GET', 'POST'))
def send():
    try:
       if request.method == 'POST':
            receiver = request.form['receiver']
            asunto   = request.form['asunto']
            mensaje  = request.form['mensaje']

            flash('Mensaje fue enviado a <{}> con asunto <{}> y cuerpo: {}' .format(receiver, asunto, mensaje))
    except:
        flash("Sending fail")
    
    return render_template('send.html')

@app.route( '/validation', methods=('GET', 'POST'))
def validation():
    flash( 'Revisa tu correo para activar tu cuenta' )
    try:
       if request.method == 'POST':
            code = request.form['code']
            sent_code = get_last_code()
            if(code == sent_code):
                reset_code()
                return redirect('login')
            return render_template('validation.html')    
    except:
        return render_template('validation.html')

    return render_template('validation.html')    

if __name__ == '__main__':
    app.run()