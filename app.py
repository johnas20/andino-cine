from flask import Flask, render_template, request, redirect
from flask_wtf import FlaskForm, recaptcha
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
    username = StringField('Correo', validators=[InputRequired(message='El usuario es requerido'),Length(min=1,max=99, message='El usuario debe tener entre 5 y 10 caracteres')])
    password = PasswordField("Contraseña", validators=[InputRequired(message='Contraseña es requerida')])
    recaptcha = RecaptchaField()

class register_form(FlaskForm):
    Nusername = StringField('Nombre Usuario', validators=[InputRequired(message='El mombre de usuario es requerido'),Length(min=1,max=99, message='El nombre debe tener por lo menos un caracter')])
    Nemail = StringField('Correo', validators=[InputRequired(message='El correo es requerido')])
    Npassword = PasswordField("Contraseña", validators=[InputRequired(message='La contraseña es requerida')])
    NRpassword = PasswordField("Repite la contraseña", validators=[InputRequired(message='La contraseña es requerida')])

class add_pelicula(FlaskForm):
    nombre = StringField('nombre de la pelicula')
    sinopsis = StringField('sinopsis')
    cartelera = StringField('En cartelera (1:Si o 0:no)')
    image = StringField('nombre de la imagen (debe estar en static/img/)')


#Ejemplo de dos usuarios para los layouts de perfilUsuario y dashboard del admin
usuarios = {
    1:{'Nombre': 'usuario1', 'Correo': 'usuario1@gmailcom', 'Rol': 'usuario' },
    2:{'Nombre': 'admin1', 'Correo': 'admin1@gmailcom', 'Rol': 'administrador'}
}

@app.route('/', methods=['GET'])
def index():


    conP = sql_connection()
    curP = conP.cursor()
    statementP = 'SELECT * FROM Peliculas' 
    curP.execute(statementP)
    dataP = curP.fetchall()

    return render_template('index.html', page='inicio',  pelis = dataP)

@app.route('/login', methods=['GET','POST'])
def login():
    form = login_form()
    if form.validate_on_submit():

        con = sql_connection()
        cur = con.cursor()
        statement = 'SELECT * FROM Usuarios WHERE correo = ?' 
        cur.execute(statement, [form.username.data])
        data = cur.fetchall()
        
        try:
            idusuario = data[0][0]
            nombre = data[0][1]
            passw = data [0][2]
            rol = data[0][5]

            if passw == form.password.data:
                if rol == 'Usuario':
                    return redirect('perfilUsuario/'+str(idusuario))
                if rol == 'Admin':
                    return redirect('dashboard')
        
        except:

            pass
            
    return render_template('login.html', form=form, recaptcha=recaptcha, page='login')
        
    

    
    

@app.route('/registrar', methods=['GET','POST'])
def registrar():
    register = register_form()
    if register.validate_on_submit():
                
        con = sql_connection()
        cur = con.cursor()
        statement = 'INSERT INTO Usuarios (nombre_usuario, contraseña, correo, status, rol) VALUES (?,?,?,?,?)' 
        cur.execute(statement, [register.Nusername.data, register.Npassword.data, register.Nemail.data, '1', 'Usuario'])
        con.commit()

        return redirect ('login')
    else:
        return render_template('registrar.html', page='registrar', form = register)





@app.route('/dashboard/', methods=['GET','POST'])
def dashboard():

    
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

    return render_template('dashboard.html', page='dashboard', user = dataU, pelis = dataP)

@app.route('/detalleDeLaFuncion/<id>', methods=['GET','POST'])
def detalle_de_funcion(id):
    id_peli = int(id)
    if id_peli in peliculas:
        return render_template('detalleDeLaFuncion.html', page='detalleFuncion', pos = peliculas[id_peli])
    else:
        return "la noticia que esta buscando no existe"
    
@app.route('/detalleDePelicula/<id>', methods=['GET'])
def detalle_pelicula(id):

    conP = sql_connection()
    curP = conP.cursor()
    statementP = 'SELECT * FROM Peliculas WHERE id_pelicula = ?' 
    curP.execute(statementP, [id])
    dataP = curP.fetchall()

    try:
        return render_template('detalleDePelicula.html', page='detallePelicula', pelis = dataP[0])

    except:
        return redirect ('index')
    

@app.route('/perfilUsuario/<nom_usuario>', methods=['GET'])
def perfil_usuario(nom_usuario):
    return render_template('perfilUsuario.html', page='perfilUsuario', name = nom_usuario)


@app.route('/perfilUsuario/', methods=['GET'])
def perfil_user():
    return render_template('perfilUsuario.html', page='perfilUsuario', name = "invitado")


@app.route('/peliculas/', methods=['GET'])
def todas_peliculas():

    conP = sql_connection()
    curP = conP.cursor()
    statementP = 'SELECT * FROM Peliculas' 
    curP.execute(statementP)
    dataP = curP.fetchall()

    #COnsulta de la tabla comentarios para calcular el promedio por pelicula


    return render_template('todasPeliculas.html', page='peliculas', pelis = dataP)



@app.route('/agregarPelicula/', methods=['POST','GET'])
def agregar_peliculas():

    addPelis = add_pelicula()

    if addPelis.validate_on_submit():

        con = sql_connection()
        cur = con.cursor()
        statement = 'INSERT INTO Peliculas (nombre, sinopsis, cartelera, imagen) VALUES (?,?,?,?)' 
        cur.execute(statement, [addPelis.nombre.data, addPelis.sinopsis.data, addPelis.cartelera.data, addPelis.image.data])
        con.commit()

        print("Se ingreso la película")
        return redirect('/dashboard')
    else: 
        return render_template('agregarPelicula.html', form = addPelis)


@app.route('/dashboard/eliminar/<id_pelicula>')
def eliminar_pelicula(id_pelicula):

    #Statement en SQL eliminando el registro de la tabla películas el id = id_pelicula

    pass
    return render_template('dashboard.html', page='dashboard', user = usuarios, pelis = peliculas)


if __name__ == '__main__':
    app.run(debug=True)

