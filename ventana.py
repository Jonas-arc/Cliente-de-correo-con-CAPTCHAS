#! /usr/bin/python

import gi
import os
import email
import json
import SSE
import re
import captchas
import http
import logging
import time

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio
from smtp2 import validarSmtp
from listarCorreos import listaCorreosView
from listarCorreos import contarCorreo
from listarCorreos import body
from pop3 import conexionPop3
from pop3 import validarPop
from envios import envios
from salidaSmtp import salida


path = './Usuarios'
EMAIL_REGEX = re.compile(r'([(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15})')

def listdirs(folder):
	return [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]

def listFiles(folder):
	return [d for d in os.listdir(folder) if os.path.isfile(os.path.join(folder, d))]

class MyWindow(Gtk.Window):

	user=listdirs(path)
	selectCarpeta=None
	selectUsuario=None
	config={}

	def __init__(self,config):
		while len(self.user) == 0:
			self.user = listdirs(path)
		self.config = config
		Gtk.Window.__init__(self, title="Cliente de Correos")
		self.set_border_width(4)
		self.set_default_size(800, 600)

		self.notebook = Gtk.Notebook()
		self.add(self.notebook)

		self.page = self.newPage()
		self.page.set_border_width(10)
		self.notebook.append_page(self.page, Gtk.Label('Index'))

	def visorCorreo(self):
		debug.debug("Carga del visor de mensaje de correo")
		vistaCorre = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		self.emisor = Gtk.Label("De: ")
		self.emisor.set_justify(Gtk.Justification.LEFT)
		self.destinatorio = Gtk.Label("Para: ")
		self.destinatorio.set_justify(Gtk.Justification.LEFT)
		self.asunto = Gtk.Label("Asunto: ")
		self.asunto.set_justify(Gtk.Justification.LEFT)
		descifrado= Gtk.Button(label="Descifrar")
		descifrado.connect("clicked", self.descifrarBody)
		box1 = Gtk.VBox(False,10)
		box1.pack_start(self.emisor,True,True,0)
		box1.pack_end(self.destinatorio,False,True,0)
		box2 = Gtk.HBox(False,0)
		box2.pack_start(self.asunto,False, False, 0)
		box2.pack_end(descifrado,False,False,0)
		self.cuerpo = Gtk.TextView()
		self.cuerpo.set_wrap_mode(Gtk.WrapMode.WORD)
		self.cuerpo.set_editable(False)
		scrol = Gtk.ScrolledWindow()
		scrol.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
		scrol.set_vexpand(True)
		scrol.add(self.cuerpo)
		vistaCorre.add(box1)
		vistaCorre.add(box2)
		vistaCorre.add(scrol)
		return vistaCorre

	def visorCorreoNuevo(self):
		debug.info("Carga del visor para la redaccion de un mensaje de correo")
		vistaCorre = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		newDest = Gtk.Entry(name="Destino")
		newDest.set_editable(True)
		newAsunto = Gtk.Entry(name="Asunto")
		newAsunto.set_editable(True)

		destinatorio = Gtk.Label("Para: ")
		destinatorio.set_justify(Gtk.Justification.LEFT)
		asunto = Gtk.Label("Asunto: ")
		asunto.set_justify(Gtk.Justification.LEFT)

		Cerrar = Gtk.Button(label="Cerrar")
		Cerrar.connect("clicked", self.cerrarPagina)
		Enviar = Gtk.Button(label="Enviar")
		Enviar.connect("clicked", self.enviarMensage)

		box1 = Gtk.HBox(False,0)
		box1.pack_start(destinatorio,False,False,0)
		box1.pack_start(newDest,True,True,0)
		
		box2 = Gtk.HBox(False,0)
		box2.pack_start(asunto,False, False, 0)
		box2.pack_start(newAsunto,True, True, 0)

		box3 = Gtk.HBox(False,0)
		box3.pack_end(Cerrar,False, False, 0)
		box3.pack_end(Enviar,False, False, 0)

		cuerpo = Gtk.TextView(name="cuerpo")
		cuerpo.set_wrap_mode(Gtk.WrapMode.WORD)
		#WRAP_WORD
		scrol = Gtk.ScrolledWindow()
		scrol.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
		scrol.set_vexpand(True)
		scrol.add(cuerpo)
		vistaCorre.add(box1)
		vistaCorre.add(box2)
		vistaCorre.add(scrol)
		vistaCorre.add(box3)
		return vistaCorre

	def cerrarPagina(self,button):
		page=self.notebook.get_current_page()
		debug.info("Pagina "+str(page)+" cerrada")
		self.notebook.remove_page(page)
		self.notebook.show_all()

	def enviarMensage(self,button):
		debug.info("Inicia envio de nuevo mensaje de correo")
		page=self.notebook.get_current_page()
		contenedor = self.notebook.get_nth_page(page)
		asunto = ""
		destino = ""
		cuerpo = ""
		for c in contenedor.get_children():
				for x in c.get_children():
					if isinstance(x,Gtk.Entry):
						if x.get_name() == "Destino":
							destino = x.get_text()
							debug.debug("Direccion del destinatario: "+destino)
						elif x.get_name() == "Asunto":
							asunto = x.get_text()
							debug.debug("Asunto del mensaje: "+asunto)
					if isinstance(x,Gtk.TextView):
						buf = x.get_buffer()
						end_iter = buf.get_end_iter()
						start_iter = buf.get_start_iter()
						cuerpo = x.get_buffer().get_text(start_iter, end_iter, True)
						debug.debug("Cuerpo del mensaje: "+cuerpo)
		if not destino.split():
			debug.error("Direccion de correo destino")
			dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
				Gtk.ButtonsType.CANCEL, "Error al enviar Mensaje")
			dialog.format_secondary_text(
				"La direccion de correo destino no ha sido ingresado.")
			dialog.run()
			dialog.destroy()
		elif not asunto and not cuerpo:
			debug.warning("Mensaje o el asunto vacio")
			dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING,
				Gtk.ButtonsType.OK_CANCEL, "Mensaje vacio")
			dialog.format_secondary_text(
				"El mensaje o el asunto estan vacios, decea que se envie el mensaje?")
			response = dialog.run()
			if response == Gtk.ResponseType.OK:
				debug.info("Mensaje incompleto")
				t = envios(destino,self.user[0],asunto,cuerpo,[],self.config)
				t.start()
			dialog.destroy()
		else:
			debug.info("Mensaje Completo")
			t = envios(destino,self.user[0],asunto,cuerpo,[],self.config)
			t.start()
		debug.debug("Asunto: "+asunto)
		debug.debug("Destino: "+destino)
		debug.debug("Cuerpo: "+cuerpo)
		page=self.notebook.get_current_page()
		debug.info("Cerrando pagina : "+ str(page))
		self.notebook.remove_page(page)
		self.notebook.show_all()

	def descifrarBody(self, button):
		debug.info("Descifrando mensaje")
		bodyBuffer=self.cuerpo.get_buffer()
		start_iter = bodyBuffer.get_start_iter()
		end_iter = bodyBuffer.get_end_iter()
		text = bodyBuffer.get_text(start_iter, end_iter, True) 
		firma=text.find("------SSE Cipher------")
		if(firma>=0):
			debug.info("Mensaje cifrado")
			text2 = text[firma:]
			m = re.search('\-\n(.+)\n\-',text2)
			if(m!=None):
				textFirma = m.group(1)
				debug.debug("Firma del mensaje : "+textFirma)
				correoOrigen=self.emisor.get_text()
				correoDestino=self.destinatorio.get_text()
				m = re.search("([(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15})",correoOrigen)
				correoOriegen = m.group(1)
				m = re.search("([(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15})",correoDestino)
				correoDestino = m.group(1)
				debug.debug("Direccion de Origen del mensaje : "+correoOriegen)
				debug.debug("Direccion de Destino del mensaje : "+correoDestino)
				debug.info("Busqueda de CAPTCHAS")
				despliegue=captchas.buscarCAPTCHAS(textFirma,correoDestino,correoOriegen)
				if len(despliegue)>0:
					debug.info("Inicia despliegue de CAPTCHAS")
					ventanaCaptcha(self,despliegue)
				else:
					debug.error("Error en el despliegue de CAPTCHAS")
					dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
					Gtk.ButtonsType.CANCEL, "Error al descargar CAPTCHA")
					dialog.format_secondary_text(
						"Ocurrio un error con el servidor, intentarlo mas tarde")
					dialog.run()
					dialog.destroy()
		else:
			debug.info("Mensaje no cifrado")

	def listaMail(self, usuario, carpeta):
		debug.info("Listando correos de la carpeta : "+carpeta)
		software_liststore = Gtk.ListStore(str, str, str, str)
		if self.selectCarpeta == None:
			archivos = [("", "",  "", "")]
		else:
			archivos = [("prueba", "prueba",  "prueba", "mail-attachment")]
		for archivo in archivos:
			software_liststore.append(list(archivo))
		
		lista = software_liststore.filter_new()

		self.listaCar = Gtk.TreeView.new_with_model(lista)
		self.listaCar.connect("row-activated",self.celdasCorreo)
		for i, column_title in enumerate(["Asunto", "Correo", "Fecha", "Adjunto"]):
			if i == 3:
				renderer = Gtk.CellRendererPixbuf()
				column = Gtk.TreeViewColumn(column_title, renderer, icon_name=i)
			else:
				renderer = Gtk.CellRendererText()
				column = Gtk.TreeViewColumn(column_title, renderer, text=i)
			self.listaCar.append_column(column)

		scrollable_treelist = Gtk.ScrolledWindow()
		scrollable_treelist.set_vexpand(True)
		scrollable_treelist.set_hexpand(True)
		scrollable_treelist.add(self.listaCar)
		
		return scrollable_treelist

	def listaCarpetas(self, usuarios):
		debug.info("Listando carpetas del usuario : "+str(usuarios))
		treestore = Gtk.TreeStore(str)
		numCorreo = 0
		for usuario in usuarios:
			carpetas = listdirs(os.path.join(path,usuario))
			piter = treestore.append(None, ['%s' % usuario])
			for carpeta in carpetas:
				numCorreo = contarCorreo(os.path.join(path,usuario,carpeta))
				if carpeta=="Entrada":
					treestore.prepend(piter, ['%s \t %d' % (carpeta, numCorreo)])
				else:
					treestore.append(piter, ['%s \t %d' % (carpeta, numCorreo)])

		treeview = Gtk.TreeView(treestore)		
		tvcolumn = Gtk.TreeViewColumn('Cuentas de Correos')
		tvcolumn.set_reorderable(False)
		treeview.append_column(tvcolumn)
		treeview.connect("row-activated",self.celdasCarp)
		cell = Gtk.CellRendererText()
		tvcolumn.pack_start(cell, True)
		tvcolumn.add_attribute(cell, 'text', 0)
		treeview.set_search_column(0)
		tvcolumn.set_sort_column_id(0)
		treeview.set_reorderable(False)
		return treeview

	def celdasCorreo(self, treeview, posi, column):
		debug.info("Abriendo mensaje de correo")
		model = treeview.get_model()
		car = model.get_iter(posi)
		correo = (model.get_value(car, 0),model.get_value(car, 1),model.get_value(car, 2),model.get_value(car, 3))
		for key in self.listaCotejoCorreos:
			aux = self.listaCotejoCorreos[key]
			if ((aux[1]==correo[1]) and (aux[2]==correo[2])):
				archivo=key
				break
		ruta=os.path.join(path, self.selectUsuario, self.selectCarpeta, archivo)
		fp=open(ruta,"r")
		ms = email.message_from_file(fp)
		fp.close()
		self.destinatorio.set_text("Para: "+ms['To'])
		self.emisor.set_text("De: "+ms['From'])
		self.asunto.set_text("Asunto: "+ms['Subject'])
		textbody = body(ms)
		debug.debug("Cuerpo del mensaje : "+textbody.strip())
		buffered = Gtk.TextBuffer()
		buffered.set_text(textbody.strip())
		self.cuerpo.set_buffer(buffered)

	def celdasCarp(self, treeview, posi, column):
		model = treeview.get_model()
		car = model.get_iter(posi)
		carpeta = model.get_value(car, 0)
		debug.info("Despliegue de correos en la carpeta :"+carpeta)
		if carpeta.find('@')>0:
			debug.warning("Seleccion de cuenta de correo electronico")
			return
		carpeta = carpeta.split('\t')[0].strip()
		self.selectCarpeta=carpeta
		usu = model.iter_parent(car)
		usuario = model.get_value(usu, 0)
		self.selectUsuario=usuario
		self.listaCotejoCorreos = listaCorreosView(os.path.join(path,usuario,carpeta))
		software_liststore = Gtk.ListStore(str, str, str, str)
		debug.debug("Listado de correos")
		for reg in self.listaCotejoCorreos:	
			software_liststore.append(self.listaCotejoCorreos[reg])
		lista = software_liststore.filter_new()
		self.listaCar.set_model(lista)

	def headerMail(self):
		box = Gtk.HBox(False,0)
		botonNewMail = Gtk.Button(label="Nuevo correo")
		botonNewMail.connect("clicked", self.nuevoCorreo,"newMail")
		botonEnviarRecibir = Gtk.Button(label="Enviar y Recibir")
		botonEnviarRecibir.connect("clicked", self.enviarRecibir)
		botonHerramientas = Gtk.Button(label="Herramientas")
		box.pack_start(botonNewMail, False, False, 0)
		box.pack_start(botonEnviarRecibir, False, False, 0)
		#box.pack_end(botonHerramientas, False, False, 0)
		return box

	def nuevoCorreo(self, button,name):
		debug.info("Nueva ventana de redaccion : "+name)
		self.pageNuevoCorreo = self.visorCorreoNuevo()
		self.pageNuevoCorreo.set_border_width(10)
		self.notebook.insert_page(self.pageNuevoCorreo, Gtk.Label("Nuevo Correo"),1)
		self.notebook.show_all()

	def enviarRecibir(self, button):
		debug.info("Enviando y reciviendo mensajes de correo electronico")
		debug.debug("Configurancion del sistema : "+str(self.config))
		host = self.config["hostPop"]
		port = self.config["portPop"]
		keyfile = self.config["keyfile"]
		certfile = self.config["certfile"]
		user = self.config["user"]
		passwd = self.config["passwd"]
		ssl = self.config["ssl"]
		delete = self.config["delete"]
		ruta = os.path.join(path,user,"Entrada")
		debug.info("Solicitando conexion POP3")
		t=conexionPop3(host, port, keyfile, certfile, user, passwd, ssl, delete, ruta)
		t.start()
		debug.info("Solicitando conexion SMTP")
		t2=salida(os.path.join(path,user),self.config)
		t2.start()
		#popDescarga(host, port, keyfile, certfile, user, passwd, ssl, delete, path)

	def newPage(self):
		marco = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		barra = self.headerMail()
		areaCorreo = Gtk.Box(spacing=10)


		listaCap = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		listaCap.add(self.listaCarpetas(self.user))
		areaViewCorreo = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		listaCorreo = Gtk.Box(spacing=10)
		self.listaM = self.listaMail(self.user[0],'Entrada')
		listaCorreo.add(self.listaM)
		viewCorreo = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
		self.visorCo = self.visorCorreo()
		viewCorreo.pack_start(self.visorCo, True, True, 0)

		areaViewCorreo.pack_start(listaCorreo, False, True, 0)
		areaViewCorreo.pack_start(viewCorreo, True, True, 0)

		areaCorreo.add(listaCap)
		areaCorreo.add(areaViewCorreo)

		marco.pack_start(barra, False, False, 0)
		marco.pack_end(areaCorreo, True, True, 0)
		return marco

	def cuerpoDk(self,valores,op):
		bodyBuffer=self.cuerpo.get_buffer()
		start_iter = bodyBuffer.get_start_iter()
		end_iter = bodyBuffer.get_end_iter()
		text = bodyBuffer.get_text(start_iter, end_iter, True) 
		firma=text.find("------SSE Cipher------")
		text= text[:firma]
		debug.debug("Mensaje cifrado: "+text)
		descifrado=SSE.Ek_din.descifrar(text,valores,op)
		try:
			aux=descifrado.decode("utf8")
			buf = Gtk.TextBuffer()
			debug.debug("Decodificacion en utf-8")
			buf.set_text(aux.encode("utf8"))
			self.cuerpo.set_buffer(buf)
		except Exception, e:
			debug.error("Error al descifrar")
			dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
				Gtk.ButtonsType.CANCEL, "Error al descifrar")
			dialog.format_secondary_text(
				"El CAPTCHA fue ingresado incorrectamente")
			dialog.run()
			dialog.destroy()



