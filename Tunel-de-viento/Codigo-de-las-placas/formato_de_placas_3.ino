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
// ==========================================
const int fanPins[4]  = {5, 16, 27, 13};  // no modificar, esta asi en el esquematico  
const char* MODULE_NAME = "modulo-10"; 
String moduleId = "";  
#define LED_PIN 2

// ==========================================
// CONFIGURACIÓN MQTT (Sincronizado con mqtt.py)
// ==========================================
const char* mqttBroker = "broker.emqx.io";
const int mqttPort = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

String macAddress = "";
String selfTopic = "";
unsigned long lastReconnectAttempt = 0;
unsigned long lastIdPublish = 0;

// Control de ventiladores (PWM)
void setSpeeds(int speed) {
  speed = constrain(speed*2.55, 0, 255);
  for (int i = 0; i < 4; i++) {
    ledcWrite(fanPins[i], speed);
  }
  Serial.printf("Velocidad: %d\n", speed);
}

// Procesar mensajes que vienen desde Python/Web
void callback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) message += (char)payload[i];
  String strTopic = String(topic);

  // Si la web pide identificación o si recibe comando de velocidad
  if (strTopic == "fanWall/wall/id" && message == "get") {
    client.publish("fanWall/wall/id", macAddress.c_str());
  } else if (strTopic == selfTopic) {
    setSpeeds(message.toInt());
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);

  // LIMITACIÓN DE ENERGÍA: Evita que la placa se resetee al usar WiFi
  WiFi.setTxPower(WIFI_POWER_8_5dBm); 

  // Configurar PWM
  for (int i = 0; i < 4; i++) {
    ledcAttach(fanPins[i], 25000, 8);
    ledcWrite(fanPins[i], 0);
  }

  // Configuración de WiFi sin reinicio forzado
  WiFiManager wm;
  wm.setConfigPortalTimeout(300); // 5 minutos de espera antes de continuar
  
  if (!wm.autoConnect("ESP32_FanWall_Lab")) {
    Serial.println("Portal agotado, intentando conectar con credenciales guardadas...");
  }

  //macAddress = WiFi.macAddress();
  moduleId = String(MODULE_NAME);
  selfTopic = "fanWall/wall/" + moduleId; // Tópico único: fanWall/wall/XX:XX:XX...

  client.setServer(mqttBroker, mqttPort);
  client.setCallback(callback);
  
  digitalWrite(LED_PIN, LOW);
  Serial.println("Sistema iniciado. ID: " + moduleId);
}

void loop() {
  // Mantener WiFi y MQTT activos
  if (WiFi.status() == WL_CONNECTED) {
    if (!client.connected()) {
      unsigned long now = millis();
      if (now - lastReconnectAttempt > 500) {
        lastReconnectAttempt = now;
        String clientId = "ESP32_" + moduleId;
        if (client.connect(clientId.c_str())) {
          // Suscribirse a los canales definidos en mqtt.py
          client.subscribe("fanWall/wall/id");
          client.subscribe(selfTopic.c_str());
          
          // Enviar estado inicial
          String statusMsg = "Connected/" + moduleId;
          client.publish("fanWall/wall/status", statusMsg.c_str());
          client.publish("fanWall/wall/id", moduleId.c_str());
        }
      }
    } else {
      client.loop();
      
      // Heartbeat: Publicar ID cada 20 seg para que el slider no desaparezca
      unsigned long now = millis();
      if (now - lastIdPublish > 20000) {
        lastIdPublish = now;
        client.publish("fanWall/wall/id", moduleId.c_str());
      }
    }
  }
}
