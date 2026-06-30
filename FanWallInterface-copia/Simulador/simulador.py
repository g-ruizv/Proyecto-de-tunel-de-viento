#!/usr/bin/env python3
"""
Simulador de ESP32 para FanWall.
Se comporta como múltiples módulos que responden a comandos MQTT.
Módulos simulados: 1, 2, 3, 8, 11, 15
"""

import time
import paho.mqtt.client as mqtt
import threading
import random

MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883

# Lista de IDs de módulos que simularemos
MODULOS = ["modulo-1", "modulo-2", "modulo-3", "modulo-8", "modulo-11", "modulo-15",""]

# Almacenar velocidades actuales de cada módulo (0-100)
velocidades = {mod: 0 for mod in MODULOS}

# Control de reconexión
running = True

def on_connect(client, userdata, flags, rc):
    print(f"[Simulador] Conectado al broker con código {rc}")
    # Suscribirse al tópico de identificación y a los comandos de cada módulo
    client.subscribe("fanWall/wall/id")
    for mod in MODULOS:
        client.subscribe(f"fanWall/wall/{mod}")
    print(f"[Simulador] Suscrito a {len(MODULOS)} módulos.")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode().strip()
    
    if topic == "fanWall/wall/id":
        if payload == "get":
            # Responder con todos los IDs
            for mod in MODULOS:
                client.publish("fanWall/wall/id", mod)
                print(f"[Simulador] Respondiendo a 'get' con ID: {mod}")
    else:
        # Comando de velocidad para un módulo concreto
        # El tópico es "fanWall/wall/<id>"
        module_id = topic.split('/')[-1]
        if module_id in velocidades:
            try:
                speed = int(payload)
                # Limitar a 0-100
                speed = max(0, min(100, speed))
                if velocidades[module_id] != speed:
                    velocidades[module_id] = speed
                    print(f"[Simulador] Módulo {module_id} -> {speed}%")
                    # Publicar el nuevo estado
                    client.publish(f"fanWall/wall/estado/{module_id}", str(speed))
            except ValueError:
                print(f"[Simulador] Comando inválido para {module_id}: {payload}")

def on_disconnect(client, userdata, rc):
    print(f"[Simulador] Desconectado (código {rc})")
    if rc != 0 and running:
        print("[Simulador] Intentando reconectar...")

def heartbeat_loop(client):
    """Publica heartbeats cada 10 segundos."""
    while running:
        for mod in MODULOS:
            client.publish("fanWall/wall/id", mod)
        time.sleep(10)

def main():
    global running
    
    # Configurar cliente MQTT
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    # Conectar y mantener conexión con reconexión automática
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except Exception as e:
        print(f"[Simulador] Error al conectar: {e}")
        return
    
    client.loop_start()
    
    # Publicar estados iniciales (todos a 0) para que la interfaz los muestre
    time.sleep(1)  # Esperar a que la conexión esté estable
    for mod in MODULOS:
        client.publish(f"fanWall/wall/estado/{mod}", "0")
        client.publish("fanWall/wall/id", mod)
    print("[Simulador] Estados iniciales publicados.")
    
    # Lanzar hilo de heartbeats
    hilo_heartbeat = threading.Thread(target=heartbeat_loop, args=(client,), daemon=True)
    hilo_heartbeat.start()
    
    print(f"[Simulador] Iniciado con {len(MODULOS)} módulos: {', '.join(MODULOS)}")
    print("[Simulador] Esperando comandos MQTT. Presiona Ctrl+C para detener.")
    
    try:
        while running:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Simulador] Deteniendo...")
        running = False
        client.loop_stop()
        client.disconnect()
        print("[Simulador] Detenido.")

if __name__ == "__main__":
    main()