class ventanaCaptcha(Gtk.Window):
	
	def __init__(self,ventana,despliegue):
		self.ventana = ventana
		self.ruta=despliegue[0]
		self.archivos=despliegue[1]
		self.op=despliegue[2]
		Gtk.Window.__init__(self, title="Cliente de Correos")
		self.set_border_width(4)
		self.set_default_size(500,300)
		self.add(self.viewCAPTCHAS())
		self.show_all()

	def descifrado(self, button):
		debug.info('Busqueda del valor del CAPTCHA')
		for c in self.box1.get_children():
			for x in c.get_children():
				if isinstance(x,Gtk.Entry):
					debug.debug("Imagen CAPTCHA : "+x.get_name())
					valor=x.get_text()
		debug.debug('Valor del CAPTCHA : '+valor)
		if valor=="":
			debug.error('Valor vacio del CAPTCHA')
			dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
				Gtk.ButtonsType.CANCEL, "Error en el CAPTCHA")
			dialog.format_secondary_text(
				"Resolver el CAPTCHA")
			dialog.run()
			dialog.destroy()
		else:
			debug.info('Inicia decifrado del mensaje')
			self.ventana.cuerpoDk(valor,self.op)

	def descifrado2(self, button):
		valor=[]
		debug.info('Busqueda de los valores del CAPTCHAS')
		for c in self.box1.get_children():
			for x in c.get_children():
				if isinstance(x,Gtk.Entry):
					debug.debug("Imagen CAPTCHA : "+x.get_name())
					aux=x.get_text()
					debug.debug("Valor del CAPTCHA : "+aux)
					if aux!="":
						valor.append([self.archivos[x.get_name()],x.get_text()])
		for c in self.box2.get_children():
			for x in c.get_children():
				if isinstance(x,Gtk.Entry):
					debug.debug("Imagen CAPTCHA : "+x.get_name())
					aux=x.get_text()
					debug.debug("Valor del CAPTCHA : "+aux)
					if aux!="":
						valor.append([self.archivos[x.get_name()],x.get_text()])
		for c in self.box3.get_children():
			for x in c.get_children():
				if isinstance(x,Gtk.Entry):
					debug.debug("Imagen CAPTCHA : "+x.get_name())
					aux=x.get_text()
					debug.debug("Valor del CAPTCHA : "+aux)
					if aux!="":
						valor.append([self.archivos[x.get_name()],x.get_text()])
		debug.debug('Valores de los CAPTCHA : '+str(valor))
		if len(valor)==0:
			dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
				Gtk.ButtonsType.CANCEL, "Error en el CAPTCHA")
			dialog.format_secondary_text(
				"Resolver el CAPTCHA")
			dialog.run()
			dialog.destroy()
		else:
			self.ventana.cuerpoDk(valor,self.op)

	def viewCAPTCHAS(self):
		debug.info('Cargando imagenes CAPTCHAS')
		marco = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		scrol = Gtk.ScrolledWindow()
		scrol.set_hexpand(True)
		boxGen=Gtk.VBox(False,0)
		boxGen.set_spacing(10)
		boxGen.set_border_width(10)
		separator = Gtk.HSeparator()
		separator.set_size_request(400, 5)
		separator2 = Gtk.HSeparator()
		separator2.set_size_request(400, 5)
		self.box1=Gtk.HBox(False,0)
		boxGen.pack_start(self.box1,False,False,0)
		boxGen.pack_start(separator, False, True, 5)
		self.box2=Gtk.HBox(False,0)
		boxGen.pack_start(self.box2,False,False,0)
		boxGen.pack_start(separator2, False, True, 5)
		self.box3=Gtk.HBox(False,0)
		boxGen.pack_start(self.box3,False,False,0)
		box4=Gtk.HBox(False,0)
		descifrado= Gtk.Button(label="Descifrar")
		if isinstance(self.archivos,dict):
			debug.info('Despliegue de multiples imagenes CAPTCHAS')
			index=0
			for img in self.archivos.keys():
				debug.debug('Despliegue de la imagen : '+img)
				self.set_default_size(700,400)
				aux = Gtk.VBox(False,0)
				texto = Gtk.Entry(name=img)
				image = Gtk.Image()
				rutaImg=os.path.join(self.ruta,img)
				debug.debug('Ruta de la imagen : '+rutaImg)
				image.set_from_file(rutaImg)
				image.show()
				aux.pack_start(image,False,False,0)
				aux.pack_end(texto,False,False,0)
				if index<2:
					self.box1.pack_start(aux,False,False,0)
				if index<4:
					self.box2.pack_start(aux,False,False,0)
				else:
					self.box3.pack_start(aux,False,False,0)
				index+=1
			descifrado.connect("clicked", self.descifrado2)
		else:
			debug.info('Despliegue de una imagen CAPTCHA')
			for img in self.archivos:
				debug.debug('Despliegue de la imagen: '+img)
				aux = Gtk.VBox(False,0)
				texto = Gtk.Entry(name=img)
				image = Gtk.Image()
				rutaImg=os.path.join(self.ruta,img)
				debug.debug('Ruta de la imagen: '+rutaImg)
				image.set_from_file(rutaImg)
				image.show()
				aux.pack_start(image,False,False,0)
				aux.pack_end(texto,False,False,0)
				self.box1.pack_start(aux,False,False,0)
			descifrado.connect("clicked", self.descifrado)

		box4.pack_end(descifrado,False,False,0)
		marco.pack_start(boxGen,False,False,0)
		marco.pack_start(box4,False,False,0)
		scrol.add(marco)
		return scrol

