from sqlite3.dbapi2 import TimestampFromTicks
from flask import Flask, render_template, request, redirect, make_response, session
from flask.scaffold import _matching_loader_thinks_module_is_package
from flask_wtf import FlaskForm, form, recaptcha
from flask_wtf.recaptcha.fields import RecaptchaField
from wtforms import StringField, PasswordField, SelectField, TextAreaField
from wtforms import validators
from wtforms.fields.core import BooleanField
from wtforms.validators import InputRequired, DataRequired, Length, AnyOf;
from flask.helpers import flash, url_for
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'claveoculta'
app.config['RECAPTCHA_PUBLIC_KEY'] = '6Lf-rKwcAAAAAIQKSPI2becEW2WRLZcUt80kp4z5'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6Lf-rKwcAAAAAIkQKHWtgSNhqNkEb2nmW7XkTZIC'

from peliculas import peliculas


def sql_connection():
    con = sqlite3.connect('db/basedatos.db')
    return con


class login_form(FlaskForm):
    username = StringField('Correo', validators=[InputRequired(message='El usuario es requerido')])
    password = PasswordField("Contraseña", validators=[InputRequired(message='Contraseña es requerida')])
    #recaptcha = RecaptchaField()

class register_form(FlaskForm):
    Nusername = StringField('Nombre Usuario', validators=[InputRequired(message='El mombre de usuario es requerido')])
    Nemail = StringField('Correo', validators=[InputRequired(message='El correo es requerido')])
    Npassword = PasswordField("Contraseña", validators=[InputRequired(message='La contraseña es requerida')])
    NRpassword = PasswordField("Repite la contraseña", validators=[InputRequired(message='La contraseña es requerida')])

class add_pelicula(FlaskForm):
    nombre = StringField('Nombre de la Pelicula', validators=[InputRequired(message='Agregue un nombre')])
    sinopsis = StringField('Sinopsis', validators=[InputRequired(message='Agregue una descripción')])
    cartelera = StringField('En cartelera | (1: Si | 0: No)', validators=[InputRequired(message='Agregue un valor')])
    image = StringField('Nombre de la Imagen (debe estar en static/img/)', validators=[InputRequired(message='Agregue la ruta')])

class add_comentario(FlaskForm):
    comentario = TextAreaField('Comentario', validators=[InputRequired(message='Escriba un comentario')])
    rating = SelectField('Calificación', choices=[(1,'1'), (2,'2'),(3,'3'), (4,'4'), (5,'5')])



@app.route('/', methods=['GET'])
def index():


    try:
        user_tipo = session['user_tipo']
        user_id = session['user_id']
    except:
        user_tipo = "Invitado"
        user_id = 0


    conP = sql_connection()
    curP = conP.cursor()
    statementP = 'SELECT * FROM Peliculas' 
    curP.execute(statementP)
    dataP = curP.fetchall()

    return render_template('index.html', page='inicio',  pelis = dataP, user_tipo = user_tipo, user_id = user_id)

@app.route('/login', methods=['GET','POST'])
def login():
    
    try:
        user_tipo = session['user_tipo']
        user_id = session['user_id']
    except:
        user_tipo = "Invitado"
        user_id = 0

    form = login_form()
    if form.validate_on_submit():

        con = sql_connection()
        cur = con.cursor()
        statement = 'SELECT * FROM Usuarios WHERE correo = ?' 
        cur.execute(statement, [form.username.data])
        data = cur.fetchall()

        try:
            
            if data [0][2] == form.password.data:

                
                
                if data[0][5] == 'Usuario':

                    session['user_tipo'] = data[0][5]
                    session['user_id'] = data[0][0]

                    return redirect('perfilUsuario/'+str(data[0][0]))

                if data[0][5] == 'Admin':

                    session['user_tipo'] = data[0][5]
                    session['user_id'] = data[0][0]
                    
                    return redirect('dashboard')

        except:
            pass
            
    return render_template('login.html', form=form, recaptcha=recaptcha, page='login', user_tipo=user_tipo, user_id=user_id)
        
 
@app.route('/registrar', methods=['GET','POST'])
def registrar():

    try:
        user_tipo = session['user_tipo']
        user_id = session['user_id']
    except:
        user_tipo = "Invitado"
        user_id = 0
    
    register = register_form()
    if register.validate_on_submit():
                
        con = sql_connection()
        cur = con.cursor()
        statement = 'INSERT INTO Usuarios (nombre_usuario, contraseña, correo, status, rol) VALUES (?,?,?,?,?)' 
        cur.execute(statement, [register.Nusername.data, register.Npassword.data, register.Nemail.data, '1', 'Usuario'])
        con.commit()

        return redirect (url_for('login'))
    else:
        return render_template('registrar.html', page='registrar', form = register, user_tipo=user_tipo, user_id=user_id)




@app.route('/dashboard/', methods=['GET','POST'])
def dashboard():

    try:
        user_tipo = session['user_tipo']
        user_id = session['user_id']
    except:
        user_tipo = "Invitado"
        user_id = 0

    #Consulta de PELICULAS

    conP = sql_connection()
    curP = conP.cursor()
    statementP = 'SELECT * FROM Peliculas' 
    curP.execute(statementP)
    dataP = curP.fetchall()

    #Consulta de USUARIOS

    conU = sql_connection()
    curU = conU.cursor()
    statementU = 'SELECT * FROM Usuarios' 
    curU.execute(statementU)
    dataU = curU.fetchall()

    if user_tipo=="Admin":
        return render_template('dashboard.html', page='dashboard', user = dataU, pelis = dataP, user_tipo=user_tipo, user_id=user_id)
    else:
        return redirect(url_for('login'))


