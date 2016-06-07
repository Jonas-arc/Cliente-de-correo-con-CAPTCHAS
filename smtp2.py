import os
import smtplib
import mimetypes
import hashlib
import time
import email
import logging
# For guessing MIME type based on file name extension
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

debug = logging.getLogger('debug')

def validarSmtp(dat):
	debug.info("Abriendo conexion SMTP")
	try:
		if dat["ssl"]:
			M = smtplib.SMTP_SSL(host=dat["host"], port=dat["port"], keyfile=dat["keyfile"], certfile=dat["certfile"])
		else:
			M = smtplib.SMTP(host=dat["host"], port=dat["port"])
		#M.set_debuglevel(True)
	except Exception, e:
		debug.error("Error de conexion con el servidor SMTP : "+dat["host"])
		debug.error(e)
		return False
	debug.info("Validando usuario")
	try:
		M.ehlo()
		M.starttls()
		M.ehlo()
		M.login(dat["user"], dat["passwd"])
		M.close()
		return True
	except Exception, e:
		debug.error("Credenciales invalidas")
		return False

def smtpEnpaquetar(to, subject, fromUser, text, attach):
	debug.info("Empaquetado mensaje")
	outer = MIMEMultipart()
	if to == None:
		debug.error("Direccion destino vacia")
		return 0
	elif fromUser == None:
		debug.error("Direccion origen vacia")
		return 1
	elif (subject == None) and (text == None):
		debug.error("Mensaje vacio")
		return 2

	outer['From'] = fromUser
	outer['To'] = to
	outer['Subject'] = subject
	outer['Date'] = time.asctime(time.localtime(time.time()))

	outer.attach(MIMEText(text))
	for path in attach:
		if not os.path.isfile(path):
			continue
		ctype, encoding = mimetypes.guess_type(path)
		if ctype is None or encoding is not None:
			ctype = 'application/octet-stream'

		maintype, subtype = ctype.split('/', 1)
		if maintype == 'text':
			fp = open(path)
			msg = MIMEText(fp.read(), _subtype=subtype)
			fp.close()

		elif maintype == 'image':
			fp = open(path, 'rb')
			msg = MIMEImage(fp.read(), _subtype=subtype)
			fp.close()

		elif maintype == 'audio':
			fp = open(path, 'rb')
			msg = MIMEAudio(fp.read(), _subtype=subtype)
			fp.close()

		else:
			fp = open(path, 'rb')
			msg = MIMEBase(maintype, subtype)
			msg.set_payload(fp.read())
			fp.close()
			encoders.encode_base64(msg)

		msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(path))
		outer.attach(msg)	  
	return outer

def smtpEnvio(ms,server,port,passwd,ssl):
	debug.info("Enviando de mensaje por SMTP")
	fromUser = ms['From']
	to = ms['To']
	composed = ms.as_string()
	debug.debug("Datos del mensaje")
	debug.debug("Servidor: "+server)
	debug.debug("Puerto: "+str(port))
	try:
		s = smtplib.SMTP(server,port)
		s.ehlo()
		debug.debug("Tls")
		s.starttls()
		s.ehlo()
		debug.debug("Validando usuario")
		s.login(fromUser, passwd)
		debug.debug("Enviando mensaje")
		s.sendmail(fromUser, to, composed)
		debug.debug("Envio completado")
		s.close()
		return 0
	except Exception, e:
		return 1

#smtpMensaje("jonas.arcos.99@gmail.com", "prueba", "jonny.test.arc.99@hotmail.com", "prueba text", ["webcam.jpg"], "360_live", "smtp-mail.outlook.com", 587, True)
#smtpEnvio(arc='pop3.txt',passwd="360_live", server="smtp-mail.outlook.com", port=587)
#print(datosPrincipales("pruebaPop.txt"))