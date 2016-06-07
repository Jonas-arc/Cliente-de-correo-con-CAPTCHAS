import os
from os import path
import json
import http
import logging
from subprocess import call

debug = logging.getLogger('debug')

def listFiles(folder):
	return [d for d in os.listdir(folder) if path.isfile(path.join(folder, d))]

def buscarCAPTCHAS(firma, correoDes, correoOri):
	debug.info("Busqueda de CAPTCHAS")
	ruta=path.join("./CAPTCHAS",firma)
	if path.exists(ruta):
		debug.info("CAPTCHAS ya descargados")
		return listarCaptchas(ruta)
	elif path.exists(ruta+".zip"):
		debug.info("CAPTCHAS en archivo zip")
		unzip="unzip "+ruta+".zip -d ./CAPTCHAS"
		unz=call(unzip, shell=True)
		debug.info("Descomprecion de archivo zip : "+ruta+".zip")
		return listarCaptchas(ruta)
	else:
		debug.info("Inicio de la descarga de CAPTCHAS")
		datos={}
		datos["correo_electronico"]=correoOri
		datos["correo_destino"]=correoDes
		datos["firma"]=firma
		if http.httpDescarga(datos,ruta+".zip"):
			unzip="unzip "+ruta+".zip -d ./CAPTCHAS"
			unz=call(unzip, shell=True)
			rm=call("rm "+ruta+".zip", shell=True)
			debug.info("Descomprecion de archivo zip : "+ruta+".zip")
			return listarCaptchas(ruta)
		else:
			return []

#unzip archivo
def listarCaptchas(ruta):
	if path.exists(path.join(ruta,"lista.json")):
		op=1
		jsonCorreo = open(path.join(ruta,"lista.json"),"r")
		jsonLectura = jsonCorreo.readline()
		jsonCorreo.close()
		archivos = json.loads(jsonLectura)
		debug.debug(str(archivos))
	else:
		archivos = listFiles(ruta)
		debug.debug("Numero de archivos : "+str(len(archivos)))
		debug.debug("Nombre de los archivos"+str(archivos))
		op=0
	debug.info("CAPTCHAS : "+str([ruta,archivos,op]))
	return [ruta,archivos,op]