from flask import Flask, render_template, request, redirect
from flask_wtf import FlaskForm, recaptcha
from flask_wtf.recaptcha.fields import RecaptchaField
from wtforms import StringField, PasswordField, SelectField, TextAreaField
from wtforms import validators
from wtforms.fields.core import BooleanField
from wtforms.validators import InputRequired, DataRequired, Length, AnyOf;
from flask.helpers import url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = 'claveoculta'
app.config['RECAPTCHA_PUBLIC_KEY'] = '6Lf-rKwcAAAAAIQKSPI2becEW2WRLZcUt80kp4z5'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6Lf-rKwcAAAAAIkQKHWtgSNhqNkEb2nmW7XkTZIC'

from peliculas import peliculas

class login_form(FlaskForm):
    username = StringField('Usuario o correo', validators=[InputRequired(message='El usuario es requerido'),Length(min=5,max=10, message='El usuario debe tener entre 5 y 10 caracteres')])
    password = PasswordField("Contraseña", validators=[InputRequired(message='Contraseña es requerida'), AnyOf(values=['admin','12345'])])
    recaptcha = RecaptchaField()

class register_form(FlaskForm):
    Nusername = StringField('Nombre', validators=[InputRequired(message='El mombre es requerido'),Length(min=5,max=10, message='El nombre debe tener entre 5 y 10 caracteres')])
    Nlast = StringField('Apellido')
    Nemail = StringField('Nombre', validators=[InputRequired(message='El correo es requerido')])
    Nphone = StringField('Teléfono', validators=[InputRequired(message='El teléfono es requerido')])
    Npassword = PasswordField("Contraseña", validators=[InputRequired(message='La contraseña es requerida')])
    NRpassword = PasswordField("Repite la contraseña", validators=[InputRequired(message='La contraseña es requerida')])

class add_pelicula(FlaskForm):
    nombre = StringField('nombre de la pelicula')
    categoria = StringField('categoria')
    valor = StringField('Calificación (de 1 a 5) estrellas')
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
    return render_template('index.html', page='inicio',  peliculas = peliculas)

@app.route('/login', methods=['GET','POST'])
def login():
    form = login_form()
    if form.validate_on_submit():
        print("Usuario: {} Contraseña: {}".format(form.username.data,form.password.data))
    return render_template('login.html', form=form, recaptcha=recaptcha, page='login')
    

@app.route('/registrar', methods=['GET','POST'])
def registrar():
    register = register_form()
    return render_template('registrar.html', page='registrar', form = register)

@app.route('/dashboard/', methods=['GET','POST'])
def dashboard():
    return render_template('dashboard.html', page='dashboard', user = usuarios, pelis = peliculas)

@app.route('/detalleDeLaFuncion/<id>', methods=['GET','POST'])
def detalle_de_funcion(id):
    id_peli = int(id)
    if id_peli in peliculas:
        return render_template('detalleDeLaFuncion.html', page='detalleFuncion', pos = peliculas[id_peli])
    else:
        return "la noticia que esta buscando no existe"
    
@app.route('/detalleDePelicula/<id>', methods=['GET'])
def detalle_pelicula(id):
    id_peli = int(id)
    if id_peli in peliculas:
        return render_template('detalleDePelicula.html', page='detallePelicula', pos = peliculas[id_peli], ident = id_peli)
    else:
        return "la noticia que esta buscando no existe"
    

@app.route('/perfilUsuario/<nom_usuario>', methods=['GET'])
def perfil_usuario(nom_usuario):
    return render_template('perfilUsuario.html', page='perfilUsuario', name = nom_usuario)

@app.route('/perfilUsuario/', methods=['GET'])
def perfil_user():
    return render_template('perfilUsuario.html', page='perfilUsuario', name = "invitado")

@app.route('/peliculas/', methods=['GET'])
def todas_peliculas():
    return render_template('todasPeliculas.html', page='peliculas', peliculas = peliculas)

@app.route('/agregarPelicula/', methods=['POST','GET'])
def agregar_peliculas():
    addPelis = add_pelicula()
    if addPelis.validate_on_submit():
        cod = len(peliculas)
        peliculas[cod] = {'nombre': addPelis.nombre.data, 'categoria':addPelis.categoria.data, 'calificacion':int(addPelis.valor.data),'sinopsis':addPelis.sinopsis.data,'cartelera':bool(addPelis.cartelera.data),'image':addPelis.image.data}
        print(peliculas)
        return redirect('/dashboard')
    return render_template('agregarPelicula.html', form = addPelis)

if __name__ == '__main__':
    app.run(debug=True)

