// ============================================================
//  CÓDIGO PARA MÓDULO ESP32 - CONTROL DE 4 VENTILADORES
//  Proyecto: Fan-Wall Interface (Túnel de Viento)
//  Versión: 1.0
// ============================================================

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ========== SECCIÓN DE PERSONALIZACIÓN ==========
//  ¡MODIFICAR ESTOS VALORES PARA CADA MÓDULO!

// 1. Identificador único del módulo (cambiar por modulo_02, modulo_03... modulo_16)
const char* MODULE_ID = "modulo_01";

// 2. Credenciales de la red WiFi
const char* ssid = "TU_SSID";           // Nombre de tu red WiFi
const char* password = "TU_PASSWORD";   // Contraseña de tu red WiFi

// 3. Dirección IP del servidor MQTT (la PC donde corre Mosquitto y FanWallInterface)
const char* mqtt_server = "192.168.1.100";

// ==============================================

// Puerto estándar MQTT (no modificar)
const int mqtt_port = 1883;

// Tópicos MQTT (se construyen automáticamente a partir del MODULE_ID)
String topic_sensores = "fanwall/" + String(MODULE_ID) + "/sensores";
String topic_estado   = "fanwall/" + String(MODULE_ID) + "/estado";
String topic_control  = "fanwall/" + String(MODULE_ID) + "/control";

// Clientes WiFi y MQTT
WiFiClient espClient;
PubSubClient client(espClient);

// ========== PINES (NO MODIFICAR) ==========
// Pines PWM para control de ventiladores (salidas)
const int fanPins[4] = {28, 26, 11, 16};   // Ventilador 1, 2, 3, 4

// Pines TACH para lectura de tacómetros (entradas)
const int tachPins[4] = {29, 27, 12, 13};  // Tacómetro 1, 2, 3, 4
// ==========================================

// Variables de estado de los ventiladores
bool fanStates[4] = {false, false, false, false};  // true = encendido, false = apagado
int fanSpeeds[4] = {0, 0, 0, 0};                   // Velocidad deseada (0-255) - reservado para PWM

// Variables para medición de RPM
volatile unsigned int tachPulseCount[4] = {0, 0, 0, 0};  // Contadores de pulsos (volatile por interrupciones)
unsigned long lastRPMCalc = 0;                            // Momento del último cálculo de RPM
float fanRPM[4] = {0.0, 0.0, 0.0, 0.0};                   // RPM calculadas

// ========== PROTOTIPOS DE FUNCIONES ==========
void setup_wifi();
void reconnect();
void callback(char* topic, byte* payload, unsigned int length);
void publicarEstado();
void publicarSensores();
void calcularRPM();
void IRAM_ATTR tachISR(void* arg);

// ============================================
//  FUNCIÓN DE CONFIGURACIÓN INICIAL (setup)
// ============================================
void setup() {
  // 1. Iniciar comunicación serie para depuración (solo por USB)
  Serial.begin(115200);

  // 2. Configurar pines PWM como salidas y apagar ventiladores
  for (int i = 0; i < 4; i++) {
    ledcSetup(i, 5000, 8);           // Canal, Frecuencia 5kHz, 8 bits
    ledcAttachPin(fanPins[i], i);    // Asignar pin a canal
    digitalWrite(fanPins[i], LOW);   // Apagar al inicio
  }

  // 3. Configurar pines TACH como entradas con pull-up y adjuntar interrupciones
  for (int i = 0; i < 4; i++) {
    pinMode(tachPins[i], INPUT_PULLUP);
    attachInterruptArg(digitalPinToInterrupt(tachPins[i]), tachISR, &tachPulseCount[i], FALLING);
  }

  // 4. Conectar a la red WiFi
  setup_wifi();

  // 5. Configurar cliente MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

// ============================================
//  BUCLE PRINCIPAL (loop)
// ============================================
void loop() {
  // 1. Verificar y mantener conexión MQTT
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // 2. Publicar datos periódicamente (cada 1 segundo)
  static unsigned long lastPublish = 0;
  unsigned long now = millis();
  if (now - lastPublish > 1000) {
    calcularRPM();           // Calcular revoluciones por minuto
    publicarSensores();      // Enviar RPM al servidor
    publicarEstado();        // Enviar estado de ventiladores al servidor
    lastPublish = now;
  }
}

// ============================================
//  FUNCIÓN: Conexión a la red WiFi
// ============================================
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Conectando a ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi conectado. IP: " + WiFi.localIP().toString());
}

