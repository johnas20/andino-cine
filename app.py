from os import execl
from sqlite3.dbapi2 import TimestampFromTicks
from flask import Flask, render_template, request, redirect, make_response, session, flash, url_for
from flask.scaffold import _matching_loader_thinks_module_is_package
from flask_wtf import FlaskForm, form, recaptcha
from flask_wtf.recaptcha.fields import RecaptchaField
from wtforms import StringField, PasswordField, SelectField, TextAreaField
from wtforms import validators
from wtforms.fields.core import BooleanField, DateField, DateTimeField, IntegerField
from wtforms.validators import InputRequired, DataRequired, Length, AnyOf;
from werkzeug.security import check_password_hash, generate_password_hash

import sqlite3

from wtforms.widgets.core import Input

app = Flask(__name__)
app.config['SECRET_KEY'] = 'claveoculta'
app.config['RECAPTCHA_PUBLIC_KEY'] = '6Lf-rKwcAAAAAIQKSPI2becEW2WRLZcUt80kp4z5'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6Lf-rKwcAAAAAIkQKHWtgSNhqNkEb2nmW7XkTZIC'


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
    tickettarde = IntegerField('Cantidad de tickets horario de la Tarde', validators=[InputRequired(message='Indique un valor')])
    ticketnoche = IntegerField('Cantidad de tickets horario de la Noche', validators=[InputRequired(message='Indique un valor')])

class add_comentario(FlaskForm):
    comentario = TextAreaField('Comentario', validators=[InputRequired(message='Escriba un comentario')])
    rating = SelectField('Calificación', choices=[(1,'1'), (2,'2'),(3,'3'), (4,'4'), (5,'5')])