@app.route('/detalleDeLaFuncion/<id>', methods=['GET','POST'])
def detalle_de_funcion(id):

    try:
        user_tipo = session['user_tipo']
        user_id = session['user_id']
    except:
        user_tipo = "Invitado"
        user_id = 0

    conP = sql_connection()
    curP = conP.cursor()
    statementP = 'SELECT * FROM Peliculas WHERE id_pelicula = ?' 
    curP.execute(statementP, [id])
    dataP = curP.fetchall()


    if user_tipo != "Invitado":
        try:
            return render_template('detalleDeLaFuncion.html', page='detalleFuncion', pelis = dataP[0], user_tipo=user_tipo, user_id=user_id)

        except:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))

    
        
@app.route('/detalleDePelicula/<id>', methods=['GET'])
def detalle_pelicula(id):

    try:
        user_tipo = session['user_tipo']
        user_id = session['user_id']
    except:
        user_tipo = "Invitado"
        user_id = 0

    

    #COnsulta Pelicula
    conP = sql_connection()
    curP = conP.cursor()
    statementP = 'SELECT * FROM Peliculas WHERE id_pelicula = ?' 
    curP.execute(statementP, [id])
    dataP = curP.fetchall()


    #Consulta Comentarios
    conC = sql_connection()
    curC = conC.cursor()
    statementC = 'SELECT * FROM Comentarios WHERE id_pelicula = ?' 
    curC.execute(statementC, [id])
    dataC = curC.fetchall()

    try:
        return render_template('detalleDePelicula.html', page='detallePelicula', pelis = dataP[0], com = dataC, user_tipo=user_tipo, user_id=user_id)

    except:
        return redirect(url_for('index'))
    

@app.route('/perfilUsuario/<nom_usuario>', methods=['GET'])
def perfil_usuario(nom_usuario):

    try:
        user_tipo = session['user_tipo']
        user_id = session['user_id']
    except:
        user_tipo = "Invitado"
        user_id = 0

    if user_tipo == "Usuario":
        if str(nom_usuario) == str(user_id):
            return render_template('perfilUsuario.html', page='perfilUsuario', name = nom_usuario, user_tipo=user_tipo, user_id=user_id)
        else:
            return redirect('../perfilUsuario/'+str(user_id))
    elif user_tipo == "Admin":
        return redirect(url_for('dashboard'))

    else:
        return redirect(url_for('login'))

@app.route('/peliculas/', methods=['GET'])
def todas_peliculas():

    try:
        user_tipo = session['user_tipo']
        user_id = session['user_id']
    except:
        user_tipo = "Invitado"
        user_id = 0

    conP = sql_connection()
    curP = conP.cursor()
    statementP = 'SELECT * FROM Peliculas' 
    curP.execute(statementP)
    dataP = curP.fetchall()

    #COnsulta de la tabla comentarios para calcular el promedio por pelicula


    return render_template('todasPeliculas.html', page='peliculas', pelis = dataP, user_tipo=user_tipo, user_id=user_id)



@app.route('/agregarPelicula/', methods=['POST','GET'])
def agregar_peliculas():

    try:
        user_tipo = session['user_tipo']
        user_id = session['user_id']
    except:
        user_tipo = "Invitado"
        user_id = 0

    if user_tipo == "Admin":

        addPelis = add_pelicula()

        if addPelis.validate_on_submit():

            con = sql_connection()
            cur = con.cursor()
            statement = 'INSERT INTO Peliculas (nombre, sinopsis, cartelera, imagen) VALUES (?,?,?,?)' 
            cur.execute(statement, [addPelis.nombre.data, addPelis.sinopsis.data, addPelis.cartelera.data, addPelis.image.data])
            con.commit()

            
            return redirect('/dashboard')
        else: 
            return render_template('agregarPelicula.html', form = addPelis, user_tipo=user_tipo, user_id=user_id)
    else:
        return redirect(url_for('login'))


@app.route('/dashboard/eliminar/<id_pelicula>')
def eliminar_pelicula(id_pelicula):

    #Statement en SQL eliminando el registro de la tabla películas el id = id_pelicula

    pass
    #return render_template('dashboard.html', page='dashboard', user = usuarios, pelis = peliculas)


@app.route('/agregarComentario/<id>', methods=['GET','POST'])
def agregarComentario(id):
    
    
    try:
        user_tipo = session['user_tipo']
        user_id = session['user_id']
    except:
        user_tipo = "Invitado"
        user_id = 0

    conP = sql_connection()
    curP = conP.cursor()
    statementP = 'SELECT * FROM Peliculas WHERE id_pelicula = ?' 
    curP.execute(statementP, [id])
    dataP = curP.fetchall()

    if user_tipo != "Invitado":

        addCom = add_comentario()
        if addCom.validate_on_submit():
            
            conA = sql_connection()
            curA = conA.cursor()
            statementA = 'INSERT INTO Comentarios (id_usuario, id_pelicula, texto, calificacion) VALUES (?,?,?,?)' 
            curA.execute(statementA, [1,id,addCom.comentario.data, addCom.rating.data])
            conA.commit()

            return redirect('../detalleDePelicula/'+str(id))
        
        else:
            
            try:
                return render_template('agregarComentario.html', form=addCom,page='agregarComentario', pelis = dataP[0], user_tipo=user_tipo, user_id=user_id)

            except:
                return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))


@app.route("/logout", methods=['GET','POST'])
def logout():
    session.clear()
    session['user_tipo'] = "Invitado"
    session['user_id'] = 0
    return redirect(url_for('index'))
    


if __name__ == '__main__':
    app.run(debug=True)
