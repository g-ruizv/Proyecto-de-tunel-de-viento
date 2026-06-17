#!/usr/bin/env python3
"""
Interfaz Tkinter para visualizar el estado de los módulos FanWall.
Se suscribe a fanWall/wall/estado/# para recibir velocidades actualizadas.
"""

import tkinter as tk
from tkinter import ttk
import paho.mqtt.client as mqtt
import time

MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883

class FanWallDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("FanWall Dashboard - Simulador")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a1a2e')
        
        self.modules = {}
        self.last_update = tk.StringVar(value="Esperando datos...")
        self.module_counter = 0
        
        self.build_ui()
        self.setup_mqtt()
    
    def build_ui(self):
        # Título
        title = tk.Label(self.root, text="FanWall Dashboard", 
                         font=('Segoe UI', 24, 'bold'), 
                         fg='#e94560', bg='#1a1a2e')
        title.pack(pady=10)
        
        # Canvas con scroll
        self.canvas = tk.Canvas(self.root, bg='#1a1a2e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient='vertical', command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#1a1a2e')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y')
        
        # Grid de módulos (2 columnas)
        self.grid_frame = tk.Frame(self.scrollable_frame, bg='#1a1a2e')
        self.grid_frame.pack(fill='both', expand=True)
        self.grid_frame.grid_columnconfigure(0, weight=1)
        self.grid_frame.grid_columnconfigure(1, weight=1)
        
        # Leyenda
        bottom_frame = tk.Frame(self.root, bg='#1a1a2e')
        bottom_frame.pack(side='bottom', fill='x', pady=10)
        legend_frame = tk.Frame(bottom_frame, bg='#0f3460', padx=10, pady=5)
        legend_frame.pack(pady=5)
        
        tk.Label(legend_frame, text="0%", fg='white', bg='#0f3460', font=('Arial', 10)).pack(side='left', padx=5)
        gradiente = tk.Canvas(legend_frame, width=150, height=15, bg='#0f3460', highlightthickness=0)
        gradiente.pack(side='left', padx=5)
        for i in range(150):
            ratio = i / 150
            if ratio < 0.5:
                t = ratio / 0.5
                r = 0
                g = int(68 * t + 68)
                b = int(168 - 168 * t)
            else:
                t = (ratio - 0.5) / 0.5
                r = int(0 + 232 * t)
                g = int(136 - 136 * t)
                b = 0
            color = f'#{r:02x}{g:02x}{b:02x}'
            gradiente.create_line(i, 0, i, 15, fill=color, width=2)
        tk.Label(legend_frame, text="100%", fg='white', bg='#0f3460', font=('Arial', 10)).pack(side='left', padx=5)
        
        tk.Label(bottom_frame, textvariable=self.last_update, 
                 fg='#aaa', bg='#1a1a2e', font=('Arial', 9)).pack(pady=5)
    
    def get_color(self, speed):
        ratio = speed / 100
        if ratio < 0.5:
            t = ratio / 0.5
            r = 0
            g = int(68 * t + 68)
            b = int(168 - 168 * t)
        else:
            t = (ratio - 0.5) / 0.5
            r = int(0 + 232 * t)
            g = int(136 - 136 * t)
            b = 0
        return f'#{min(r,255):02x}{min(g,255):02x}{min(b,255):02x}'
    
    def add_module(self, module_id):
        if module_id in self.modules:
            return
    
        COLUMNAS = 4  # Número de columnas (puedes usar 6 si quieres más horizontal)
        row = self.module_counter // COLUMNAS
        col = self.module_counter % COLUMNAS
        self.module_counter += 1
    
        module_frame = tk.Frame(self.grid_frame, bg='#16213e', bd=2, relief='solid',
                            borderwidth=1, highlightbackground='#0f3460', highlightthickness=2)
        module_frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
    
    # Configurar peso de columnas para que se expandan
        self.grid_frame.grid_columnconfigure(col, weight=1)
        self.grid_frame.grid_rowconfigure(row, weight=1)
        
        title = tk.Label(module_frame, text=module_id, font=('Segoe UI', 14, 'bold'),
                         fg='#e94560', bg='#16213e')
        title.pack(pady=(5,10))
        
        fans_frame = tk.Frame(module_frame, bg='#16213e')
        fans_frame.pack(pady=5)
        
        fan_labels = []
        speed_labels = []
        for i in range(4):
            row_fan = i // 2
            col_fan = i % 2
            fan_cell = tk.Frame(fans_frame, bg='#0f3460', relief='flat', bd=2,
                                highlightthickness=0, width=80, height=80)
            fan_cell.grid(row=row_fan, column=col_fan, padx=8, pady=8, sticky='nsew')
            fan_cell.grid_propagate(False)
            
            tk.Label(fan_cell, text=f"V{i+1}", font=('Arial', 9),
                     fg='#ccc', bg='#0f3460').pack(pady=(8,0))
            speed_label = tk.Label(fan_cell, text="0%", font=('Arial', 12, 'bold'),
                                   fg='white', bg='#0f3460')
            speed_label.pack(pady=(2,0))
            fan_labels.append(fan_cell)
            speed_labels.append(speed_label)
        
        tk.Label(module_frame, text="Online", font=('Arial', 9),
                 fg='#28a745', bg='#16213e').pack(pady=(5,0))
        
        self.modules[module_id] = {'fans': fan_labels, 'speed_labels': speed_labels}
        
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def update_module(self, module_id, speed):
        if module_id not in self.modules:
            self.add_module(module_id)
        module = self.modules[module_id]
        color = self.get_color(speed)
        for fan in module['fans']:
            fan.configure(bg=color)
        for label in module['speed_labels']:
            label.configure(text=f"{int(speed)}%", fg='white')
        self.last_update.set(f"Última actualización: {time.strftime('%H:%M:%S')}")
    
    def setup_mqtt(self):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        self.mqtt_client.loop_start()
    
    def on_connect(self, client, userdata, flags, rc):
        print("[Interfaz Tk] Conectada a MQTT")
        client.subscribe("fanWall/wall/estado/#")
        client.subscribe("fanWall/wall/id")
    
    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode().strip()
        if topic == "fanWall/wall/id":
            # Si llega un heartbeat de un módulo nuevo, añadirlo (si no existe)
            if payload.startswith('modulo-'):
                if payload not in self.modules:
                    self.root.after(0, lambda: self.add_module(payload))
        elif topic.startswith("fanWall/wall/estado/"):
            module_id = topic.split('/')[-1]
            if module_id.startswith('modulo-'):
                try:
                    speed = int(payload)
                    self.root.after(0, lambda: self.update_module(module_id, speed))
                except ValueError:
                    pass

if __name__ == "__main__":
    root = tk.Tk()
    app = FanWallDashboard(root)
    root.mainloop()