from flask import Flask, render_template, request, redirect, url_for, session, flash
import db, funcionalidades
import util
from util import form_to_dict


app = Flask(__name__)
app.secret_key = 'fonasa_test'


@app.route('/')
@app.route('/index/')
def index():
    return render_template('index.html')


# Listar hospitales, consultas y pacientes
@app.route('/hospital/')
def hospital_list():
    # Crea las listas de pacientes
    session.permanent = False
    if 'lista_espera' not in session:
        session['lista_espera'] = {}
        flash('Lista de espera creada!', 'info')
    if 'lista_pendiente' not in session:
        session['lista_pendiente'] = {}
        flash('Lista de pendientes creada!', 'info')
    if 'lista_atencion' not in session:
        session['lista_atencion'] = {}
        flash('Lista de atención creada!', 'info')
    mydb = db.get_db()
    hospitales = db.get_hospitales(mydb)
    return render_template('hospital_list.html', title='Hospitales', hospitales=hospitales, count=len(hospitales))


@app.route('/hospital/<id_hospital>/')
def consulta_list(id_hospital):
    # Verifica que existen las listas de pacientes
    if 'lista_espera' not in session:
        return redirect(url_for('index'))
    if 'lista_pendiente' not in session:
        return redirect(url_for('index'))
    if 'lista_atencion' not in session:
        return redirect(url_for('index'))
    # Crea las listas de pacientes para cada Hospital accedido
    if str(id_hospital) not in session['lista_espera']:
        session['lista_espera'][id_hospital] = []
        flash('Lista de espera para hospital creada!', 'info')
    if str(id_hospital) not in session['lista_pendiente']:
        session['lista_pendiente'][id_hospital] = []
        flash('Lista de pendientes para hospital creada!', 'info')
    if str(id_hospital) not in session['lista_atencion']:
        session['lista_atencion'][id_hospital] = []
        flash('Lista de atención para hospital creada!', 'info')
    # Recupera la información necesaria desde la base de datos para mostrar en front-end
    mydb = db.get_db()
    nombre_hospital = db.get_nombre_hospital(mydb, id_hospital)
    consultas = db.get_consultas(mydb, id_hospital)
    consulta_mas_pacientes = funcionalidades.consulta_mas_pacientes_atendidos(mydb, id_hospital)
    return render_template('consulta_list.html', title='Consultas ', idHospital=id_hospital,
                           nombre_hospital=nombre_hospital, consultas=consultas,
                           consulta_mas_pacientes=consulta_mas_pacientes)


@app.route('/hospital/<id_hospital>/pacientes/')
def paciente_list(id_hospital):
    # Verifica que existen las listas de pacientes
    if 'lista_espera' not in session:
        return redirect(url_for('index'))
    if 'lista_pendiente' not in session:
        return redirect(url_for('index'))
    if 'lista_atencion' not in session:
        return redirect(url_for('index'))
    # Recupera la información necesaria desde la base de datos para mostrar en front-end
    mydb = db.get_db()
    nombre_hospital = db.get_nombre_hospital(mydb, id_hospital)
    pacientes = db.get_pacientes(mydb, id_hospital)
    count = len(pacientes)
    ancianos = funcionalidades.paciente_mas_anciano(session['lista_espera'][id_hospital])
    return render_template('paciente_list.html', title='Lista Pacientes', pacientes=pacientes,
                           count=count, idHospital=id_hospital, nombre_hospital=nombre_hospital, ancianos=ancianos)


# Agregar hospitales, consultas y pacientes
@app.route('/hospital/nuevo/', methods=['POST', 'GET'])
def hospital_add():
    # Verifica que existen las listas de pacientes
    if 'lista_espera' not in session:
        return redirect(url_for('index'))
    if 'lista_pendiente' not in session:
        return redirect(url_for('index'))
    if 'lista_atencion' not in session:
        return redirect(url_for('index'))
    if request.method == 'GET':
        return redirect(url_for('hospital_list'))
    if request.method == 'POST':
        mydb = db.get_db()
        estado, id_hospital = db.insert_hospital(mydb, request.form)
        if estado:
            flash('Hospital agregado!', 'info')
        else:
            flash('Hospital ya existe!', 'info')
        return redirect(url_for('hospital_list'))


