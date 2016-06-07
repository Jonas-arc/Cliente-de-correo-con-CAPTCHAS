import json
import os
import email
import quopri
import logging

from os import path

debug = logging.getLogger('debug')

def listFiles(folder):
	return [d for d in os.listdir(folder) if path.isfile(path.join(folder, d))]

def listaCorreos(ruta):
	debug.info("Listando correos de la Carpeta : "+ruta)
	archivos = listFiles(ruta)
	disc={}
	for archivo in archivos:
		if archivo.find(".txt")>0:
			fp = open(path.join(ruta,archivo), 'r')
			ms = email.message_from_file(fp)
			fp.close()
			if len(ms.get_payload())>1:
				disc[archivo]=(ms['Subject'],ms['From'],ms['Date'],"mail-attachment")
			else:
				disc[archivo]=(ms['Subject'],ms['From'],ms['Date'],"")
	lista=open(path.join(ruta,"lista.json"),"w")	
	lista.write(json.dumps(disc))
	lista.close
	debug.debug("Numero de correos encontrados : "+str(len(disc)))

def listaCorreosView(ruta):
	debug.info("Listando correos para visualizar de la Carpeta : "+ruta)
	jsonCorreo = open(os.path.join(ruta,"lista.json"),"r")
	if jsonCorreo:
		jsonLectura = jsonCorreo.readline()
		jsonCorreo.close()
		dic = json.loads(jsonLectura)
		debug.debug("Numero de correos encontrados : "+str(len(dic)))
		return dic
	else:
		return None

def contarCorreo(directorio):
	debug.info("Contando correos en el directorio : "+directorio)
	if directorio==None:
		return -1
	for files in os.walk(directorio):
		num=0
		for file in files[2]:
			if file.find(".txt")>0:
				num+=1
	debug.debug("Correos encontrados : "+str(num))
	return num

def body(ms):
	debug.debug("Buscando el cuerpo del mensaje")
	charset = ms.get_content_charset()
	if ms.is_multipart():
		for payload in ms.get_payload():
			ctype=payload.get_content_type()
			cdispo = str(payload.get('Content-Disposition'))
			if payload.is_multipart():
				return body(payload)
				break
			elif ctype=='text/plain' and 'attachment' not in cdispo:
				charset = payload.get_content_charset()
				aux = payload.get_payload(decode=True)
				debug.debug("Cuerpo del mensaje encontrado")
				return aux.decode(charset)
	else:
		aux = ms.get_payload(decode=True)
		debug.debug("Cuerpo del mensaje encontrado")
		return aux.decode(charset)
#listaCorreos("./Usuarios/jonny.test.arc.99@hotmail.com/Entrada/")
#print(listaCorreosView("./Usuarios/jonny.test.arc.99@hotmail.com/Entrada/"))
#print(contarCorreo("./Usuarios/jonny.test.arc.99@hotmail.com/Enviados/"))