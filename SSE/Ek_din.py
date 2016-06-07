from Crypto.Hash import SHA256
import os
import random
import base64
import json
from random import randrange
from map import mapeoBtoI
from map import mapeoItoB
from image import ImageCaptcha
from Crypto.Cipher import AES

def isprime(n): 
	'''chequear si un entero es primo''' 
	# chequear que la entrada sea un entero positivo 
	n = abs(int(n)) 
	# 0 y 1 no son primos 
	if n < 2: 
		return False 
	# 2 es el unico primo par 
	if n == 2:  
		return True	 
	# El resto de pares no son primos 
	if not n & 1:  
		return False 
	#El rango comienza en 3 y solo necesita subir hasta la raiz cuadrada de n  
	# para todos los impares 
	for x in range(3, int(n**0.5)+1, 2): 
		if n % x == 0: 
			return False 
	return True 
def primoSig(num):
	buscar=True
	while buscar:
		if isprime(num):
			buscar=False
		else:
			num+=1
	return num
def crearSemilla(tam):
	r=0
	semilla=""
	for i in range(tam):
		r=random.randrange(64)
		semilla=semilla+str(mapeoItoB(r))
	return semilla

def crearLlave(semilla1):
	aux=""
	llave=""
	hash = SHA256.new()
	hash.update(semilla1)
	aux=hash.digest()
	llave = ""
	for i  in range(16):
		llave=llave+aux[i]
	return llave

def crearCAPTCHA(op,semilla2,asunto):
	imagen=""
	aux=""
	ax=[]
	xa=""
	s=[]
	c=0
	asunto=asunto.replace(" ","_")
	os.mkdir('./'+asunto+"",0755)
	image = ImageCaptcha(fonts=['./SSE/fon/A1.ttf', './SSE/fon/A1.ttf'])
	if (op==0):
		aux='./'+asunto+'/CAPTCHA00.png'
		image.write(semilla2, aux)
		return './'+asunto
	else:
		for x in semilla2:
			#print(x)
			aux='./'+asunto+'/CAPTCHA'+str(c)+'.png'
			xa='CAPTCHA'+str(c)+'.png'
			ax.append(xa)
			s.append(ax)
			ax=[]
			image.write(x, aux)
			c=c+1
		return (s,'./'+asunto)

def encodeSS(strin):
	bina=""
	aux=""
	for i in range(len(strin)):
		aux=bin(mapeoBtoI(strin[i])).replace("0b","")
		if (len(aux)==6):
			bina=bina+aux
		else:
			while ((len(aux))<6):
				aux="0"+aux
			bina=bina+aux
	return int(str(bina),2)

def decodeSS(strr,w0):
	c=0
	s=""
	capt=""
	letras=[]
	z=bin(strr).replace("0b","")
	while (len(z)<(6*w0)):
		z="0"+z
	for i in z:
		if (c==5):
			c=0
			s=s+i
			letras.append(s)
			s=""
		else:
			c=c+1
			s=s+i
	for j in letras:
		capt=capt+mapeoItoB(int(str(j),2))
	return capt

