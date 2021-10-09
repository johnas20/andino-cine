from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = 'mysecretkey'

@app.route('/')
def index():
    return render_template('index.html', page='inicio')

@app.route('/login')
def login():
    return render_template('login.html', page='login')

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