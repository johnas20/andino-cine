from flask import Flask, render_template
from flask_wtf import FlaskForm, recaptcha
from flask_wtf.recaptcha.fields import RecaptchaField
from wtforms import StringField, PasswordField

app = Flask(__name__)
app.config['SECRET_KEY'] = 'claveoculta'
app.config['RECAPTCHA_PUBLIC_KEY'] = '6Lf-rKwcAAAAAIQKSPI2becEW2WRLZcUt80kp4z5'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6Lf-rKwcAAAAAIkQKHWtgSNhqNkEb2nmW7XkTZIC'

class login_form(FlaskForm):
    username = StringField('username')
    password = PasswordField("password")
    recaptcha = RecaptchaField()

@app.route('/')
def index():
    return render_template('index.html', page='inicio')

@app.route('/login', methods=['GET','POST'])
def login():
    form = login_form()
    return render_template('login.html', form=form, recaptcha=recaptcha, page='login')

@app.route('/registrar')
def registrar():
    return render_template('registrar.html', page='registrar')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', page='dashboard')

@app.route('/detalleDeFuncion/')
def detalle_de_funcion():
    return render_template('detalleDeLaFuncion.html', page='detaleFuncion')

@app.route('/perfilUsuario/')
def perfil_usuario():
    return render_template('perfilUsuario.html', page='perfilUsuario')

@app.route('/peliculas/')
def todas_peliculas():
    return render_template('todasPeliculas.html', page='peliculas')

if __name__ == '__main__':
    app.run(debug=True)