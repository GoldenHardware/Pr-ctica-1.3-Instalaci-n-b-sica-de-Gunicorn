# Práctica 1.3: instalación básica de Gunicorn

Módulo: Despliegue de aplicaciones web (2º DAW)

Alumno: Javier Doñoro Garcia

Fecha: 18 / 11 / 2026

## Introducción

En esta práctica he instalado el servidor de aplicaciones Gunicorn en mi máquina virtual con Ubuntu Server 24.04 y lo he usado para arrancar un backend hecho con FastAPI. He creado un entorno virtual con Python 3.13, he instalado las dependencias desde un requirements.txt y he comprobado con curl que los endpoints /health, /version y /ping responden en el puerto 8000.

Todo lo he hecho conectado a la máquina por SSH. El proyecto está en la carpeta ~/practica-1.3 con esta estructura:

```
practica-1.3/
  app/
    __init__.py
    main.py
  docs/
    gunicorn.md
  requirements.txt
  venv/
```

## Paso 1. Comprobar la versión de Python

Primero miré qué versión de Python traía el sistema:

```bash
python3 --version
```

Me salió Python 3.12.3, que es la que trae Ubuntu 24.04. La práctica pide la 3.13 o superior, así que tuve que instalarla aparte.

Captura 1: versión de Python que trae Ubuntu (3.12.3).

![Captura 1](img/captura1.png)

## Paso 2. Instalar Python 3.13

Python 3.13 no está en los repositorios oficiales de Ubuntu 24.04, así que añadí el repositorio deadsnakes, que tiene otras versiones de Python, e instalé la 3.13 con el paquete venv para poder crear entornos virtuales:

```bash
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.13 python3.13-venv
python3.13 --version
```

La versión instalada es la 3.13.18. La 3.12 del sistema sigue instalada, porque Ubuntu la usa para sus propias herramientas, y por eso la nueva se llama con python3.13.

Captura 2: Python 3.13.18 instalado.

![Captura 2](img/captura2.png)

## Paso 3. Crear la carpeta del proyecto y el entorno virtual

Creé la carpeta del proyecto con las subcarpetas app y docs, entré en ella y creé el entorno virtual con Python 3.13:

```bash
mkdir -p ~/practica-1.3/app ~/practica-1.3/docs
cd ~/practica-1.3
python3.13 -m venv venv
source venv/bin/activate
python --version
which python
```

Al activar el entorno el prompt empieza por (venv). Dentro del entorno, python ya es la versión 3.13 y which python apunta a ~/practica-1.3/venv/bin/python, así que todo lo que instale con pip se queda dentro del proyecto y no toca el Python del sistema.

Captura 3: entorno virtual activado con Python 3.13.

![Captura 3](img/captura3.png)

## Paso 4. Instalar las dependencias

Creé el fichero requirements.txt con las tres librerías que necesito: FastAPI para la aplicación, Uvicorn para el soporte ASGI y Gunicorn como servidor de aplicaciones.

```bash
tee requirements.txt <<'EOF'
fastapi
uvicorn[standard]
gunicorn
EOF
```

Después actualicé pip e instalé todo desde el fichero:

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip list | grep -Ei "fastapi|uvicorn|gunicorn"
gunicorn --version
```

Se instalaron fastapi 0.165.0, gunicorn 27.0.1 y uvicorn 0.54.0.

Captura 4: paquetes instalados en el entorno virtual y versión de Gunicorn.

![Captura 4](img/captura4.png)

## Paso 5. Crear la aplicación

Creé el fichero vacío app/__init__.py para que Python trate la carpeta app como un paquete. Así funciona la ruta app.main:app que se le pasa a Gunicorn. Luego creé app/main.py con una API sencilla en FastAPI con los tres endpoints que pide la práctica:

```bash
touch app/__init__.py
tee app/main.py <<'EOF'
from fastapi import FastAPI

app = FastAPI(title="API practica 1.3", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"app": "API practica 1.3", "version": app.version}