class add_ticket(FlaskForm):
    horario = SelectField('Seleccione el Horario ', choices=[('Tarde', 'Tarde'), ('Noche','Noche')], validators=[InputRequired(message='Seleccione el Horario')])
    cantidad_ticket = IntegerField('Cantidad Boletas', validators=[InputRequired(message='Indique una cantidad')])


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
            
            if (check_password_hash((data[0][2]),form.password.data)):
            #if data[0][2] == form.password.data: 
            # Se comenta lina de código que NO busca la password encriptada
                
                
                if data[0][5] == 'Usuario':

                    session['user_tipo'] = data[0][5]
                    session['user_id'] = data[0][0]

                    flash('Bienvenido de vuelta '+ data[0][1] + '!')

                    return redirect('../perfilUsuario/'+str(data[0][0]))

                if data[0][5] == 'Admin':

                    session['user_tipo'] = data[0][5]
                    session['user_id'] = data[0][0]

                    flash('Bienvenido de vuelta '+ data[0][1] + '!')
                    
                    return redirect(url_for('dashboard'))

                if data[0][5] == 'Superadmin':

                    session['user_tipo'] = data[0][5]
                    session['user_id'] = data[0][0]

                    flash('¿Qué vamos a destruir hoy :) ?  '+ data[0][1] + '!')   

                    return redirect(url_for('dashboard'))

            else:

                flash('Ups, Contraseña Incorrecta. Intenta de nuevo!')

                return render_template('login.html', form=form, recaptcha=recaptcha, page='login', user_tipo=user_tipo, user_id=user_id)

        except:

            flash('Ups, Usuario no encontrado. Intenta de nuevo!')

            return render_template('login.html', form=form, recaptcha=recaptcha, page='login', user_tipo=user_tipo, user_id=user_id)

    else:
        if user_tipo=='Admin' or user_tipo=='Superadmin':
            return redirect(url_for('dashboard'))
        
        elif user_tipo=='Usuario':
            return redirect('../perfilUsuario/'+str(user_id))

        else:
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

        #Consulta buscando el usuario en la BD para verificar si se puede crear el usuario
        #Consulta de USUARIOS

        conU = sql_connection()
        curU = conU.cursor()
        statementU = 'SELECT * FROM Usuarios WHERE correo = ?' 
        curU.execute(statementU, [register.Nemail.data])
        dataU = curU.fetchall()

        try:
            if dataU[0][3]==register.Nemail.data:
                flash('¡Ya hay un usuario registrado con este E-Mail!')
                return render_template('registrar.html', page='registrar', form = register, user_tipo=user_tipo, user_id=user_id)

        except: 
            register.Npassword.data=generate_password_hash(register.Npassword.data)  #Se encripta la password
            con = sql_connection()
            cur = con.cursor()
            statement = 'INSERT INTO Usuarios (nombre_usuario, contraseña, correo, status, rol) VALUES (?,?,?,?,?)' 
            cur.execute(statement, [register.Nusername.data, register.Npassword.data, register.Nemail.data, '1', 'Usuario'])
            con.commit()

            flash('Bienvenido a la familia ANDINO. Ahora puedes Iniciar Sesión')     
            return redirect (url_for('login'))
    
    else:

        if user_tipo=='Admin' or user_tipo=='Superadmin':
            return redirect(url_for('dashboard'))
        
        elif user_tipo == 'Usuario':
            return redirect('../perfilUsuario/'+str(user_id))

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

    if user_tipo=='Admin' or user_tipo=='Superadmin':
        return render_template('dashboard.html', page='dashboard', user = dataU, pelis = dataP, user_tipo=user_tipo, user_id=user_id)
    
    elif user_tipo=='Usuario':
        return redirect('../perfilUsuario/'+str(user_id))

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


    #Consulta de Pelicula
    conP = sql_connection()
    curP = conP.cursor()
    statementP = 'SELECT * FROM Peliculas WHERE id_pelicula = ?' 
    curP.execute(statementP, [id])
    dataP = curP.fetchall()

    #Consulta de Tickets Tarde
    conT = sql_connection()
    curT = conT.cursor()
    statementT = 'SELECT SUM(cantidad_ticket) as cantidad_ticket FROM Tickets WHERE id_pelicula = ? AND Horario = ?' 
    curT.execute(statementT, [id, 'Tarde'])
    dataT = curT.fetchall()

    try:
        tarde = int(dataT[0][0])
        disp_tarde = dataP[0][5] - tarde
    except:
        tarde = 0
        disp_tarde =  dataP[0][5] 


    #Consulta de Tickets Tarde
    conT2 = sql_connection()
    curT2 = conT2.cursor()
    statementT2 = 'SELECT SUM(cantidad_ticket) as cantidad_ticket FROM Tickets WHERE id_pelicula = ? AND Horario = ?' 
    curT2.execute(statementT2, [id, 'Noche'])
    dataT2 = curT2.fetchall()

    try: 
        noche = int(dataT2[0][0])
        disp_noche = dataP[0][5] - noche
    except:
        noche = 0
        disp_noche = dataP[0][5]

    Context= {

        'tarde' : tarde,
        'disp_tarde' : disp_tarde,
        'noche': noche,
        'disp_noche': disp_noche,

    }

    form = add_ticket()
    if form.validate_on_submit():

        if form.horario.data == 'Tarde':
            if int(form.cantidad_ticket.data) <= disp_tarde:
                bool = True
            else: bool = False
        if form.horario.data == 'Noche':
            if int(form.cantidad_ticket.data) <= disp_noche:
                bool = True
            else: bool = False

        if bool == True:

            #Consulta para ingresar el ticket
            conT = sql_connection()
            curT = conT.cursor()
            statementT = 'INSERT INTO Tickets (id_pelicula, id_usuario, cantidad_ticket, Horario) VALUES (?,?,?,?)' 
            curT.execute(statementT, [id, user_id, form.cantidad_ticket.data, form.horario.data])
            conT.commit()

            flash('Ticket comprado exitosamente!')     

            return redirect ('../detalleDePelicula/'+str(id))
        if bool == False:

            flash('Cantidad no disponible!') 
            return redirect ('../detalleDeLaFuncion/'+str(id))



    else:
        if user_tipo != "Invitado":
            try:
                return render_template('detalleDeLaFuncion.html', page='detalleFuncion', form=form,  pelis = dataP[0], user_tipo=user_tipo, user_id=user_id, **Context)

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
    statementC = 'SELECT * FROM vw_ComentariosxUsuarios WHERE id_pelicula = ?' 
    curC.execute(statementC, [id])
    dataC = curC.fetchall()

    #Consulta Tickets

    conT = sql_connection()
    curT = conT.cursor()
    statementT = 'SELECT * FROM vw_TicketsxUsuarios WHERE id_pelicula = ?' 
    curT.execute(statementT,[id])
    dataT = curT.fetchall()


    try:
        return render_template('detalleDePelicula.html', page='detallePelicula', pelis = dataP[0], com = dataC, tickets=dataT, user_tipo=user_tipo, user_id=user_id)

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


    #Consulta de USUARIOS

    conU = sql_connection()
    curU = conU.cursor()
    statementU = 'SELECT * FROM Usuarios WHERE id_usuario = ?' 
    curU.execute(statementU,[nom_usuario])
    dataU = curU.fetchall()

    #Consulta de TICKETS

    conT = sql_connection()
    curT = conT.cursor()
    statementT = 'SELECT * FROM vw_TicketsxPelicula WHERE id_usuario = ?' 
    curT.execute(statementT,[nom_usuario])
    dataT = curT.fetchall()

    #Consulta de Comentarios

    conC = sql_connection()
    curC = conC.cursor()
    statementC = 'SELECT * FROM vw_ComentariosxPelicula WHERE id_usuario = ?' 
    curC.execute(statementC, [nom_usuario])
    dataC = curC.fetchall()

    if user_tipo == "Usuario":
        if str(nom_usuario) == str(user_id):
            return render_template('perfilUsuario.html', page='perfilUsuario', name = dataU[0], tickets=dataT, com=dataC, user_tipo=user_tipo, user_id=user_id)
        else:
            return redirect('../perfilUsuario/'+str(user_id))

    elif user_tipo=='Admin' or user_tipo=='Superadmin':
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

    if user_tipo=='Admin' or user_tipo=='Superadmin':

        addPelis = add_pelicula()

        if addPelis.validate_on_submit():

            con = sql_connection()
            cur = con.cursor()
            statement = 'INSERT INTO Peliculas (nombre, sinopsis, cartelera, imagen, tarde, noche) VALUES (?,?,?,?,?,?)' 
            cur.execute(statement,
                [addPelis.nombre.data, addPelis.sinopsis.data, addPelis.cartelera.data, addPelis.image.data,
                 addPelis.tickettarde.data, addPelis.ticketnoche.data])
            con.commit()

            flash('Película agregada correctamente!')     

            
            return redirect('/dashboard')
        else: 
            return render_template('agregarPelicula.html', form = addPelis, user_tipo=user_tipo, user_id=user_id)
    
    elif user_tipo== 'Usuario':
        return redirect('../perfilUsuario/'+str(user_id))
    
    else:
        return redirect(url_for('login'))


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
            curA.execute(statementA, [user_id, id,addCom.comentario.data, addCom.rating.data])
            conA.commit()

            flash('Comentario agregado correctamente!')     

            return redirect('../detalleDePelicula/'+str(id))
        
        else:
            
            try:
                return render_template('agregarComentario.html', form=addCom,page='agregarComentario', pelis = dataP[0], user_tipo=user_tipo, user_id=user_id)

            except:
                return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))



