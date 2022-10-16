import sqlite3
from sqlite3 import Error
from flask import current_app, g

mensajeactive = False

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

def mensajes(edit_db):
    global mensajeactive
    mensajeactive = edit_db
    return
 
def enviar_mensaje(fromm, to1, asunto, mensaje):
    global  from1, to12, asuntos, mensajees
    from1 = fromm
    to12 = to1
    asuntos  = asunto
    mensajees = mensaje

def get_db_status():
  return mensajeactive

def add_validated_menssage():
    if (get_db_status()):
        global  mensajeactive, fromm, to1, asunto, mensaje
        mensajeactive = False
        db = get_db()
        db.executescript(
            "INSERT INTO mensajes (fromm, to1, asunto, mensaje) VALUES ('%s','%s','%s','%s')" % (fromm, to1, asunto, mensaje)
        )
        db.commit()
        close_db()
    else:
        print()
    return