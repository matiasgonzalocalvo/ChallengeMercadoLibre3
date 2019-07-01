# CHALLENGE MERCADOLIBRE 3

## OBJETIVO

El challenge es armar un programa en Python, Ruby o Java. El
lenguaje lo elegís vos. La idea es que este programa pueda acceder a
una cuenta de Gmail, leer e identificar los emails que tengan la
palabra "DevOps" en el asunto o el cuerpo del email.
De estos correos debés guardar en una base de datos MySQL los
siguientes campos: fecha, from, subject.
La base de datos también debe ser creada.

## CONFIGURACION

En el archivo config.ini esta toda la configuracion

[mysql] | Justification
------- |  -------------
mysql_user| Nombre de usuario
mysql_db | Nombre de la base de datos
mysql_pass | password del usuario
mysql_host | host donde esta hosteado el mysql o mariadb
mysql_port | puerto del mysql o mariadb
mysql_table | nombre de la tabla
mysql_table_id | nombre de la columna id
mysql_table_from | nombre de la columna from
mysql_table_asunto | nombre de la columna asunto
mysql_table_date | nombre de la columna date

[gmail] | Justification
------- |  -------------
credenciales | archivo generado siguiendo estas instrucciones https://developers.google.com/gmail/api/quickstart/python
user_id | user id por lo general es "me"
label_id_one | leabel de INBOX
label_id_two |  leabel de  UNREAD
storage_json | nombre del archivo donde se va a guardar la authorizacion


##GMAIL 
Generar las credenciales (client_secret.json) para utilizar las apis de gmail ver siguiente enlace

  https://developers.google.com/gmail/api/quickstart/python


Si no existe el archivo storage_json. va a requerir darle permisos en forma manual siguiendo las instrucciones que arroje por pantalla
Mas info https://developers.google.com/gmail/api/quickstart/python



## Test script from Docker 

### pre requisitos

  Verificar el archivo config.ini ahi vive la configuracion. 
  el archivo storage.json tiene que estar configurado.

### Build docker

```bash
  docker build -t challenge3-mariadb -f Dockerfile-mariadb .
  docker build -t challenge3 -f Dockerfile .
```

### Exec mariadb
  
  El mariadb va a escuchar en la ip del host cambiar la configuracion por la ip
  para ver todas las variables del mariadb revisar la configuracion <https://hub.docker.com/_/mariadb>

```bash

  docker run --name challenge3-mariadb -e MYSQL_ROOT_PASSWORD="mercadolibre" -e MYSQL_DATABASE="mercadolibre_devops_email" -e MYSQL_USER="mercadolibre" -e MYSQL_PASSWORD="mercadolibre" -p 3306:3306 -d challenge3-mariadb:latest

```

### exec challenge Docker

```bash
  docker run --name challenge3  -v $(pwd)/config.ini:/ChallengeMercadoLibre3/config.ini -v $(pwd)/storage.json:/ChallengeMercadoLibre3/storage.json  -v $(pwd)/client_secret.json:/ChallengeMercadoLibre3/client_secret.json -d challenge3:latest

```

cada ves que se necesite ejecutar utilizar el siguiente comando 

```bash

  docker start challenge3

```

Ver los logs 

```bash

  docker logs challenge3

```



## Test script from Debian
Debian 9 netinstall

#Base de datos
Tener instalado mariadb server
```bash
  $ sudo apt install mariadb-server
  $ sudo mysql_secure_installation
```
Crear usuario y password

```mysql
  GRANT ALL ON *.* TO 'mercadolibre'@'localhost' IDENTIFIED BY 'mercadolibre' WITH GRANT OPTION;
  FLUSH PRIVILEGES;
```
Crear la base de datos

```mysql
  create database mercadolibre_ldap ;
```

crear tablas hay 2 maneras restaurando el dump

```mysql
  $ mysql -u mercadolibre -pmercadolibre mercadolibre_ldap < mysql/dump_mercadolibre_ldap.sql
```

### Python Config

Verificar tener instalado cliente pip

```bash
  $ sudo apt install python-pip
  $ sudo apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev
```

Instalar todas las dependencias

```bash
$ pip install -r requirements.txt
```


###  EJECUCION

```bash
  $ python challenge3.py
```
