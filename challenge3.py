# Importing required libraries
from datetime import datetime
import datetime
import csv
import sys
import re
import time
import base64
from oauth2client import file, client, tools
from apiclient import discovery
from apiclient import errors
from httplib2 import Http
from bs4 import BeautifulSoup
import dateutil.parser as parser
import mysql.connector
import ConfigParser
config_file="config.ini"
def variables():
    """ Funcion le el archivo config_file y lee la configuracion que necesita para su ejecucion"""
    try:
        config = ConfigParser.ConfigParser()
        config.read(config_file)
    except Exception, e:
        print e
        print "CRITICAL No pude leer el archivo %s revisar que exista" % config_file
        sys.exit(1)
    charge_variables("mysql_user mysql_db mysql_pass mysql_host mysql_port mysql_table mysql_table_id mysql_table_from mysql_table_asunto mysql_table_date", "mysql", config)
    charge_variables("credenciales user_id label_id_one label_id_two storage_json", "gmail", config)

def charge_variables(variables, seccion, config):
    """ Funcion se encarga de pasar lo que esta en el archivo config_file a variables globales. recibe como parametros las variables que se quieren poner como globales y el archivo config"""
    for i in variables.split():
        try:
            globals()['%s' % i] = config.get(seccion, i)
        except Exception, e:
            print e
            print "CRITICAL No pude leer %s revisar el archivo de configuracion" % i
            sys.exit(1)

def conectar_gmail():
    #Autenticacion https://developers.google.com/gmail/api/quickstart/python 
    # Creating a storage.JSON file with authentication details
    SCOPES = 'https://www.googleapis.com/auth/gmail.modify' # we are using modify and not readonly, as we will be marking the messages Read
    store = file.Storage(storage_json) 
    creds = store.get()
    #si no existe el storage va a crear uno
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(credenciales, SCOPES)
        creds = tools.run_flow(flow, store)
    GMAIL = discovery.build('gmail', 'v1', http=creds.authorize(Http()))
    return GMAIL

def marcar_email_leido(GMAIL,m_id):
    """ Funcion se encarga de marcar como leido un determinado email"""
    try:
        GMAIL.users().messages().modify(userId='me', id=m_id,body={ 'removeLabelIds': ['UNREAD']}).execute()
    except Exception, e:
        print e
        print "CRITICAL NO PUDE MARCAR COMO LEIDO EL EMAIL"

def guardar_mysql(devops_email_asunto, devops_email_from, devops_email_date):
    """ Funcion que guarda en la base de datos el asunto , from y email date """ 
    try:
        mymysql = mysql.connector.connect(host=mysql_host,user=mysql_user,passwd=mysql_pass,port=mysql_port,database=mysql_db)
    except Exception, e:
        print e
        print "CRITICAL no me pude conectar a la base de datos. verificar la base"
        print 'mysql_host: %s' % mysql_host
        print 'mysql_user: %s' % mysql_user
        print 'mysql_pass: ********'
        print 'mysql_port: %s' % mysql_port
        print 'database: %s' % mysql_db
        sys.exit(1)
    try:
        mycursor = mymysql.cursor()
        sql = "INSERT INTO " + mysql_table  + "(" + mysql_table_asunto + "," + mysql_table_from + "," + mysql_table_date +") VALUES (%s, %s, %s)"
        val = (devops_email_asunto, devops_email_from, devops_email_date)
        mycursor.execute(sql, val)
        mymysql.commit()
    except Exception, e:
        print e
        print "CRITICAL NO PUDE INSERTAR EN LA BASE DE DATOS"
        sys.exit(1)

def main():
    variables()
    GMAIL = conectar_gmail()
    unread_msgs = GMAIL.users().messages().list(userId='me',labelIds=[label_id_one, label_id_two]).execute()
    try:
        # We get a dictonary. Now reading values for the key 'messages'
        mssg_list = unread_msgs['messages']
    except Exception, e:
        print e
        print "Bandeja vacia"
        sys.exit(0)
    for mssg in mssg_list:
        print mssg['id']
    	m_id = mssg['id'] # get id of individual message
	message = GMAIL.users().messages().get(userId='me', id=m_id).execute() # fetch the message using API
        body = message['snippet']
	payld = message['payload'] # get payload of the message 
	headr = payld['headers'] # get header of the payload
	for head in headr: # getting the Subject
    	    if head['name'] == 'Subject':
	        msg_subject = head['value']
            elif head['name'] == 'Date':
                msg_date = head['value']
                date_parse = (parser.parse(msg_date))
                m_date = (date_parse.date())
                fecha = str(m_date)
            elif head['name'] == 'From':
                 msg_from = head['value']
            else:
		pass
        #print ("devops en asunto o body", "asunto: ", msg_subject, " fecha: ", fecha,  " from: ", msg_from, " body: " + body)
        if ( "devops" in msg_subject.lower() ) or ( "devops" in body.lower() ) :
            print ("devops en asunto o body", "asunto: ", msg_subject, " fecha: ", fecha,  " from: ", msg_from, " body: " + body)
            guardar_mysql(msg_subject, msg_from, fecha)
            marcar_email_leido(GMAIL,m_id)
if __name__ == '__main__':
        main()
