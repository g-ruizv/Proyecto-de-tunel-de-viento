# FanWallInterface

En este documento estara contenido la informacion de todo lo necesario para ejecutar la interfaz grafica, el tunel de viento, sus configuraciones y demas caracteristicas

## Ejecucion de la interfaz

## Prerrequisitos y Configuración Inicial

Antes de ejecutar la interfaz, es necesario tener configurados los siguientes servicios externos:

### 1. Variables de Entorno (Archivo `.env`)
El programa busca credenciales sensibles en un archivo llamado `.env` en la raíz del proyecto. **Si este archivo no existe, la aplicación no iniciará.**

Crea un archivo `.env` y pega lo siguiente (ajusta los valores a tu equipo):

```env
SECRET_KEY='clave_secreta_para_flask'
DATABASE_POSTGRES_URL='postgresql://postgres:tu_contraseña@localhost:5432/tunel_viento_db'
```

En primer lugar tenemos que asegurarnos que estamos en la carpeta indicada para esto inicia en la carpeta en vscode o si estas afuera de la carpeta ejecuta el siguiente comando

```bash
cd FanWallInterface-copia
```

Posteriormente, lo que hay que realizar es una maquinavirtual para que el programa no interfiera con otras versiones instaladas de programas, para esto tenemos que tener en cuenta si esta creado esta maquina virtual, por defecto en el repositorio si esta creada, por lo cual solo necesitamos ocupar el siguiente comando para activar la maquina virtual.

```bash
venv\Scripts\activate
```
si queremos desactivarla ocupamos el siguiente comando

```bash
deactivate
```
Si por error borramos la carpeta venv, que es donde esta la maquina virtual, para crearla solo necesitamos el siguiente comando.

```bash
py -3.11 -m venv venv
```

Es de vital importancia que la version de python sea 3.11, porque de caso contrario, se van a presentar variados errores por la interferencia de las versiones de los programas. Para que no pase esto, despues de activar la maquina virtual es necesario ejecutar el siguiente comando para tener instalado los siguientes requerimientos.

```bash
pip install -r requirements.txt
```

Con la instruccion anterior lista, ahora se puede ejecutar todo el programa de la interfase con el siguiente comando

```bash
python run.py
```

Despues de la ejecucion de este hay que esperar unos segundos hasta que el servidor este conectado y nos de el siguiente mensaje

```bash
Connected to MQTT broker
MQTT Started
Connected with result code 0
```

Posteriormente a este mensaje podemos ingresar a la pagina de la interfaz que esta contenida en el siguiente link

[Link de la interfaz del tunel de viento](http://localhost:5000/register)


## Estructura del repositorio
```
FanWallInterface-copia/
├── app/
│   ├── __init__.py           # Inicialización de Flask, SQLAlchemy, SocketIO
│   ├── models.py             # Modelos de base de datos (User, Experiment, etc.)
│   ├── routes.py             # Vistas y endpoints de la aplicación
│   ├── mqtt_client.py        # Cliente MQTT y manejo de mensajes
│   ├── services/
│   │   ├── serial_service.py # Comunicación serie con Arduino
│   │   └── data_service.py   # Procesamiento y almacenamiento de datos
│   ├── templates/            # Plantillas HTML (Jinja2)
│   └── static/               # Archivos CSS, JS, imágenes
├── migrations/               # Migraciones de base de datos (Flask-Migrate)
├── venv/                     # Entorno virtual (no incluido en repo)
├── requirements.txt          # Dependencias del proyecto
├── run.py                    # Punto de entrada de la aplicación
├── .env                      # Variables de entorno (no incluido en repo)
└── README.md                 # Este documento
```