@app.route('/hospital/<id_hospital>/nuevoConsulta/', methods=['POST', 'GET'])
def consulta_add(id_hospital):
    # Verifica que existen las listas de pacientes
    if 'lista_espera' not in session:
        return redirect(url_for('index'))
    if 'lista_pendiente' not in session:
        return redirect(url_for('index'))
    if 'lista_atencion' not in session:
        return redirect(url_for('index'))
    if request.method == 'GET':
        return redirect(url_for('consulta_list', id_hospital=id_hospital))
    if request.method == 'POST':
        mydb = db.get_db()
        estado, id_consulta = db.insert_consulta(mydb, id_hospital, request.form)
        if estado:
            flash('Consulta agregada!', 'info')
        else:
            flash('Consulta ya existe!', 'info')
        return redirect(url_for('consulta_list', id_hospital=id_hospital))


@app.route('/hospital/<id_hospital>/nuevoPaciente/', methods=['POST', 'GET'])
def pacienteNuevo(id_hospital):
    # Verifica que existen las listas de pacientes
    if 'lista_espera' not in session:
        return redirect(url_for('index'))
    if 'lista_pendiente' not in session:
        return redirect(url_for('index'))
    if 'lista_atencion' not in session:
        return redirect(url_for('index'))
    if request.method == 'GET':
        return redirect(url_for('paciente_list', id_hospital=id_hospital))
    if request.method == 'POST':
        mydb = db.get_db()
        estado, id_paciente = db.insert_paciente(mydb, id_hospital, request.form)
        if estado:
            flash('Paciente agregado a la base de datos!', 'info')
        else:
            flash('Paciente ya existe en la base de datos!', 'info')
        if 'ingresarPendiente' in request.form and estado:
            flash('Paciente ingresado a la lista de pendientes', 'info')
            paciente = db.get_paciente(mydb, id_paciente)
            session['lista_pendiente'][id_hospital].append(paciente)
            session['lista_pendiente'][id_hospital] = util.ordenar_lista(session['lista_pendiente'][id_hospital])
            print(session['lista_pendiente'][id_hospital])
        return redirect(url_for('paciente_list', id_hospital=id_hospital))


# Funcionalidades
@app.route('/hospital/<id_hospital>/pacientes/masriesgo', methods=['POST', 'GET'])
def mayor_riesgo(id_hospital):
    # Verifica que existen las listas de pacientes
    if 'lista_espera' not in session:
        return redirect(url_for('index'))
    if 'lista_pendiente' not in session:
        return redirect(url_for('index'))
    if 'lista_atencion' not in session:
        return redirect(url_for('index'))
    if request.method == 'GET':
        return redirect(url_for('paciente_list', id_hospital=id_hospital))
    if request.method == 'POST':
        mydb = db.get_db()
        id_paciente = form_to_dict(request.form)['id_paciente']
        pacientes_mayor_riesgo = funcionalidades.listar_pacientes_mayor_riesgo(mydb, id_hospital, id_paciente)
        count = len(pacientes_mayor_riesgo)
        caso = 'N° de pacientes con mayor riesgo'
        return render_template('pacientes_especifico.html',
                               title='Pacientes riesgosos que:', count=count, pacientes=pacientes_mayor_riesgo,
                               idHospital=id_hospital, caso=caso)


