import db
from util import get_tipo_paciente, ordenar_lista


def listar_pacientes_mayor_riesgo(mydb, id_hospital, id_paciente):
    # Lista a los pacientes con más riesgo que el paciente pedido por parámetro
    pacientes = db.get_pacientes(mydb, id_hospital)
    pacientes.sort(reverse=True, key=lambda paciente: paciente['riesgo'])
    mas_riesgo = []
    for paciente in pacientes:
        if paciente['id_paciente'] == int(id_paciente):
            break
        mas_riesgo.append(paciente)
    return mas_riesgo


def atender_paciente(consultas, lista_espera, lista_pendiente, lista_atencion, flagOPT=False):
    # Asumiendo que las listas están ordenadas
    tipos_consulta_libres = []
    id_consulta_libres = []
    id_consulta_atendido = []
    lista_no_atendidos = []
    for consulta in consultas:
        if consulta['estado'] == 0:
            tipos_consulta_libres.append(consulta['tipoConsulta'])
            id_consulta_libres.append(consulta['id_consulta'])
    if len(lista_espera) == 0:  # Si la sala de espera está vacía, se atiende a los que se pueden y los demás pasan a espera
        lista_espera = lista_pendiente.copy()
        lista_pendiente.clear()
    for paciente_espera in lista_espera:    # Se atienden a los que se pueda en la lista de espera
        index = -1
        prioridad_paciente = paciente_espera['prioridad']
        tipo_paciente = get_tipo_paciente(paciente_espera['edad'])
        if prioridad_paciente <= 4 and tipo_paciente == 0:  # Pediatría NO Urgente
            if 0 in tipos_consulta_libres:  # Si hay pediatría disponible
                index = tipos_consulta_libres.index(0)
        elif prioridad_paciente <= 4:  # CGI
            if 2 in tipos_consulta_libres:
                index = tipos_consulta_libres.index(2)
        elif 1 in tipos_consulta_libres:  # Urgencias
            index = tipos_consulta_libres.index(1)
        if index != -1:  # Si se encontró donde atender al paciente
            id_consulta_atendido.append(id_consulta_libres[index])
            id_consulta_libres.pop(index)
            tipos_consulta_libres.pop(index)
            lista_atencion.append(paciente_espera)
        else:
            lista_no_atendidos.append(paciente_espera)
    # Actualizar consultas
    mydb = db.get_db()
    db.ocupar_consultas(mydb, id_consulta_atendido)
    # Actualizar listas
    lista_espera = lista_no_atendidos.copy()
    if not flagOPT:
        lista_espera = ordenar_lista(lista_espera, lista_pendiente)
        lista_pendiente.clear()
    return lista_espera, lista_pendiente, lista_atencion


def liberar_consultas(consultas, lista_espera, lista_pendiente, lista_atencion):
    # Libera todas las consultas ocupadas
    # Tener en cuenta que se atienden a los pacientes en lista de espera
    mydb = db.get_db()
    # consultasUpdate = db.liberar_consulta(mydb, consultas)
    db.liberar_consulta(mydb, consultas)
    lista_atencion.clear()
    lEspera, lPendiente, lAtencion = atender_paciente(consultas, lista_espera, lista_pendiente, lista_atencion)
    return lEspera, lPendiente, lAtencion


def listar_pacientes_fumadores_urgentes(pacientes):
    # Lista el nombre de todos los pacientes fumadores
    # que necesitan ser atendidos con urgencia (Prioridad mayor a 4)
    fumadores_urgentes = []
    for paciente in pacientes:
        if (paciente['edad'] >= 16) and (paciente['edad'] <= 40):
            if (paciente['fumador'] == 1) and (paciente['prioridad'] > 4):
                fumadores_urgentes.append(paciente)
    return fumadores_urgentes


def consulta_mas_pacientes_atendidos(mydb, id_hospital=-1):
    # Muestra la consulta que más pacientes haya atendido hasta el momento
    consultas = db.get_consultas(mydb, id_hospital)
    consultas.sort(reverse=True, key=lambda consulta: consulta['cantPacientes'])
    max_pacientes = consultas[0]['cantPacientes']
    consultas_mas_pacientes = []
    for consulta in consultas:
        if max_pacientes != consulta['cantPacientes']:
            break
        consultas_mas_pacientes.append(consulta)
    return consultas_mas_pacientes


def paciente_mas_anciano(lista_espera):
    # Muestra el paciente más anciano de la lista de espera (Paciente con mayor edad)
    lista = []
    lista.extend(lista_espera)
    lista.sort(reverse=True, key=lambda paciente: paciente['edad'])
    pacientes_mas_ancianos = []
    if len(lista) == 0:
        return pacientes_mas_ancianos
    max_edad = lista[0]['edad']
    if max_edad <=40:
        return pacientes_mas_ancianos
    for paciente in lista:
        if max_edad != paciente['edad']:
            break
        pacientes_mas_ancianos.append(paciente)
    return pacientes_mas_ancianos


def optimizar_atencion(consultas, lista_espera, lista_pendiente, lista_atencion):
    # Ordenar lista_pendientes
    pacientes_riesgo = []
    pacientes_ninno_anciano = []
    pacientes_joven = []
    for pacientes_pendientes in lista_pendiente:
        tipo_paciente = get_tipo_paciente(pacientes_pendientes['edad'])
        if pacientes_pendientes['riesgo'] > 4:
            pacientes_riesgo.append(pacientes_pendientes)
        elif tipo_paciente == 1:
            pacientes_joven.append(pacientes_pendientes)
        else:
            pacientes_ninno_anciano.append(pacientes_pendientes)
    pacientes_riesgo.sort(reverse=True, key=lambda paciente: paciente['riesgo'])
    lista_pendiente.clear()
    lista_pendiente.extend(pacientes_riesgo)
    lista_pendiente.extend(pacientes_ninno_anciano)
    lista_pendiente.extend(pacientes_joven)

    # Se atienden los pacientes sin mover nuevos pacientes a la sala de espera
    lista_espera, lista_pendiente, lista_atencion = atender_paciente(consultas, lista_espera, lista_pendiente, lista_atencion, True)
    return lista_espera, lista_pendiente, lista_atencion


def ingresar_paciente(paciente, lista_pendiente):
    lista_pendiente.append(paciente)
    lista_ordenada = ordenar_lista(lista_pendiente)
    return lista_ordenada
