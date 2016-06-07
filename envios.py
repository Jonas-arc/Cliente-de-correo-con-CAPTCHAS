import threading
import hashlib
import time
import os
import re
import urllib2
import email
import SSE
import http
import logging
from subprocess import call
from SSE import empaquetar
#from empaquetar import empaquetar
from subprocess import call

from smtp2 import smtpEnpaquetar, smtpEnvio
from listarCorreos import listaCorreos, listaCorreosView

debug = logging.getLogger('debug')

class envios(threading.Thread):
	
	def __init__(self, correoDes, correoOri, asunto, body, attach, config):
		threading.Thread.__init__(self)
		self.correoD = correoDes
		self.correoO = correoOri
		self.asunto = asunto
		self.cuerpo = body
		self.attachment = attach
		self.configuracion=config
	
	def run(self):
		debug.info("Inicio del envio")
		firma =self.firma()
		debug.debug("Firma del mensaje : "+firma)
		debug.info("Mensaje a cifrar : "+self.cuerpo)
		body,ruta = empaquetar(self.cuerpo,firma,self.configuracion["SSE"])
		debug.info("Mensaje cifrado : "+body)
		body += "\n------SSE Cipher------\n"
		body += firma
		body += "\n------SSE Cipher------\n"
		debug.debug("Mensaje firmado"+body)
		debug.debug("Ruta de captchas : "+ruta)
		debug.debug("Moviendo CAPTCHAS del mensaje a la carpeta CAPTCHAS")
		mv=call("mv "+ruta+" ./CAPTCHAS/"+firma+".zip", shell=True)
		ms=smtpEnpaquetar(self.correoD, self.asunto, self.correoO, body, self.attachment)
		path=os.path.join("./Usuarios",self.correoO,"Salida")
		fp = open(os.path.join(path,firma+".txt"), 'w')
		fp.write(ms.as_string())
		fp.close()
		listaCorreos(path)
		self.enviarCorreos(os.path.join("./Usuarios",self.correoO),"Salida")

	def firma(self):
		m = hashlib.md5()
		localtime = time.asctime( time.localtime(time.time()) )
		m.update(self.correoD+localtime+self.correoO)
		return m.hexdigest()

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
#aux = envios("sdfg", "dsfg","asdfd","dfg",[])
#aux.run()