// ============================================
//  FUNCIÓN: Reconexión al servidor MQTT
// ============================================
void reconnect() {
  while (!client.connected()) {
    Serial.print("Intentando conexión MQTT...");
    // Crear un identificador único para el cliente MQTT
    String clientId = "ESP32_" + String(MODULE_ID) + "_" + String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str())) {
      Serial.println("conectado");
      // Suscribirse al tópico de control para recibir comandos
      client.subscribe(topic_control.c_str());
    } else {
      Serial.print("falló, rc=");
      Serial.print(client.state());
      Serial.println(" reintentando en 5s");
      delay(5000);
    }
  }
}

// ============================================
//  FUNCIÓN: Callback MQTT - Se ejecuta al recibir un mensaje
// ============================================
void callback(char* topic, byte* payload, unsigned int length) {
  // Convertir el mensaje de bytes a String
  String mensaje;
  for (int i = 0; i < length; i++) {
    mensaje += (char)payload[i];
  }

  // Parsear el JSON recibido
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, mensaje);
  if (error) {
    Serial.println("Error al parsear JSON");
    return;
  }

  // Procesar comandos para ventiladores
  if (doc.containsKey("ventiladores")) {
    JsonArray fans = doc["ventiladores"];
    for (int i = 0; i < fans.size() && i < 4; i++) {
      JsonObject fan = fans[i];
      if (fan.containsKey("estado")) {
        fanStates[i] = fan["estado"];                       // Guardar nuevo estado
        analogWrite(fanPins[i], fanStates[i] ? fanSpeeds[i] : 0); // Activar/desactivar pin
      }
      if (fan.containsKey("velocidad")) {
        fanSpeeds[i] = fan["velocidad"];
        analogWrite(fanPins[i], fanSpeeds[i]);                    // Guardar velocidad (para futuro PWM)
      }
    }
  }

  // Confirmar el nuevo estado al servidor
  publicarEstado();
}

// ============================================
//  FUNCIÓN: Publicar estado de los ventiladores
// ============================================
void publicarEstado() {
  StaticJsonDocument<512> doc;
  doc["module_id"] = MODULE_ID;
  JsonArray fans = doc.createNestedArray("ventiladores");
  for (int i = 0; i < 4; i++) {
    JsonObject fan = fans.createNestedObject();
    fan["id"] = i;
    fan["estado"] = fanStates[i];
    fan["velocidad"] = fanSpeeds[i];
  }
  
  String output;
  serializeJson(doc, output);
  client.publish(topic_estado.c_str(), output.c_str());
}

// ============================================
//  FUNCIÓN: Publicar datos de sensores (RPM)
// ============================================
void publicarSensores() {
  StaticJsonDocument<256> doc;
  doc["module_id"] = MODULE_ID;
  JsonArray rpmArray = doc.createNestedArray("rpm_ventiladores");
  for (int i = 0; i < 4; i++) {
    rpmArray.add(fanRPM[i]);
  }
  
  String output;
  serializeJson(doc, output);
  client.publish(topic_sensores.c_str(), output.c_str());
}

// ============================================
//  FUNCIÓN: Calcular RPM a partir de pulsos acumulados
// ============================================
void calcularRPM() {
  unsigned long currentTime = millis();
  unsigned long elapsed = currentTime - lastRPMCalc;
  
  if (elapsed > 0) {
    for (int i = 0; i < 4; i++) {
      // Leer y reiniciar contador de pulsos de forma segura (desactivando interrupciones momentáneamente)
      noInterrupts();
      unsigned int pulses = tachPulseCount[i];
      tachPulseCount[i] = 0;
      interrupts();
      
      // Calcular RPM (asumiendo 2 pulsos por revolución, típico en ventiladores de PC)
      fanRPM[i] = (pulses / 2.0) * (60000.0 / elapsed);
    }
  }
  lastRPMCalc = currentTime;
}

// ============================================
//  FUNCIÓN: Interrupción para contar pulsos del tacómetro
// ============================================
void IRAM_ATTR tachISR(void* arg) {
  unsigned int* counter = (unsigned int*)arg;
  (*counter)++;
}