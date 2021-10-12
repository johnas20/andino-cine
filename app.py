from flask import Flask, render_template
from flask_wtf import FlaskForm, recaptcha
from flask_wtf.recaptcha.fields import RecaptchaField
from wtforms import StringField, PasswordField, SelectField
from wtforms import validators
from wtforms.validators import InputRequired, DataRequired, Length, AnyOf;

app = Flask(__name__)
app.config['SECRET_KEY'] = 'claveoculta'
app.config['RECAPTCHA_PUBLIC_KEY'] = '6Lf-rKwcAAAAAIQKSPI2becEW2WRLZcUt80kp4z5'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6Lf-rKwcAAAAAIkQKHWtgSNhqNkEb2nmW7XkTZIC'

peliculas = {
    1:{'nombre': 'Venon 2', 'calificacion':5,'sinopsis':'lorem ipsum its a dolor it...','reserva':True,'image':'caratula-venon.jpg'},
    2:{'nombre': 'Los avengers 2', 'calificacion':5,'sinopsis':'lorem ipsum its a dolor it...','reserva':True,'image':'caratula-1.png'},
    3:{'nombre': 'Los avengers 3', 'calificacion':5,'sinopsis':'lorem ipsum its a dolor it...','reserva':False,'image':'caratula-1.png'},
    4:{'nombre': 'Los avengers 4', 'calificacion':5,'sinopsis':'lorem ipsum its a dolor it...','reserva':False,'image':'caratula-1.png'},
    5:{'nombre': 'Los avengers 5', 'calificacion':5,'sinopsis':'lorem ipsum its a dolor it...','reserva':True,'image':'caratula-1.png'},
    6:{'nombre': 'Los avengers 6', 'calificacion':5,'sinopsis':'lorem ipsum its a dolor it...','reserva':True,'image':'caratula-1.png'}
}

class login_form(FlaskForm):
    username = StringField('username', validators=[InputRequired(message='El usuario es requerido'),Length(min=5,max=10, message='El usuario debe tener entre 5 y 10 caracteres')])
    password = PasswordField("password", validators=[InputRequired(message='Contraseña es requerida'), AnyOf(values=['admin','12345'])])
    recaptcha = RecaptchaField()


#Ejemplo de dos usuarios para los layouts de perfilUsuario y dashboard del admin
usuarios = {
    1:{'Id': 1, 'Nombre': 'usuario1', 'Correo': 'usuario1@gmailcom', 'Rol': 'usuario' },
    2:{'Id': 2, 'Nombre': 'admin1', 'Correo': 'admin1@gmailcom', 'Rol': 'administrador' }
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
    return render_template('registrar.html', page='registrar')

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    return render_template('dashboard.html', page='dashboard')

@app.route('/detalleDeFuncion/', methods=['GET','POST'])
def detalle_de_funcion():
    return render_template('detalleDeLaFuncion.html', page='detaleFuncion')

@app.route('/perfilUsuario/', methods=['GET','POST'])
def perfil_usuario():
    return render_template('perfilUsuario.html', page='perfilUsuario')

@app.route('/peliculas/', methods=['GET'])
def todas_peliculas():
    return render_template('todasPeliculas.html', page='peliculas')

if __name__ == '__main__':
    app.run(debug=True)

#Prueba