@app.route('/eliminarPelicula/<id_pelicula>')
def eliminarPelicula(id_pelicula):

    try:
        user_tipo = session['user_tipo']
        user_id = session['user_id']
    except:
        user_tipo = "Invitado"
        user_id = 0


    if user_tipo=='Admin' or user_tipo=='Superadmin':

        #Consulta Peliculas
        try:
            conP = sql_connection()
            curP = conP.cursor()
            statementP = 'DELETE FROM Peliculas WHERE id_pelicula = ?' 
            curP.execute(statementP, [id_pelicula])
            conP.commit()

            flash('Pelicula eliminada correctamente!')  

            return redirect(url_for('dashboard'))

               

        except:

            return redirect(url_for('index'))

    else:
        return redirect(url_for('login'))


@app.route('/eliminarUsuario/<id_usuario>')
def eliminarUsuario(id_usuario):

    try:
        user_tipo = session['user_tipo']
        user_id = session['user_id']
    except:
        user_tipo = "Invitado"
        user_id = 0


    if user_tipo=='Admin' or user_tipo=='Superadmin':

        #Consulta Usuarios
        try:
            conU = sql_connection()
            curU = conU.cursor()
            statementU = 'DELETE FROM Usuarios WHERE id_usuario = ?' 
            curU.execute(statementU, [id_usuario])
            conU.commit()

            flash('Usuario eliminado correctamente!')  

            return redirect(url_for('dashboard'))

        except:

            return redirect(url_for('index'))

    else:
        return redirect(url_for('login'))