class configView(Gtk.Window):

	def __init__(self):
		Gtk.Window.__init__(self, title="Configuracion")
		self.set_border_width(4)
		self.set_default_size(500, 600)
		self.add(self.viewConfig())
		self.show_all()
	
	def viewConfig(self):
		marco = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		marco.pack_start(Gtk.Label("Servidor Smtp"),False,False,0)
		self.servidorSmtp=Gtk.Entry()
		marco.pack_start(self.servidorSmtp,False,False,0)
		marco.pack_start(Gtk.Label("Puerto Smtp"),False,False,0)
		self.puertoSmtp=Gtk.Entry()
		marco.pack_start(self.puertoSmtp,False,False,0)
		marco.pack_start(Gtk.Label("Servidor Pop"),False,False,0)
		self.servidorPop=Gtk.Entry()
		marco.pack_start(self.servidorPop,False,False,0)
		marco.pack_start(Gtk.Label("Puerto Pop"),False,False,0)
		self.puertoPop=Gtk.Entry()
		marco.pack_start(self.puertoPop,False,False,0)
		marco.pack_start(Gtk.Label("Usuario de Correo Electronico"),False,False,0)
		self.usuCorreoElec=Gtk.Entry()
		marco.pack_start(self.usuCorreoElec,False,False,0)
		marco.pack_start(Gtk.Label("Contrasena de Correo Elecctronico"),False,False,0)
		self.contraCorreoElec=Gtk.Entry()
		self.contraCorreoElec.set_visibility(False)
		marco.pack_start(self.contraCorreoElec,False,False,0)
		marco.pack_start(Gtk.Label("Conexion POP SSL"),False,False,0)
		self.conexSSL=Gtk.Switch()
		self.conexSSL.set_active(False)
		marco.pack_start(self.conexSSL,False,False,0)
		marco.pack_start(Gtk.Label("Usuario del Servidor de CAPTCHAS"),False,False,0)
		self.usuSerCAPTCHA=Gtk.Entry()
		marco.pack_start(self.usuSerCAPTCHA,False,False,0)
		marco.pack_start(Gtk.Label("Contrasena del Servidor de CAPTCHAS"),False,False,0)
		self.contraSerCAPTCHA=Gtk.Entry()
		self.contraSerCAPTCHA.set_visibility(False)
		marco.pack_start(self.contraSerCAPTCHA,False,False,0)
		marco.pack_start(Gtk.Label("Activar Esquema de Secreto Compartido"),False,False,0)
		self.SSE=Gtk.Switch()
		self.SSE.set_active(False)
		marco.pack_start(self.SSE,False,False,0)
		boton = Gtk.Button(label="Activar")
		boton.connect("clicked", self.Activar)
		marco.pack_start(boton,False,False,0)
		return marco
	def Activar(self,button):
		debug.debug("Conexion con el servidor de CAPTCHAS")
		dic={}
		dic["nombre"]=self.usuSerCAPTCHA.get_text()
		dic["contrasena"]=self.contraSerCAPTCHA.get_text()
		dic["correo_electronico"]=self.usuCorreoElec.get_text()
		if http.httpAltaUsu(dic):
			debug.info("Conexion exitosa con el servidor de CAPTCHAS")
			debug.debug("Conexion POP3 con el servidor de correos")
			disc={}
			disc["host"]=self.servidorPop.get_text()
			disc["port"]=self.puertoPop.get_text()
			disc["keyfile"]="./Seguridad/server2048.key"
			disc["certfile"]="./Seguridad/server2048.pem"
			disc["user"]=self.usuCorreoElec.get_text()
			disc["passwd"]=self.contraCorreoElec.get_text()
			disc["ssl"]=self.conexSSL.get_active()
			if validarPop(disc):
				debug.info("Conexion POP3 exitosa con el servidor de correos")
				debug.debug("Conexion SMTP con el servidor de correos")
				disc["host"]=self.servidorSmtp.get_text()
				disc["port"]=self.puertoSmtp.get_text()
				disc["ssl"]=False
				if validarSmtp(disc):
					debug.info("Conexion SMTP exitosa con el servidor de correos")
					disc={}
					disc["hostSmtp"]=self.servidorSmtp.get_text()
					disc["portSmtp"]=int(self.puertoSmtp.get_text())
					disc["hostPop"]=self.servidorPop.get_text()
					disc["portPop"]=int(self.puertoPop.get_text())
					disc["keyfile"]="./Seguridad/server2048.key"
					disc["certfile"]="./Seguridad/server2048.pem"
					disc["user"]=self.usuCorreoElec.get_text()
					disc["passwd"]=self.contraCorreoElec.get_text()
					disc["ssl"]=self.conexSSL.get_active()
					disc["delete"]=0
					disc["SSE"]=self.SSE.get_active()
					disc["nombre"]=self.usuSerCAPTCHA.get_text()
					disc["passwdSSE"]=self.contraSerCAPTCHA.get_text()
					lista=open("config.json","w")	
					lista.write(json.dumps(disc))
					lista.close
					if not os.path.exists(os.path.join("./Usuarios",self.usuCorreoElec.get_text())):
						debug.debug("Crear carpetas")
						usu = os.path.join("./Usuarios",self.usuCorreoElec.get_text())
						os.mkdir(usu)
						os.mkdir(os.path.join(usu,"Entrada"))
						aux=open(os.path.join(usu,"Entrada","lista.json"), "a+")
						aux.write('{}')
						aux.close()
						os.mkdir(os.path.join(usu,"Enviados"))
						aux=open(os.path.join(usu,"Enviados","lista.json"), "a+")
						aux.write('{}')
						aux.close()
						os.mkdir(os.path.join(usu,"Salida"))
						aux=open(os.path.join(usu,"Salida","lista.json"), "a+")
						aux.write('{}')
						aux.close()

					debug.info('Cargando configuracion')
					win = MyWindow(disc)
					win.connect("delete-event", Gtk.main_quit)
					win.show_all()
				else:
					debug.error("Conexion SMTP fallida, verificar configuracion")
					dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
					Gtk.ButtonsType.CANCEL, "Error en el servidor SMTP")
					dialog.format_secondary_text(
						"No se logro estableser comunicacion con el servidor SMTP, verificar los datos ingresados")
					dialog.run()
					dialog.destroy()
			else :
				debug.error("Conexion POP3 fallida, verificar configuracion")
				dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
				Gtk.ButtonsType.CANCEL, "Error en el servidor POP")
				dialog.format_secondary_text(
					"No se logro estableser comunicacion con el servidor POP, verificar los datos ingresados")
				dialog.run()
				dialog.destroy()
		else:
			debug.error("Conexion con el servidor de CAPTCHAS fallida, verificar configuracion")
			dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
			Gtk.ButtonsType.CANCEL, "Error en el servidor de CAPTCHAS")
			dialog.format_secondary_text(
				"Ocurrio un error en el registro como usuario en el servidor de CAPTCHAS")
			dialog.run()
			dialog.destroy()
