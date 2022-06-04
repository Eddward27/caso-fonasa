# caso-fonasa
Desafío entrevista de caso FONASA
___
Este proyecto usa [Flask](https://flask.palletsprojects.com) para el back-end y [Python Connector MySQL](https://dev.mysql.com/doc/connector-python/en/) para acceder a la base de datos [MySQL](https://www.mysql.com/).

También es necesario escribir un nombre de usuario y contraseña para acceder a la base de datos en `/db.py`

Para que funcione, se necesita un servidor MySQL con una base de datos como está modelada en `/sql/db_fonasa.sql`, también hay datos de ejemplo en `/sql/rellenar_hospitales.sql` y `/sql/rellenar_consultas.sql`

Para instalar los requerimientos y ejecutar, use en una terminal:
```
$ pip install -r requirements.txt
$ py app.py
``` 
___
Autor: Matías Eduardo Allende Pino