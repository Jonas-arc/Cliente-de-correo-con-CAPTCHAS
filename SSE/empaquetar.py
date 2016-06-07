from Ek_din import cifrar
from subprocess import call
import types
import os
from os import path

def listFiles(folder):
	return [d for d in os.listdir(folder) if path.isfile(path.join(folder, d))]

def empaquetar(body,asunto,op):
	s=cifrar(body,asunto,op)
	asunto=asunto.replace(" ","_")
	disc={}
	#print(s[1])
	ass=asunto+".zip"
	if type(s[1])==types.StringType:
		zi=call("zip -r "+ass+" "+s[1], shell=True)
		mv=call("mv ./"+ass+" ./CAPTCHAS", shell=True)
		rmm=call("rm -rf "+s[1], shell=True)
		return (s[0],"./CAPTCHAS/"+ass)
	else:
		zi=call("zip -r "+ass+" "+s[1][1], shell=True)
		mv=call("mv ./"+ass+" ./CAPTCHAS", shell=True)
		rmm=call("rm -rf "+s[1][1], shell=True)
		return (s[0],"./CAPTCHAS/"+ass)