def setup_logger(logger_name, log_file, level=logging.INFO):
	l = logging.getLogger(logger_name)
	formatter = logging.Formatter('%(asctime)s : %(name)s : %(levelname)s : %(message)s')
	fileHandler = logging.FileHandler(log_file, mode='w')
	fileHandler.setFormatter(formatter)
	streamHandler = logging.StreamHandler()
	streamHandler.setFormatter(formatter)

	l.setLevel(level)
	l.addHandler(fileHandler)
	l.addHandler(streamHandler)	
arcLogDebug="./logs/debug"+time.strftime('%d-%m-%y %H:%M:%S')+".log"
#arcLogError="./logs/error"+time.strftime('%d-%m-%y %H:%M:%S')+".log"
#arcLogDebug="./logs/debug.log"
setup_logger('debug', arcLogDebug, logging.DEBUG)
debug = logging.getLogger('debug')

win=None
if not os.path.exists("config.json"):
	debug.info('Inicia Configuracion')
	win = configView()
	win.connect("delete-event", Gtk.main_quit)
	win.show_all()
	Gtk.main()

else:
	debug.info('Inicia Aplicacion')
	jsonCorreo = open("config.json","r")
	jsonLectura = jsonCorreo.readline()
	jsonCorreo.close()
	configuracion = json.loads(jsonLectura)
	debug.info('Cargando configuracion')
	win = MyWindow(configuracion)
	win.connect("delete-event", Gtk.main_quit)	
	win.show_all()
	Gtk.main()
