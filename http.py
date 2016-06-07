import urllib
import urllib2
import re
import logging
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

debug = logging.getLogger('debug')

def httpEnvio(data):
	register_openers()
	datagen, headers = multipart_encode(data)
	request = urllib2.Request("http://correocifrado.esy.es/AltaMensage.php", datagen, headers)
	found=''
	try:
		for line in urllib2.urlopen(request):
			if line.find("name=\"respuesta\"") >= 0:
				m = re.search('>([0-9]+)<',line)
				if m:
					found = m.group(1)
					debug.info("Respuesta del servidor de CAPTCHAS : "+found)
					if found=="5":
						debug.info("Envio de CAPTCHAS correcto")
						return True
					else:
						debug.error("Error al subir CAPTCHAS")
						return False
				else:
					debug.error("Error en el servidor de CAPTCHAS")
					return False
	except Exception, e:
		debug.error(e)
		return False

def httpDescarga(data,nomArc):
	register_openers()
	datagen, headers = multipart_encode(data)
	debug.info("Peticion al servidor de CAPTCHAS")
	try:
		request = urllib2.Request("http://correocifrado.esy.es/BusquedaArchivo.php", datagen, headers)
		found=''
		for line in urllib2.urlopen(request):
			if line.find("name=\"respuesta\"") >= 0:
				m = re.search('>(http.+zip)<',line)
				if m:
					found = m.group(1)
					debug.info("Respuesta del servidor de CAPTCHAS : "+found)
					break
				else:
					debug.error("Error en la busqueda de los CAPTCHAS")
					return False
	except urllib2.HTTPError, e:
		debug.error(e.code)
		return False
	except urllib2.URLError, e:
		debug.error(e.args)
		return False
	try:
		debug.info("Descarga de CAPTCHAS")
		res=urllib2.urlopen(found)
		arc=open(nomArc,"w")
		arc.write(res.read())
		arc.close()
		return True
	except urllib2.HTTPError, e:
		debug.error(e.code)
		return False
	except urllib2.URLError, e:
		debug.error(e.args)
		return False

def httpAltaUsu(data):
	debug.info("Alta de usuario en el servidor de CAPTCHAS")
	register_openers()
	datagen, headers = multipart_encode(data)
	request = urllib2.Request("http://correocifrado.esy.es/AltaUsuario.php", datagen, headers)
	found=''
	try:
		for line in urllib2.urlopen(request):
			if line.find("name=\"respuesta\"") >= 0:
				m = re.search('>([0-9]+)<',line)
				if m:
					found = m.group(1)
					debug.info("Respuesta del servidor de CAPTCHAS : "+found)
					if found=="5":
						debug.info("Envio de registro correcto")
						return True
					else:
						debug.error("Error en el registro de usuario")
						return False
				else:
					debug.error("Error en el servidor de CAPTCHAS")
					return False
	except Exception, e:
		debug.error(e)
		return False