@app.route('/eliminarComentario/<id_comentario>')
def eliminarComentario(id_comentario):

    try:
        user_tipo = session['user_tipo']
        user_id = session['user_id']
    except:
        user_tipo = "Invitado"
        user_id = 0


    if user_tipo=='Admin' or user_tipo=='Superadmin':

        
        try:

            #Consulta ID Pelicula antes de borrar el comentario
            conP = sql_connection()
            curP = conP.cursor()
            statementP = 'SELECT * FROM Comentarios WHERE id_comentario = ?' 
            curP.execute(statementP, [id_comentario])
            dataP = curP.fetchall()

            #Consulta Comentario
            conC = sql_connection()
            curC = conC.cursor()
            statementC = 'DELETE FROM Comentarios WHERE id_comentario = ?' 
            curC.execute(statementC, [id_comentario])
            conC.commit()

            flash('Comentario eliminado correctamente!')  

            return redirect('../detalleDePelicula/'+str(dataP[0][2]))

        except:

            return redirect(url_for('index'))

    elif user_tipo == 'Usuario':

        #Consulta Comentarios
        conC = sql_connection()
        curC = conC.cursor()
        statementC = 'SELECT * FROM Comentarios WHERE id_comentario = ?' 
        curC.execute(statementC, [id_comentario])
        dataC = curC.fetchall()

        try:
            if dataC[0][1] == user_id:

                #Consulta de DELETE
                conC = sql_connection()
                curC = conC.cursor()
                statementC = 'DELETE FROM Comentarios WHERE id_comentario = ?' 
                curC.execute(statementC, [id_comentario])
                conC.commit()
                flash('Comentario eliminado correctamente!')  

                return redirect('../perfilUsuario/'+str(user_id))


            else:
                return redirect('../perfilUsuario/'+str(user_id))
        
        except:

            return redirect(url_for('index'))

    else:
        return redirect(url_for('login'))


@app.route('/eliminarTicket/<id_ticket>')
def eliminarTicket(id_ticket):

    try:
        user_tipo = session['user_tipo']
        user_id = session['user_id']
    except:
        user_tipo = "Invitado"
        user_id = 0


    if user_tipo=='Admin' or user_tipo=='Superadmin':

       
        try:

            #Consulta ID Pelicula antes de borrar el comentario
            conP = sql_connection()
            curP = conP.cursor()
            statementP = 'SELECT * FROM Tickets WHERE id_ticket = ?' 
            curP.execute(statementP, [id_ticket])
            dataP = curP.fetchall()

            #Consulta Tickets
            conT = sql_connection()
            curT = conT.cursor()
            statementT = 'DELETE FROM Tickets WHERE id_ticket = ?' 
            curT.execute(statementT, [id_ticket])
            conT.commit()

            flash('Ticket eliminado correctamente!')  

            return redirect('../detalleDePelicula/'+str(dataP[0][1]))

        except:

            return redirect(url_for('index'))

    else:
        return redirect(url_for('login'))
        

@app.route("/modificarUsuario/<id_usuario>/<rol_usuario>", methods=['GET', 'POST'])
def modificarUsuario(id_usuario, rol_usuario):

    try:
        user_tipo = session['user_tipo']
        user_id = session['user_id']
    except:
        user_tipo = "Invitado"
        user_id = 0


    if user_tipo=='Superadmin':

        #Consulta Usuarios

        #Consulta de USUARIOS

        try:
            conU = sql_connection()
            curU = conU.cursor()
            statementU = 'UPDATE Usuarios SET rol = ? WHERE id_usuario = ?' 
            curU.execute(statementU, [rol_usuario,id_usuario])
            conU.commit()

            flash("Cambiado Correctamente!")
            return redirect(url_for('dashboard'))
        
        except:
            flash("Incorrecto")
            return redirect(url_for('dashboard'))


    else:
        if user_tipo=='Usuario':
            return redirect (url_for('perfil_Usuario'))
        
        elif user_tipo =='Admin':
            return redirect(url_for('dashboard'))
        
        elif user_tipo == 'Invitado':
            return redirect(url_for('Login'))    


@app.route("/modificarCartelera/<id_pelicula>/<int:cartelera>", methods=['GET', 'POST'])
def modificarCartelera(id_pelicula, cartelera):

    try:
        user_tipo = session['user_tipo']
        user_id = session['user_id']
    except:
        user_tipo = "Invitado"
        user_id = 0


    if user_tipo=='Admin' or user_tipo == 'Superadmin':

        #Consulta de PELICULAS

        try:
            conP = sql_connection()
            curP = conP.cursor()
            statementP = 'UPDATE Peliculas SET cartelera = ? WHERE id_pelicula = ?' 
            curP.execute(statementP, [cartelera,id_pelicula])
            conP.commit()

            flash("Cambiado Correctamente!")
            return redirect(url_for('dashboard'))
        
        except:
            flash("Incorrecto")
            return redirect(url_for('dashboard'))


    else:
        if user_tipo=='Usuario':
            return redirect (url_for('perfil_Usuario'))
        
        elif user_tipo == 'Invitado':
            return redirect(url_for('Login'))    


@app.route("/logout", methods=['GET','POST'])
def logout():
    session.clear()
    session['user_tipo'] = "Invitado"
    session['user_id'] = 0

    flash('Vuelve pronto!')  

    return redirect(url_for('index'))

    


if __name__ == '__main__':
    app.run(debug=True)
