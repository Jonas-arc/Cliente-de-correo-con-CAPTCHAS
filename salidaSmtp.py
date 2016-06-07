import threading
import http
import os
import re
import urllib2
import logging
import email
from subprocess import call
from smtp2 import smtpEnvio
from listarCorreos import listaCorreos, listaCorreosView

debug = logging.getLogger('debug')

class salida(threading.Thread):

	def __init__(self, ruta, config):
		threading.Thread.__init__(self)
		self.configuracion=config
		self.ruta=ruta

	def run(self):
		debug.info("Inicio envio SMTP")
		self.enviarCorreos(self.ruta,"Salida")

	def enviarCorreos(self,path,carpeta):
		try:
			debug.info("Verificando conexion a internet")
			response=urllib2.urlopen('http://correocifrado.esy.es')
			debug.info("Conexion a internet verificada")
			debug.info("Conexion al servidor de CAPTCHAS verificada")
			salida=os.path.join(path,carpeta)
			dic=listaCorreosView(salida)
			httpPar={}
			httpPar["nombre"]=self.configuracion["nombre"]
			httpPar["contrasena"]=self.configuracion["passwdSSE"]
			debug.debug("Envio de correos de la carpeta : "+carpeta)
			for arc in dic.keys():
				try:
					debug.debug("Mensaje a enviar : "+arc)
					m = re.search('^(.+)\.txt$',arc)
					firma = m.group(1)
					debug.debug("Firma del mensaje : "+firma)
					fp = open(os.path.join(salida,arc), 'r')
					ms = email.message_from_file(fp)
					fp.close()
					httpPar["correo_electronico"]=ms["From"]
					httpPar["correo_destino"]=ms["To"]
					httpPar["firma"]=firma
					httpPar["archivo"]=open(os.path.join("./CAPTCHAS",firma+".zip"))
					debug.debug("Ruta de las imagenes CAPTCHAS : "+os.path.join("./CAPTCHAS",firma+".zip"))
					debug.debug("Envio de CAPTCHAS el servidor")
					if http.httpEnvio(httpPar):
						smtpEnvio(ms,self.configuracion["hostSmtp"], self.configuracion["portSmtp"],self.configuracion["passwd"], False)
						origen = os.path.join(salida,arc)
						destino =os.path.join(path,"Enviados",arc)
						instruc = "mv "+origen+" "+destino
						call(instruc, shell=True)	
				except Exception, e:
					debug.debug("Error al enviar Correo Electronico")
			listaCorreos(os.path.join(path,"Enviados"))
			listaCorreos(salida)
		except urllib2.URLError as err: 
			debug.error("Sin conexion a internet")
			debug.error("Sin conexion con el servidor de CAPTCHAS")