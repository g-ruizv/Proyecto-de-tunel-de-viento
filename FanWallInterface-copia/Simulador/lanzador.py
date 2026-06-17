#!/usr/bin/env python3
"""
Lanzador de FanWall: ejecuta el simulador y la interfaz grafica en simultaneo.
"""

import subprocess
import sys
import os
import threading

def print_output(proc, name):
    for line in iter(proc.stdout.readline, ''):
        if line:
            print(f"[{name}] {line.rstrip()}")

def main():
    print("Lanzando FanWall Simulator + GUI...")
    print("Presiona Ctrl+C para detener ambos procesos.\n")

    base_dir = os.path.dirname(os.path.abspath(__file__))

    simulador_proc = subprocess.Popen(
        [sys.executable, os.path.join(base_dir, "simulador.py")],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    interfaz_proc = subprocess.Popen(
        [sys.executable, os.path.join(base_dir, "interfaz.py")],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    threading.Thread(target=print_output, args=(simulador_proc, "SIMULADOR"), daemon=True).start()
    threading.Thread(target=print_output, args=(interfaz_proc, "INTERFAZ"), daemon=True).start()

    try:
        simulador_proc.wait()
        interfaz_proc.wait()
    except KeyboardInterrupt:
        print("\nDeteniendo procesos...")
        simulador_proc.terminate()
        interfaz_proc.terminate()
        simulador_proc.wait()
        interfaz_proc.wait()
        print("Procesos detenidos.")

if __name__ == "__main__":
    main()