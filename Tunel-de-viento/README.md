# Recursos del Túnel de Viento

Esta carpeta contiene todos los recursos de hardware, esquemáticos, hojas de datos y documentación complementaria para el proyecto de túnel de viento con pared de ventiladores (Fan Wall). El contenido está organizado para facilitar la consulta y el mantenimiento.

## Estructura de carpetas

```
Tunel-de-viento/
├── Datasheets-y-recursos-utiles/ # Hojas de datos y esquemáticos
│ ├── Diseño de placa.png # Esquemático de la placa de control
│ ├── Esquematico Gral-FanWall.pdf
│ ├── Esquelamento-Módulo.pdf
│ ├── Equipamento Fan-Wall Controller MK II.pdf
│ ├── PFR1212UHE-SP00.pdf # Datasheet del ventilador
│ └── WBDesign3.pdf
├── Codigo-de-las-placas/ # Firmware para ESP32
│ ├── formato_de_placas_3.ino # Código principal (WiFiManager, MQTT, PWM)
│ └── README.md # Guía de configuración y carga
└── README.md # Este archivo (índice del túnel de viento)
```


## Contenido destacado

### Datasheets y recursos útiles
- **`Diseño de placa.png`** – Esquemático de conexiones entre ESP32, ventiladores y tacómetros.
- **`Esquematico Gral-FanWall.pdf`** – Diagrama general del sistema de control.
- **`Esquelamento-Módulo.pdf`** – Detalle del módulo de ventiladores (distribución y armado).
- **`Equipamento Fan-Wall Controller MK II.pdf`** – Especificaciones del controlador comercial (referencia).
- **`PFR1212UHE-SP00.pdf`** – Hoja de datos del ventilador utilizado (12V, PWM, tacómetro).
- **`WBDesign3.pdf`** – Documento de diseño de la pared de viento (cálculos aerodinámicos).

### Código de las placas
- La carpeta `Codigo-de-las-placas/` contiene el firmware para ESP32. El archivo `formato_de_placas_3.ino` es el sketch principal que implementa:
  - Conexión WiFi mediante WiFiManager.
  - Suscripción a tópicos MQTT (`fanWall/wall/modulo-X`).
  - Control PWM de 4 ventiladores con lectura de tacómetro.
  - Publicación de ID y estado.
- Consulta el `README.md` dentro de esa carpeta para instrucciones de instalación, configuración y carga.

## Cómo usar este directorio

1. **Para entender el hardware** – Revisa los PDF y la imagen en `Datasheets-y-recursos-utiles/`.
2. **Para programar las placas** – Ve a `Codigo-de-las-placas/` y sigue la guía.
3. **Si añades nuevos recursos** – Actualiza este `README.md` para mantener la documentación al día.

## Notas

- Los archivos PDF y PNG son versiones originales proporcionadas por los fabricantes o diseñadas durante el proyecto.
- El código `formato_de_placas_3.ino` está probado para ESP32 Dev Module y placas compatibles.
- Para cualquier duda, revisa los mensajes de commit o contacta a los colaboradores del repositorio.
