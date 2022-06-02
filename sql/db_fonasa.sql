CREATE DATABASE caso_fonasa;
USE caso_fonasa;

CREATE TABLE hospital (
    id_hospital int NOT NULL AUTO_INCREMENT,
    nombre_hospital TINYTEXT NOT NULL,
    PRIMARY KEY (id_hospital)
);

CREATE TABLE consulta (
    id_consulta int NOT NULL AUTO_INCREMENT,
    id_hospital int NOT NULL,
    cantPacientes int,
    nombreEspecialista TINYTEXT,
    tipoConsulta int,                           -- 0 Pediatría, 1 Urgencia, 2 CGI (Consulta General Integral))
    estado int,                                 -- 0 Espera, 1 Ocupada
    PRIMARY KEY (id_consulta),
    FOREIGN KEY (id_hospital) REFERENCES hospital(id_hospital)
);

CREATE TABLE pacientes (
    id_paciente int NOT NULL AUTO_INCREMENT, -- Será usado también como NHC (Número de Historia Clínica)
    id_hospital int NOT NULL,
    nombre TINYTEXT,
    edad int,
    peso int,
    estatura int,
    -- noHistoriaClinica int,
    PRIMARY KEY (id_paciente),
    FOREIGN KEY (id_hospital) REFERENCES hospital(id_hospital)
);

CREATE TABLE pNinno (
    id_ninno int NOT NULL AUTO_INCREMENT,
    id_paciente int NOT NULL,
    rPesoEstatura int,
    PRIMARY KEY (id_ninno),
    FOREIGN KEY (id_paciente) REFERENCES pacientes(id_paciente)
);

CREATE TABLE pJoven (
    id_joven int NOT NULL AUTO_INCREMENT,
    id_paciente int NOT NULL,
    fumador bool,
    annosFumando int,
    PRIMARY KEY (id_joven),
    FOREIGN KEY (id_paciente) REFERENCES pacientes(id_paciente)
);

CREATE TABLE pAnciano (
    id_anciano int NOT NULL AUTO_INCREMENT,
    id_paciente int NOT NULL,
    tieneDieta bool,
    PRIMARY KEY (id_anciano),
    FOREIGN KEY (id_paciente) REFERENCES pacientes(id_paciente)
);