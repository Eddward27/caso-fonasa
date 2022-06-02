from mysql.connector import connect
from util import form_to_dict, prioridad_paciente, riesgo_paciente


def get_db():
    mydb = connect(
        host="localhost",
        user="",
        password="",
        database="caso_fonasa"
    )
    return mydb


def get_hospitales(mydb):
    dbCursor = mydb.cursor()
    dbCursor.execute("SELECT * FROM hospital")
    result = dbCursor.fetchall()
    dictHospitales = []
    for hospital in result:
        dict_loop = {
            'id_hospital': hospital[0],
            'nombre_hospital': hospital[1]
        }
        dictHospitales.append(dict_loop)
    return dictHospitales


def get_nombre_hospital(mydb, id_hospital):
    dbCursor = mydb.cursor()
    dbCursor.execute("SELECT nombre_hospital FROM hospital WHERE id_hospital=" + str(id_hospital))
    nombreHospital = dbCursor.fetchall()[0][0]
    return nombreHospital


def get_consultas(mydb, id_hospital=-1):
    dbCursor = mydb.cursor()
    if id_hospital == -1:
        dbCursor.execute("SELECT * FROM consulta")
    else:
        dbCursor.execute("SELECT * FROM consulta WHERE id_hospital=" + str(id_hospital))
    result = dbCursor.fetchall()
    dictConsultas = []
    for consulta in result:
        dict_loop = {
            'id_consulta': consulta[0],
            'id_hospital': consulta[1],
            'cantPacientes': consulta[2],
            'nombreEspecialista': consulta[3],
            'tipoConsulta': consulta[4],
            'estado': consulta[5]
        }
        dictConsultas.append(dict_loop)
    return dictConsultas


def get_pacientes(mydb, id_hospital=-1):
    dbCursor = mydb.cursor()
    if id_hospital == -1:
        dbCursor.execute("SELECT * FROM pacientes")
    else:
        dbCursor.execute("SELECT * FROM pacientes WHERE id_hospital=" + str(id_hospital))
    result = dbCursor.fetchall()
    dictPacientes = []
    for paciente in result:
        dict_loop = {
            'id_paciente': paciente[0],
            'id_hospital': paciente[1],
            'nombre': paciente[2],
            'edad': paciente[3],
            'peso': paciente[4],
            'estatura': paciente[5]
        }
        if int(paciente[3]) <= 15:
            dbCursor.execute("SELECT rPesoEstatura FROM pninno WHERE id_paciente=" + str(paciente[0]))
            datos_extra = dbCursor.fetchall()[0]
            dict_loop['rPesoEstatura'] = datos_extra[0]
        elif int(paciente[3]) <= 40:
            dbCursor.execute("SELECT fumador, annosFumando FROM pjoven WHERE id_paciente=" + str(paciente[0]))
            datos_extra = dbCursor.fetchall()[0]
            dict_loop['fumador'] = datos_extra[0]
            dict_loop['annosFumando'] = datos_extra[1]
        else:
            dbCursor.execute("SELECT tieneDieta FROM panciano WHERE id_paciente=" + str(paciente[0]))
            datos_extra = dbCursor.fetchall()[0]
            dict_loop['tieneDieta'] = datos_extra[0]
        dict_loop['prioridad'] = prioridad_paciente(dict_loop)
        dict_loop['riesgo'] = riesgo_paciente(dict_loop['edad'], dict_loop['prioridad'])
        dictPacientes.append(dict_loop)
    return dictPacientes


def insert_hospital(mydb, hospital):
    hospital_dict = form_to_dict(hospital)
    dbCursor = mydb.cursor()
    # Verificar si el hospital ya existe [Mismo nombre hospital]
    dbCursor.execute("SELECT id_hospital FROM hospital WHERE nombre_hospital=\"" + hospital["nombre_hospital"] + "\";")
    hospitalExistente = dbCursor.fetchall()
    if not hospitalExistente:   # Si no existe el hospital, se crea
        sqlHospital = ("INSERT INTO hospital (nombre_hospital)"
                       "VALUES (%(nombre_hospital)s)")
        dbCursor.execute(sqlHospital, hospital_dict)
        mydb.commit()
        id_hospital = dbCursor.lastrowid
        estado = True
    else:
        id_hospital = hospitalExistente[0][0]
        estado = False
    return estado, id_hospital


def insert_consulta(mydb, id_hospital, consulta):
    consulta_dict = form_to_dict(consulta)
    consulta_dict['id_hospital'] = id_hospital
    consulta_dict['cantPacientes'] = 0
    consulta_dict['estado'] = 0

    dbCursor = mydb.cursor()
    # Verificar si la consulta ya existe [Mismo nombre especialista]
    dbCursor.execute("SELECT id_consulta FROM consulta WHERE nombreEspecialista=\"" + consulta["nombreEspecialista"] + "\";")
    consultaExistente = dbCursor.fetchall()
    if not consultaExistente: # Si no existe la consulta, se crea
        sqlConsulta = ("INSERT INTO consulta (id_hospital, cantPacientes, nombreEspecialista, tipoConsulta, estado)"
                       "VALUES (%(id_hospital)s, %(cantPacientes)s, %(nombreEspecialista)s, %(tipoConsulta)s, %(estado)s)")
        dbCursor.execute(sqlConsulta, consulta_dict)
        mydb.commit()
        id_consulta = dbCursor.lastrowid
        estado = True
    else:
        id_consulta = consultaExistente[0][0]
        estado = False
    return estado, id_consulta