@app.get("/ping")
def ping():
    return {"message": "pong"}
EOF
cat app/main.py
```

Captura 5: contenido de app/main.py.

![Captura 5](img/captura5.png)

## Paso 6. Arrancar Gunicorn

Con el entorno virtual activado y desde ~/practica-1.3 arranqué Gunicorn:

```bash
gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
```

En la salida se ve "Listening at: http://127.0.0.1:8000", "Using worker: uvicorn.workers.UvicornWorker", "Booting worker" y "Application startup complete", así que Gunicorn arrancó bien con el worker de Uvicorn. Se queda ocupando la terminal mientras está en marcha.

Captura 6: Gunicorn arrancado escuchando en 127.0.0.1:8000.

![Captura 6](img/captura6.png)

## Paso 7. Probar los endpoints con curl

Abrí una segunda conexión SSH a la máquina y probé los tres endpoints. Usé -i para ver también las cabeceras:

```bash
curl -i http://127.0.0.1:8000/health
curl -i http://127.0.0.1:8000/version
curl -i http://127.0.0.1:8000/ping
```

Los tres devuelven HTTP/1.1 200 OK, la cabecera content-type: application/json y un JSON válido:

- /health: {"status":"ok"}
- /version: {"app":"API practica 1.3","version":"1.0.0"}
- /ping: {"message":"pong"}

Además la cabecera server es uvicorn, con lo que se ve que quien responde es mi aplicación a través de Gunicorn y no la página por defecto de Apache, que está en el puerto 80 y devuelve HTML.

Captura 7: respuestas de /health, /version y /ping con código 200 y JSON.

![Captura 7](img/captura7.png)

## Paso 8. Comprobar en qué dirección escucha

Para ver en qué dirección y puerto está escuchando Gunicorn usé ss:

```bash
ss -tlnp | grep 8000
```

Sale LISTEN en 127.0.0.1:8000 con los procesos de gunicorn (el proceso principal y su worker). No escucha en 0.0.0.0, así que solo se puede llegar a él desde la propia máquina.

Captura 8: Gunicorn escuchando solo en 127.0.0.1:8000.

![Captura 8](img/captura8.png)

## Paso 9. Parar Gunicorn

En la terminal donde estaba Gunicorn pulsé Ctrl+C para pararlo. Después volví a probar el endpoint de salud:

```bash
curl http://127.0.0.1:8000/health
```

Ahora curl da el error "curl: (7) Couldn't connect to server", porque ya no hay nada escuchando en el puerto 8000.

Captura 9: Gunicorn parado y curl sin poder conectar.

![Captura 9](img/captura9.png)

## Qué hace la orden de arranque

```bash
gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
```

- app.main:app: le dice a Gunicorn qué aplicación tiene que cargar. La parte de antes de los dos puntos es el módulo (el fichero app/main.py) y la de después es el objeto dentro de ese fichero (la variable app = FastAPI(...)).
- --worker-class uvicorn.workers.UvicornWorker: indica el tipo de worker. Gunicorn crea uno o varios procesos hijo, los workers, que son los que atienden las peticiones. Con esta opción cada worker ejecuta Uvicorn por dentro.
- --bind 127.0.0.1:8000: la dirección IP y el puerto donde escucha. 127.0.0.1 es la interfaz de loopback y 8000 el puerto.

### Por qué UvicornWorker es obligatorio (WSGI y ASGI)

WSGI es el estándar clásico de Python para comunicar un servidor con una aplicación web. Es síncrono, porque cada petición ocupa al worker hasta que termina, y es el que usan frameworks como Flask o Django. Gunicorn por defecto usa workers WSGI (el worker sync).

ASGI es el estándar más nuevo, asíncrono, que permite atender muchas peticiones a la vez con async/await y también cosas como WebSockets. FastAPI es una aplicación ASGI.

Si arranco Gunicorn sin el --worker-class, intenta llamar a la aplicación de FastAPI como si fuera WSGI y falla, porque espera otra interfaz. UvicornWorker hace de puente: Gunicorn gestiona los procesos y Uvicorn, dentro de cada worker, habla ASGI con FastAPI. Por eso es obligatorio en este caso.

### Por qué Gunicorn y no solo Uvicorn

Uvicorn por sí solo ya podría servir la aplicación, pero Gunicorn añade la gestión de procesos que hace falta en producción:

- Puede lanzar varios workers (opción -w) y aprovechar varios núcleos de CPU.
- Si un worker se cuelga o se muere, el proceso principal lo detecta y arranca otro.
- Tiene timeouts para matar workers que tardan demasiado.
- Se puede recargar la configuración o reiniciar los workers sin cortar el servicio, mandándole señales como HUP.

Gunicorn se encarga de que el servicio sea robusto y Uvicorn aporta el soporte ASGI, así que juntos tenemos lo mejor de los dos.

## Servidor web y servidor de aplicaciones

Apache, que instalé en otras prácticas, es un servidor web: atiende las conexiones HTTP de los clientes, sirve ficheros estáticos (HTML, CSS, imágenes), gestiona HTTPS y puede hacer de proxy inverso. No ejecuta código Python.

Gunicorn es un servidor de aplicaciones: carga el código Python de la aplicación y lo ejecuta en sus workers para generar las respuestas dinámicas, en este caso los JSON de la API.

En un despliegue normal se usan los dos: Apache recibe las peticiones de fuera y las que van a la API se las pasa por proxy a Gunicorn en 127.0.0.1:8000.

## 127.0.0.1, localhost y 0.0.0.0

- 127.0.0.1 es la dirección de loopback. Solo se puede conectar desde la propia máquina, no desde la red.
- localhost es un nombre que normalmente se resuelve a 127.0.0.1 (o a ::1 en IPv6), así que a efectos de acceso es lo mismo que 127.0.0.1, solo que pasa por la resolución de nombres.
- 0.0.0.0 significa escuchar en todas las interfaces de la máquina, así que el servicio sería accesible desde cualquier equipo de la red que llegue a ella.

Gunicorn solo escucha en 127.0.0.1 porque no tiene que estar expuesto directamente. El que da la cara al exterior es Apache, que además se encarga de HTTPS, de los estáticos y de las cabeceras de seguridad. Si pusiera 0.0.0.0, cualquiera podría saltarse Apache y atacar directamente al backend. En la Captura 8 se ve que efectivamente escucha en 127.0.0.1:8000.

## Cómo arrancar, parar y depurar

Para arrancarlo:

```bash
cd ~/practica-1.3
source venv/bin/activate
gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
```

Para pararlo, Ctrl+C en la terminal donde está corriendo. Para salir del entorno virtual, deactivate.

Errores comunes:

- gunicorn: command not found: no está activado el entorno virtual. Se soluciona con source venv/bin/activate.
- ModuleNotFoundError: No module named 'app': no estoy en la carpeta ~/practica-1.3 o falta el fichero app/__init__.py.
- Address already in use: ya hay otro proceso en el puerto 8000, por ejemplo un Gunicorn anterior que no se paró. Se mira con ss -tlnp | grep 8000 y se para ese proceso o se usa otro puerto.
- TypeError al hacer una petición: se ha arrancado sin --worker-class uvicorn.workers.UvicornWorker y Gunicorn trata la aplicación como WSGI.
- curl: (7) Couldn't connect to server: Gunicorn no está arrancado o está escuchando en otra dirección o puerto.

## Conclusión

He conseguido instalar Python 3.13 con un entorno virtual, instalar las dependencias desde requirements.txt y arrancar Gunicorn con el worker de Uvicorn. Los endpoints /health, /version y /ping responden con 200 y JSON en 127.0.0.1:8000. También he entendido por qué FastAPI necesita un worker ASGI y por qué el servidor de aplicaciones solo escucha en local, detrás del servidor web.
