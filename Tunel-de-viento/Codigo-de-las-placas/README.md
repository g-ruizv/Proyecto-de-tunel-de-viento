# Guía de Configuración y Ejecución - Código de las Placas ESP32

## Requisitos Previos

### Hardware Necesario
- Placa ESP32 (cualquier variante: ESP32 Dev Module, NodeMCU-32S, etc.)
- 4 Ventiladores con conectores PWM y tacómetro (opcional)
- Cable USB (de datos, no solo de carga)
- Red WiFi disponible (2.4 GHz)

### Software Necesario
- Arduino IDE versión 2.0 o superior
- **Driver USB-UART** según el chip de tu placa:
  - **CH340/CH341** (más común en placas económicas)
  - **CP2102/CP2104** (común en placas oficiales de Espressif)
  - **FTDI** (menos común)
- **Mosquitto MQTT Broker** (opcional, si usas broker local)

### Librerías Requeridas (instalar desde el Administrador de Librerías)
- `PubSubClient` by Nick O'Leary (versión 2.8.0 o superior)
- `WiFiManager` by tzapu (versión 2.0.17 o superior) – **ya no se usan credenciales fijas**
- (Opcional) `ArduinoJson` si se requiere en futuras versiones.

## Instalación de Controladores (Drivers) del Puerto COM

Para que el PC reconozca la placa ESP32, necesitas el driver adecuado. **Identifica el chip de tu placa** mirando el componente cerca del conector USB.

### Chip CH340 (el más común)
- **Descarga oficial**: [WCH CH341SER](https://www.wch-ic.com/downloads/CH341SER_EXE.html)
- **Enlace directo**: [https://www.wch.cn/download/file?id=65](https://www.wch.cn/download/file?id=65)
- **Instalación**:
  1. Descarga `CH341SER.EXE`.
  2. Ejecútalo como administrador.
  3. Sigue las instrucciones del instalador.
  4. Conecta la placa USB y espera a que se instale automáticamente.

### Chip CP2102 / CP2104
- **Descarga oficial**: [Silicon Labs CP210x](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers)
- **Enlace directo**: [CP210x_Universal_Windows_Driver.zip](https://www.silabs.com/documents/public/software/CP210x_Universal_Windows_Driver.zip)
- **Instalación**:
  1. Descomprime el ZIP.
  2. Ejecuta `CP210xVCPInstaller_x64.exe` (para Windows 64 bits).
  3. Sigue las instrucciones.
  4. Conecta la placa.

### Verificación
- Abre el **Administrador de dispositivos** (Windows).
- Busca **Puertos (COM y LPT)**.
- Deberías ver algo como `USB-SERIAL CH340 (COMx)` o `Silicon Labs CP210x (COMx)`.
- Si aparece con un triángulo amarillo, reinstala el driver o prueba otro cable USB.

## Configuración de la Placa en Arduino IDE

### Paso 1: Añadir el soporte para ESP32
1. Abre Arduino IDE.
2. Ve a **Archivo > Preferencias**.
3. En "Gestor de URLs adicionales de tarjetas", añade:
4. Ve a **Herramientas > Placa > Gestor de tarjetas**.
5. Busca "esp32" e instala **"ESP32 by Espressif Systems"**.

### Paso 2: Seleccionar la placa correcta
- Ve a **Herramientas > Placa > ESP32** y selecciona **"ESP32 Dev Module"** (es la opción más genérica y compatible).

### Paso 3: Configurar los parámetros (según la imagen que adjuntaste)

Ajusta las siguientes opciones en el menú **Herramientas**:

| Parámetro | Valor recomendado | Nota |
|-----------|------------------|------|
| Board | `ESP32 Dev Module` | |
| Upload Speed | `115200` | Velocidad de subida del sketch |
| CPU Frequency | `240MHz (WiFi/BT)` | Máximo rendimiento |
| Core Debug Level | `None` | Para producción, ahorra recursos |
| Erase All Flash Before Sketch Upload | `Disabled` | Solo si quieres borrar todos los datos |
| Events Run On | `Core 1` | Deja el Core 0 para WiFi/BT |
| Flash Frequency | `80MHz` | Estable, compatible con la mayoría |
| Flash Mode | `DIO` | El más común (no Quad I/O) |
| Flash Size | `4MB (32Mb)` | Tamaño típico de la ESP32 |
| JTAG Adapter | `Disabled` | No usado |
| Arduino Runs On | `Core 1` | Por consistencia |
| Partition Scheme | `Default 4MB with spiffs (1.2MB APP/1.5MB SPIFFS)` | Suficiente para este proyecto |
| PSRAM | `Disabled` | La mayoría de las placas no tienen PSRAM |
| Zigbee Mode | `Disabled` | No usado |

**Importante:** Estos valores funcionan para la mayoría de las placas ESP32 Dev Module. Si tienes una placa específica (por ejemplo, ESP32-S3), ajusta según corresponda.

### Paso 4: Seleccionar el puerto COM
- Conecta la placa por USB.
- Ve a **Herramientas > Puerto** y selecciona el puerto COM que apareció (ej. `COM9`).
- Si no aparece, revisa los drivers.

## Configuración del Código (Formato-de-codigo.cpp)

El código actual utiliza **WiFiManager**, por lo que **no necesitas modificar el SSID ni la contraseña** en el código. En su lugar, la primera vez que la placa se enciende crea un punto de acceso WiFi llamado `ESP32_FanWall_Lab` al que te conectas para introducir las credenciales de tu red.

### Parámetros a modificar
Localiza la línea que define el **nombre del módulo**:
```cpp
const char* MODULE_NAME = "modulo-1";
```
Cámbialo según la placa: `"modulo-1"`, `"modulo-2"`, `"modulo-3"`, etc. Este nombre aparecerá en la interfaz web y en los tópicos MQTT.

En la linea de la definicion de los pines

```cpp
const int fanPins[4]  = {5, 16, 27, 13};
```
En la siguiente imagen se presenta la siguiente distribuciones de los pines, segun la imagen los pines de control son `{j2, j3, j4, j5}`.

![Distribucion de pines](Tunel-de-viento/Datasheets-y-recursos-utiles/Dise%C3%B1o%20de%20placa.png)

Los pines pueden variar segun las placas, para el formato **original** de las placas se tiene los pines `{5, 16, 27, 13}`, para los modulos `modulo_2` se tiene `{17, 26, 16, 13}`, para `modulo_3` se tiene `{17, 16, 27, 2}`, para los modulos `modulo_5 y 7` se tiene `{17, 4, 26, 2}`.

## Procedimiento de carga del codigo

### Paso 1: Verificar la placa y puerto

- Placa seleccionada: ESP32 Dev Module.
- Puerto COM correcto (ej. `COM9`).
- Velocidad de subida: `115200`.

### Paso 2: Compilar y cargar

- Haz clic en el botón Verificar (marca de verificación) para comprobar que no hay errores.
- Luego haz clic en Cargar (flecha hacia la derecha).
- Espera a que aparezca `Salida completada` en la consola

### Paso 3: Configuración WiFi por primera vez (WiFiManager)

1. Después de cargar el código, la placa creará un punto de acceso WiFi llamado `ESP32_FanWall_Lab`.
2. Con tu teléfono o PC, conéctate a esa red (sin contraseña).
3. Abre un navegador y ve a la dirección `192.168.4.1.`
4. Se abrirá una página donde debes seleccionar tu red WiFi y escribir la contraseña.
5. La placa se reiniciará y se conectará a tu WiFi.
6. A partir de entonces, recordará las credenciales.

