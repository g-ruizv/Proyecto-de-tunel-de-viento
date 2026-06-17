#!/usr/bin/env python3
import time
import paho.mqtt.client as mqtt
import threading

MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883

# Generar 20 módulos: modulo-1, modulo-2, ..., modulo-20
MODULOS = [f"modulo-{i}" for i in range(1, 9)]

velocidades = {mod: 0 for mod in MODULOS}

def on_connect(client, userdata, flags, rc):
    print(f"[Simulador] Conectado al broker con código {rc}")
    client.subscribe("fanWall/wall/id")
    for mod in MODULOS:
        client.subscribe(f"fanWall/wall/{mod}")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode().strip()
    if topic == "fanWall/wall/id":
        if payload == "get":
            for mod in MODULOS:
                client.publish("fanWall/wall/id", mod)
                print(f"[Simulador] Respondiendo a 'get' con {mod}")
    elif topic.startswith("fanWall/wall/"):
        module_id = topic.split('/')[-1]
        if module_id in velocidades:
            try:
                speed = int(payload)
                velocidades[module_id] = speed
                print(f"[Simulador] Comando recibido: {module_id} -> {speed}%")
                client.publish(f"fanWall/wall/estado/{module_id}", str(speed))
            except ValueError:
                pass

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

# ========== NUEVO: Publicar heartbeats y estados iniciales ==========
def publicar_inicial():
    print(f"[Simulador] Publicando heartbeats y estados iniciales para {len(MODULOS)} módulos...")
    for mod in MODULOS:
        client.publish("fanWall/wall/id", mod)
        client.publish(f"fanWall/wall/estado/{mod}", "0")
    print("[Simulador] Publicación inicial completada.")

publicar_inicial()
# ====================================================================

# Hilo para heartbeats periódicos (cada 20 seg)
def heartbeat_loop():
    while True:
        for mod in MODULOS:
            client.publish("fanWall/wall/id", mod)
            print(f"[Simulador] Heartbeat: {mod}")
        time.sleep(20)

threading.Thread(target=heartbeat_loop, daemon=True).start()

print("[Simulador] Iniciado con 20 módulos.")
print("[Simulador] Publicando heartbeats cada 20 segundos y esperando comandos...")
print("[Simulador] Presiona Ctrl+C para detener.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[Simulador] Deteniendo...")
    client.loop_stop()
    client.disconnect()
    print("[Simulador] Detenido.")