@app.route('/hospital/<id_hospital>/action')
def accion_lista(id_hospital):
    # Verifica que existen las listas de pacientes
    if 'lista_espera' not in session:
        return redirect(url_for('index'))
    if 'lista_pendiente' not in session:
        return redirect(url_for('index'))
    if 'lista_atencion' not in session:
        return redirect(url_for('index'))
    # Si no se detecta una acción, se redirige a la lista de consultas
    if 'do' not in request.args:
        flash('Acción Inválida!', 'info')
        return redirect(url_for('consulta_list', id_hospital=id_hospital))
    mydb = db.get_db()
    consultas = db.get_consultas(mydb, id_hospital)
    # Funcionalidad de Atender a los Pacientes
    if request.args['do'] == 'atender':
        session['lista_espera'][id_hospital], session['lista_pendiente'][id_hospital], session['lista_atencion'][id_hospital] = funcionalidades.atender_paciente(
            consultas,
            session['lista_espera'][id_hospital],
            session['lista_pendiente'][id_hospital],
            session['lista_atencion'][id_hospital])
        flash('Pacientes Atendidos!', 'info')
    # Funcionalidad de Liberar Consultas
    elif request.args['do'] == 'liberar':
        session['lista_espera'][id_hospital], session['lista_pendiente'][id_hospital], session['lista_atencion'][id_hospital] = funcionalidades.liberar_consultas(
            consultas,
            session['lista_espera'][id_hospital],
            session['lista_pendiente'][id_hospital],
            session['lista_atencion'][id_hospital])
        flash('Consultas Liberadas!', 'info')
    # Funcionalidad de Optimizar Atención
    elif request.args['do'] == 'optimizar':
        session['lista_espera'][id_hospital], session['lista_pendiente'][id_hospital], session['lista_atencion'][id_hospital] = funcionalidades.optimizar_atencion(
            consultas,
            session['lista_espera'][id_hospital],
            session['lista_pendiente'][id_hospital],
            session['lista_atencion'][id_hospital])
        flash('Atención Optimizada!', 'info')
    # Si no se detecta una acción válida, solo se redirige a la lista de consultas
    else:
        flash('Acción Inválida!', 'info')
    return redirect(url_for('consulta_list', id_hospital=id_hospital))


@app.route('/hospital/<id_hospital>/pacientes/fumadores')
def fumadores_urgentes(id_hospital):
    # Verifica que existen las listas de pacientes
    if 'lista_espera' not in session:
        return redirect(url_for('index'))
    if 'lista_pendiente' not in session:
        return redirect(url_for('index'))
    if 'lista_atencion' not in session:
        return redirect(url_for('index'))
    # Recupera la información necesaria desde la base de datos para mostrar en front-end
    mydb = db.get_db()
    pacientes = db.get_pacientes(mydb, id_hospital)
    pacientes_fumadores = funcionalidades.listar_pacientes_fumadores_urgentes(pacientes)
    count = len(pacientes_fumadores)
    caso = 'N° de pacientes fumadores riesgosos (prioridad mayor a 4)'
    return render_template('pacientes_especifico.html',
                           title='Pacientes Fumadores', count=count, pacientes=pacientes_fumadores,
                           idHospital=id_hospital, caso=caso)


@app.route('/hospital/<id_hospital>/pacientes/add_pendiente', methods=['POST', 'GET'])
def add_pendiente(id_hospital):
    # Verifica que existen las listas de pacientes
    if 'lista_espera' not in session:
        return redirect(url_for('index'))
    if 'lista_pendiente' not in session:
        return redirect(url_for('index'))
    if 'lista_atencion' not in session:
        return redirect(url_for('index'))
    if request.method == 'GET':
        return redirect(url_for('paciente_list'))
    if request.method == 'POST':
        id_paciente = form_to_dict(request.form)['id_paciente']
        mydb = db.get_db()
        paciente = db.get_paciente(mydb, id_paciente)
        session['lista_pendiente'][id_hospital].append(paciente)
        session['lista_pendiente'][id_hospital] = util.ordenar_lista(session['lista_pendiente'][id_hospital])
        flash('Paciente Agregado a la lista de pendientes!', 'info')
        return redirect(url_for('paciente_list', id_hospital=id_hospital))


if __name__ == '__main__':
    app.run()
