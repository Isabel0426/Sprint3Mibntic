import sqlite3
from sqlite3 import Error
from flask import current_app, g

isUserCreationActive = False

def get_db():
    try:
        if 'db' not in g:
            print('conectada')
            g.db = sqlite3.connect('web_database.db')
        return g.db
    except Error:
        print(Error)


def close_db():
    db = g.pop( 'db', None )

    if db is not None:
        db.close()

def update_password(new_pass, usuario):
    db = get_db()
    db.cursor()
    db.execute(
        'UPDATE usuario set contraseña = ? where usuario = ?', (new_pass, usuario)
    )
    db.commit()
    return close_db()

def enable_user_edit(edit_db):
    global isUserCreationActive
    isUserCreationActive = edit_db
    return

def update_values_on_edit(name, username, email, password):
    global  nombre, usuario, correo, passWord
    nombre   = name
    usuario  = username
    correo   = email
    passWord = password

def get_db_status():
    return isUserCreationActive

def add_validated_user():
    if (get_db_status()):
        global  isUserCreationActive, nombre, usuario, correo, passWord
        isUserCreationActive = False
        db = get_db()
        db.executescript(
            "INSERT INTO usuario (nombre, usuario, correo, contraseña) VALUES ('%s','%s','%s','%s')" % (nombre, usuario, correo, passWord)
        )
        db.commit()
        close_db()
    else:
        print('Usuario no puede ser creado sin valición de la cuenta')
    return