def eucExt(a,b):
	r = [a,b]
	s = [1,0] 
	i = 1
	q = [[]]
	while (r[i] != 0): 
		q = q + [r[i-1] // r[i]]
		r = r + [r[i-1] % r[i]]
		s = s + [s[i-1] - q[i]*s[i]]
		i = i+1
	return s[i-1]%b

def GenerarPares(p=7,w=5,t=2,k=0):
	pares =[]
	a = [k]
	for aux in range(0,w):
		print(aux)
		pares.append([randrange(p),0])
	print("X->")
	print(pares)
	for aux in range(1,t):
		print(aux)
		a.append(randrange(p))
	print("A->")
	print(a)
#	for aux in range(0,w):
#		suma = k+(a[1]*pares[aux][0])
#		pares[aux][1] = suma%p
	for aux in pares:
		print("suma")
		suma = k
		print(suma)
		for aux2 in range(1,t):
			print("sin ecuacion")
			print(suma)
			suma = (suma+(a[aux2]*(aux[0]**aux2)))%p
			print("con ecuacion")
			print(suma)
		aux[1] =suma
	return pares

def secreto(pares,p):
	suma = 0
#	print("pares")
#	print(pares)
	for aux in pares:
#		print("par")
#		print(aux)
		ind = pares.index(aux)
#		print("index")
#		print(ind)
		lis = pares[:ind] + pares[(ind+1):]
#		print("otros pares")
#		print(lis)
		num=1
		den=1
		for aux2 in lis:
#			print("numerodor")
			num = (num*(aux2[0])*-1)%p
#			print(num)
#			print("denominador")
			den = (den*((aux[0]-aux2[0])%p))%p
#			print(den)
#		print("Euclides")
		den = eucExt(den,p)
#		print(den)
		suma += (den*aux[1]*num)%p
#		print("suma")
#		print(suma)
	return suma%p

def cifrar(body,asunto1,op1=1,ta=5,w1=5,t1=2):
	ruta=""
	salida=""
	if t1>w1:
		salida=""
		ruta=None
		print("w1 < t1")
		return (salida,ruta)
	semilla3=crearSemilla(ta)
	num=0
	cap=[]
	zp=primoSig(2**(6*ta))
	disc={}
	#print(semilla3)
	if (op1==0):
		ruta=crearCAPTCHA(0,semilla3,asunto1)
	else:
		ruta=[]
		num=encodeSS(semilla3)
		pares=GenerarPares(zp,w1,t1,num)
		#print(pares)
		for x in pares:
			cap.append(decodeSS(x[1],w1))
		ruta=crearCAPTCHA(op1,cap,asunto1)
		num=0
		print(cap)
		for x in pares:
			ruta[0][num].insert(0,x[0])
			num=num+1
		for i in ruta[0]:
			disc[i[1]]=i[0]
		print(ruta)
		lista=open(ruta[1]+"/lista.json","w")	
		lista.write(json.dumps(disc))
		lista.close
	k=crearLlave(semilla3)
	obj = AES.new(k, AES.MODE_ECB)
	salida=""
	ax=0
	c=0
	strr=""
	#print len(body)
	while (ax < len(body)):
		while (c<16):
			if (ax>=len(body)):
				strr=strr+" "
			else:
				strr=strr+body[ax]
			c=c+1
			ax=ax+1
			#print str(c) +" " + str(ax) 
		c=0
		#print strr
		ciphertext = obj.encrypt(strr)
		salida=salida+ciphertext
		strr=""
	salida = base64.b64encode(salida)
	return (salida,ruta)

def descifrar(body1,capt1,op2):
	aux=[]
	ax=0
	pares=[]
	zp=0
	
	if (op2==0):
		k=crearLlave(capt1)
	else:
		w=len(capt1[0][1])
		zp=primoSig(2**(6*(len(capt1[0][1]))))
		for x in capt1:
			aux=x
			aux[1]=encodeSS(x[1])
			pares.append(aux)	
		#print(pares)
		ax=secreto(pares,zp)
		#print(ax)
		semilla4=decodeSS(ax,w)
		#print(semilla4)
		k=crearLlave(semilla4)
		#print(k)
	obj = AES.new(k, AES.MODE_ECB)
	salida=""
	ax=0
	c=0
	strr=""
	#print len(body1)
	body1 = base64.b64decode(body1)
	while (ax < len(body1)):
		while (c<16):
			if (ax>=len(body1)):
				strr=strr+" "
			else:
				strr=strr+body1[ax]
			c=c+1
			ax=ax+1
			#print str(c) +" " + str(ax) 
		c=0
		#print strr
		ciphertext = obj.decrypt(strr)
		salida=salida+ciphertext
		strr=""
	return salida