def insert_paciente(mydb, id_hospital, paciente):
    dict_paciente = form_to_dict(paciente)
    dict_paciente['id_hospital'] = id_hospital

    dbCursor = mydb.cursor()
    # Verificar si el paciente ya existe [Mismo nombre paciente]
    dbCursor.execute("SELECT id_paciente FROM pacientes WHERE nombre=\"" + paciente["nombre"] + "\";")
    perfilExistente = dbCursor.fetchall()
    if not perfilExistente:  # Si no existe el paciente, se crea
        sqlPaciente = ("INSERT INTO pacientes (id_hospital, nombre, edad, peso, estatura)"
                       "VALUES (%(id_hospital)s, %(nombre)s, %(edad)s, %(peso)s, %(estatura)s)")
        dbCursor.execute(sqlPaciente, dict_paciente)
        mydb.commit()
        id_paciente = dbCursor.lastrowid
        estado = True
    else:
        id_paciente = perfilExistente[0][0]
        estado = False

    dict_paciente['id_paciente'] = id_paciente
    if estado and int(paciente["edad"]) <= 15:
        sqlPaciente = ("INSERT INTO pninno (id_paciente, rPesoEstatura)"
                       "VALUES (%(id_paciente)s, %(rPesoEstatura)s)")
        dbCursor.execute(sqlPaciente, dict_paciente)
        mydb.commit()
    elif estado and int(paciente["edad"]) <= 40:
        sqlPaciente = ("INSERT INTO pjoven (id_paciente, fumador, annosFumando)"
                       "VALUES (%(id_paciente)s, %(fumador)s, %(annosFumando)s)")
        dbCursor.execute(sqlPaciente, dict_paciente)
        mydb.commit()
    elif estado:  # and int(paciente["edad"]) >= 41:
        sqlPaciente = ("INSERT INTO panciano (id_paciente, tieneDieta)"
                       "VALUES (%(id_paciente)s, %(tieneDieta)s)")
        dbCursor.execute(sqlPaciente, dict_paciente)
        mydb.commit()

    return estado, id_paciente


def liberar_consulta(mydb, consultas):
    dbCursor = mydb.cursor()
    for consulta in consultas:
        if consulta['estado'] == 1:
            consulta['cantPacientes'] = consulta['cantPacientes'] + 1
            consulta['estado'] = 0
            dbCursor.execute('UPDATE consulta SET estado=0, cantPacientes=' + str(consulta['cantPacientes']) + ' WHERE id_consulta=' + str(consulta['id_consulta']))
    mydb.commit()
    return consultas


def get_paciente(mydb, id_paciente):
    dbCursor = mydb.cursor()
    dbCursor.execute("SELECT * FROM pacientes WHERE id_paciente=" + str(id_paciente))
    paciente = dbCursor.fetchall()[0]
    dict_paciente = {
        'id_paciente': paciente[0],
        'id_hospital': paciente[1],
        'nombre': paciente[2],
        'edad': paciente[3],
        'peso': paciente[4],
        'estatura': paciente[5]
    }
    if int(paciente[3]) <= 15:
        dbCursor.execute("SELECT rPesoEstatura FROM pninno WHERE id_paciente=" + str(paciente[0]))
        datos_extra = dbCursor.fetchall()[0]
        dict_paciente['rPesoEstatura'] = datos_extra[0]
    elif int(paciente[3]) <= 40:
        dbCursor.execute("SELECT fumador, annosFumando FROM pjoven WHERE id_paciente=" + str(paciente[0]))
        datos_extra = dbCursor.fetchall()[0]
        dict_paciente['fumador'] = datos_extra[0]
        dict_paciente['annosFumando'] = datos_extra[1]
    else:
        dbCursor.execute("SELECT tieneDieta FROM panciano WHERE id_paciente=" + str(paciente[0]))
        datos_extra = dbCursor.fetchall()[0]
        dict_paciente['tieneDieta'] = datos_extra[0]
    dict_paciente['prioridad'] = prioridad_paciente(dict_paciente)
    dict_paciente['riesgo'] = riesgo_paciente(dict_paciente['edad'], dict_paciente['prioridad'])
    return dict_paciente


def ocupar_consultas(mydb, id_consultas):
    dbCursor = mydb.cursor()
    for id_consulta in id_consultas:
        dbCursor.execute("UPDATE consulta SET estado=1 WHERE id_consulta=" + str(id_consulta))
    mydb.commit()
