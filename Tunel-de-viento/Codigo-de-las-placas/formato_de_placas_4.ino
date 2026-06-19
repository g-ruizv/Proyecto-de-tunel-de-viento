#include <WiFi.h>
#include <PubSubClient.h>
#include <WiFiManager.h>

// ==========================================
// CONFIGURACIÓN DE HARDWARE
// ==========================================
//   orden de los pins {j2, j3, j4, j5}
//   original = {5, 16, 27, 13}
//   modulo_5_7 = {17, 4, 26, 2}
//   modulo_3 = {17, 16, 27, 2}
//   modulo_2 = {17, 26, 16, 13}
const int fanPins[4]  = {5, 16, 27, 13};  // ajusta según tu placa
const char* MODULE_NAME = "modulo-10"; 
#define LED_PIN 2

// ==========================================
// CONFIGURACIÓN MQTT
// ==========================================
const char* mqttBroker = "broker.emqx.io";
const int mqttPort = 1883;

WiFiClient espClient;
PubSubClient client(espClient);
String selfTopic = "";
unsigned long lastReconnectAttempt = 0;
int reconnectDelay = 500;
unsigned long lastIdPublish = 0;
unsigned long lastWifiCheck = 0;

// ==========================================
// FUNCIÓN PARA ESCRIBIR PWM (0-255)
// ==========================================
void writePWM(int pin, int value) {
  ledcWrite(pin, value);
}

// ==========================================
// FUNCIÓN PARA CAMBIAR VELOCIDAD (DIRECTA)
// ==========================================
void setSpeeds(int speed) {
  speed = constrain(speed, 0, 100);
  // Si tu ventilador usa PWM invertido (0% = 255, 100% = 0), usa esta línea:
  // int pwmValue = map(speed, 0, 100, 255, 0);
  // Si es PWM normal, usa esta:
  int pwmValue = map(speed, 0, 100, 0, 255);
  
  for (int i = 0; i < 4; i++) {
    writePWM(fanPins[i], pwmValue);
  }
  Serial.printf("Velocidad: %d%% (PWM: %d)\n", speed, pwmValue);
}

// ==========================================
// FUNCIÓN PARA ARRANQUE ESCALONADO (SOLO UNA VEZ)
// ==========================================
void arranqueEscalonado(int speed) {
  speed = constrain(speed, 0, 100);
  int pwmValue = map(speed, 0, 100, 0, 255);
  
  Serial.println("Arranque escalonado: activando ventiladores uno por uno...");
  for (int i = 0; i < 4; i++) {
    writePWM(fanPins[i], pwmValue);
    Serial.printf("Ventilador %d encendido a %d%%\n", i+1, speed);
    delay(100);  // 500ms entre cada ventilador
  }
  Serial.println("Arranque completado.");
}

// ==========================================
// CALLBACK MQTT
// ==========================================
void callback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) message += (char)payload[i];
  String strTopic = String(topic);

  if (strTopic == "fanWall/wall/id" && message == "get") {
    client.publish("fanWall/wall/id", MODULE_NAME, true);
  } else if (strTopic == selfTopic) {
    int newSpeed = message.toInt();
    // CAMBIO DIRECTO (sin rampa, sin escalonado)
    setSpeeds(newSpeed);
    // Publicar estado actual
    client.publish(("fanWall/wall/estado/" + String(MODULE_NAME)).c_str(), String(newSpeed).c_str(), true);
  }
}

// ==========================================
// SETUP
// ==========================================
void setup() {
  Serial.begin(115200);

  // ========== APAGAR VENTILADORES AL ARRANCAR ==========
  for (int i = 0; i < 4; i++) {
    pinMode(fanPins[i], OUTPUT);
    digitalWrite(fanPins[i], LOW);
    ledcAttach(fanPins[i], 25000, 8);
    writePWM(fanPins[i], 0);  // 0% PWM
  }

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);

  WiFi.setTxPower(WIFI_POWER_8_5dBm);

  // WiFiManager
  WiFiManager wm;
  wm.setConfigPortalTimeout(300);
  if (!wm.autoConnect("ESP32_FanWall_Lab")) {
    Serial.println("Portal agotado, intentando conectar con credenciales guardadas...");
  }

  selfTopic = "fanWall/wall/" + String(MODULE_NAME);
  client.setServer(mqttBroker, mqttPort);
  client.setCallback(callback);

  digitalWrite(LED_PIN, LOW);
  Serial.println("Sistema iniciado. ID: " + String(MODULE_NAME));

  // ========== ARRANQUE ESCALONADO (UNA SOLA VEZ) ==========
  // Esperamos 1 segundo para que el sistema se estabilice
  delay(1000);
  // Arrancar ventiladores al 50% de velocidad, uno por uno
  arranqueEscalonado(10);  // Cambia el valor según necesites (0-100)
}

// ==========================================
// LOOP (igual que antes, sin rampa)
// ==========================================
void loop() {
  // === Control de WiFi ===
  if (WiFi.status() != WL_CONNECTED) {
    if (millis() - lastWifiCheck > 5000) {
      lastWifiCheck = millis();
      Serial.println("WiFi perdido, reconectando...");
      WiFi.reconnect();
    }
    delay(100);
    return;
  }

  // === Control de MQTT ===
  if (!client.connected()) {
    unsigned long now = millis();
    if (now - lastReconnectAttempt > reconnectDelay) {
      lastReconnectAttempt = now;
      String clientId = "ESP32_" + String(MODULE_NAME);
      if (client.connect(clientId.c_str())) {
        client.subscribe("fanWall/wall/id");
        client.subscribe(selfTopic.c_str());
        client.publish("fanWall/wall/status", ("Connected/" + String(MODULE_NAME)).c_str(), true);
        client.publish("fanWall/wall/id", MODULE_NAME, true);
        client.publish(("fanWall/wall/estado/" + String(MODULE_NAME)).c_str(), "0", true);
        reconnectDelay = 500;
        digitalWrite(LED_PIN, LOW);
        Serial.println("MQTT conectado");
      } else {
        reconnectDelay = min(reconnectDelay * 2, 10000);
        Serial.printf("MQTT falló, próximo intento en %d ms\n", reconnectDelay);
      }
    }
    return;
  }

  client.loop();

  // === Heartbeat (cada 10 segundos) ===
  if (millis() - lastIdPublish > 10000) {
    lastIdPublish = millis();
    client.publish("fanWall/wall/id", MODULE_NAME, true);
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
  }
}