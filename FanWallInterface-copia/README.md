# FanWallInterface

En este documento estará contenido la información de todo lo necesario para ejecutar la interfaz gráfica, el túnel de viento, sus configuraciones y demás características.

Esta interfaz corresponde al proyecto de FanWallInterface, que fue creado por Sebastian Trillos, cuyo repositorio es el siguiente: [FanWallInterface](https://github.com/elTrillos/FanWallInterface)

## Pre-requisitos

Para la ejecucion del programa es necesario instalar lo siguiente para el correcto funcionamiento de este codigo

### Python 3.11
El proyecto requiere **Python 3.11** específicamente. Otras versiones pueden causar errores de compatibilidad.

Para esto es necesario ir a este link: [python.org/downloads](https://www.python.org/downloads/) y busca "Python 3.11.x" (la última versión de la rama 3.11, por ejemplo 3.11.9).

### Node.js

La interfaz ahora carga todas las librerías CSS/JS desde CDN (Internet), por lo que Node.js no es obligatorio para el funcionamiento básico. Sin embargo, si deseas trabajar sin conexión a Internet o modificar las dependencias, necesitarás Node.js.

Para la instalacion tenemos que ir al siguiente link: [nodejs.org](https://nodejs.org/en)

Ahora bien, para que se muestre de forma correcta la interfaz tenemos que instalar las siguientes dependencias en la carpeta `FanWallInterface-copia`.

```bash
npm install gridstack bootstrap @popperjs/core jquery socket.io-client paho-mqtt
```

Para que funcione bien hay que copiar la carpeta `node_modules/` a `app/static/`.

```bash
Copy-Item -Recurse -Force node_modules app\static\
```

### Variables de Entorno (Archivo `.env`)
El programa busca credenciales sensibles en un archivo llamado `.env` en la raíz del proyecto. **Si este archivo no existe, la aplicación no iniciará.**

Crea un archivo `.env` y pega lo siguiente (ajusta los valores a tu equipo):

```env
SECRET_KEY=clave_secreta_para_flask
FLASK_ENV=development
DATABASE_POSTGRES_URL=postgresql://postgres:tu_contraseña@localhost:5432/tunel_viento_db
DATABASE_URL=postgresql://postgres:tu_contraseña@localhost:5432/tunel_viento_db
PORT=5000
MQTT_BROKER=broker.emqx.io
MQTT_PORT=1883
```

## Ejecución de la interfaz

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

En en el caso que nos de error o no nos de la autorizacion ponemos en el terminal lo siguiente.

```bash
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
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
## Uso de la interfaz

Una vez autenticado, accederás a la pantalla principal donde podrás:

-Poner imagen de la interfaz

### Panel izquierdo

- Get controllers: Solicita a los ESP32 que publiquen su ID. Los módulos detectados aparecerán en la cuadrícula.
- Add Multiple Controllers: Permite añadir varios controladores manualmente.
- Edit controller: Cambia el nombre o propiedades de un módulo.
- Create preset: Abre un modal para guardar una nueva línea de tiempo (ver formato de presets más abajo).
- Load preset: Abre un modal para seleccionar y ejecutar un preset.

### Area central

Los módulos se muestran como celdas arrastrables que se pueden reorganizar para definir la disposición física de los ventiladores en el túnel. Cada celda contiene un slider para controlar la velocidad (0–100 %).

### Barra superior derecha

- Configuration: Muestra la configuración actualmente cargada.
- Select Configuration: Desplegable para cargar disposiciones guardadas. 
- Create New: Guarda la disposición actual con un nombre.
- Save: Actualiza la configuración activa.
- Logout: Cierra sesión.

### Configuración de la cuadrícula

La disposición se guarda como una matriz 2×2 de números enteros (0 para celda vacía). Los números corresponden a los IDs numéricos de los módulos.

Ejemplo de matriz:

- imagen de referencia de la cuadricula

**Para crear una configuración:**
1. Arrastra los controladores desde la barra lateral o usa "Get controllers".
2. Coloca cada controlador en la celda deseada.
3. Haz clic en "Create New", escribe un nombre y guarda.
4. Para usarla, selecciona la configuración en el desplegable y haz clic en "Load Configuration".

### Creacion de presets

Un preset es un objeto JSON con dos partes:

- `frames`: contiene la matriz de disposición (solo para validación, debe coincidir con la configuración cargada).

- `timeline`: lista de pasos, cada paso con time (segundos de espera después de aplicar el paso) y velocidades para cada módulo (claves `"1"`, `"2"`, `"3"`).

```json
{
  "frames": [
    { "matrix": [[0, 3], [1, 2]] }
  ],
  "timeline": [
    { "time": 0, "1": 0, "2": 0, "3": 0 },
    { "time": 2, "1": 30, "2": 30, "3": 30 },
    { "time": 2, "1": 70, "2": 70, "3": 70 },
    { "time": 2, "1": 0, "2": 0, "3": 0 }
  ]
}
```
**Notas sobre el tiempo:** El valor `time` es el intervalo de espera en segundos después de aplicar ese paso. Por lo tanto, la secuencia anterior dura 0 + 2 + 2 + 2 = 6 segundos en total.

Para guardar un preset:

1. Abre el modal "Create preset".
2. Asigna un nombre.
3. Pega el JSON en el área de texto.
4. Haz clic en "Create".

### Cargar y ejecutar un preset

1. Abre el modal "Load preset".
2. Selecciona el preset deseado del desplegable.
3. Haz clic en "Load preset". Verás que el nombre del preset aparece en la interfaz.
4. Asegúrate de tener una configuración cargada (el sistema te lo recordará si no).
5. Haz clic en "Start" para iniciar la secuencia. Puedes detenerla en cualquier momento con "Stop".

