def form_to_dict(form):
    dictform = {}
    for key, value in form.items():
        dictform[key] = value
    return dictform


def prioridad_paciente(paciente):
    prioridad = 0
    if int(paciente["edad"]) <= 5:
        prioridad = (paciente["peso"] - paciente["estatura"]) + 3
    elif int(paciente["edad"]) <= 12:
        prioridad = (paciente["peso"] - paciente["estatura"]) + 2
    elif int(paciente["edad"]) <= 15:
        prioridad = (paciente["peso"] - paciente["estatura"]) + 1
    elif int(paciente["edad"]) <= 40 and int(paciente["fumador"]) == 1:
        prioridad = (int(paciente["annosFumando"]) / 4) + 2
    elif int(paciente["edad"]) <= 40:
        prioridad = 2
    elif (int(paciente["edad"]) >= 60) and (int(paciente["edad"]) <=100) and (int(paciente["tieneDieta"]) == 1):
        prioridad = (int(paciente["edad"]) / 20) + 4
    elif int(paciente["edad"]) >= 41:
        prioridad = (int(paciente["edad"]) / 30) + 3
    return prioridad


def riesgo_paciente(edad, prioridad):
    riesgo = (edad * prioridad) / 100
    if edad >= 41:
        riesgo += 5.3
    return riesgo


def get_tipo_paciente(edad):
    if edad <= 15:
        return 0
    if edad <= 40:
        return 1
    return 2


def ordenar_lista(lista_espera, lista_pendiente=[]):
    lista_espera = lista_espera + lista_pendiente
    lista_espera.sort(reverse=True, key=lambda paciente: paciente['prioridad'])
    return lista_espera
