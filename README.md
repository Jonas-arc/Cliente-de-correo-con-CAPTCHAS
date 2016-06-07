Instalación del Cliente de correo electrónico.

La instalación del entorno gráfico GNOME 3 se realizo en un sistema operativo XUBUN-
TU 15.1 y XUBUNTU 14.1. A continuación se explica los pasos a seguir para la instalación
de este entorno gráfico.

1. Se abre una terminal del sistema operativo.
2. Se ingresan los siguientes comandos a la terminal para instalar los repositorios de descarga.
1. sudo add−apt−repository ppa : gnome3−team/gnome3
2. sudo add−apt−repository ppa : gnome3−team/gnome3−staging
3. Posteriormente se ingresa el siguiente comando a la terminal para actualizar los repositorios de descargas.
1. sudo apt−get update
4. Una vez terminada la actualización se ingresa este último comando para terminar con la instalación del entorno gráfico GNOME 3.
1. sudo apt−get dist−upgrade
5. Una vez que la instalación termine se reinicia el equipo para activar el entorno gráfico GNOME 3.
6. Instalar JHBuild del siguiente tutorial.
1. https://developer.gnome.org/jhbuild/unstable/getting-started.html.es
7. Al termino del la instalación de JHBuild se abre una terminal del sistema operativo.
8. Se ingresan los siguientes comandos.
1. $ jhbuild build pygobject
2. $ jhbuild build gtk+
3. $ jhbuild shell
