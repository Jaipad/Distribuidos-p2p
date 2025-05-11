import socket
import threading
import json
import random
from collections import defaultdict

HOST = 'localhost'
PORT = 5000

# Estado global del servidor
equipos = {"Equipo1": [], "Equipo2": []}
puntos = {"Equipo1": 0, "Equipo2": 0}
orden_juego = []
turno_actual = 0
clientes = []
nombres = {}  # socket: nombre_equipo
bloqueo = threading.Lock()
juego_iniciado = False

def broadcast(mensaje):
    for cliente in clientes:
        try:
            cliente.send(json.dumps(mensaje).encode())
        except:
            pass

def manejar_cliente(cliente_socket):
    global juego_iniciado, turno_actual

    equipo_asignado = None
    try:
        # Solicitar nombre de equipo
        cliente_socket.send(json.dumps({"accion": "registrarse"}).encode())
        data = json.loads(cliente_socket.recv(1024).decode())
        equipo_asignado = data.get("equipo")

        if equipo_asignado not in equipos:
            cliente_socket.send(json.dumps({"accion": "error", "mensaje": "Equipo inválido"}).encode())
            cliente_socket.close()
            return

        with bloqueo:
            equipos[equipo_asignado].append(cliente_socket)
            nombres[cliente_socket] = equipo_asignado
            clientes.append(cliente_socket)
            print(f"Nuevo jugador en {equipo_asignado}")

            # ¿Hay al menos un jugador por equipo?
            if all(len(v) >= 1 for v in equipos.values()) and not juego_iniciado:
                orden_juego.extend(random.sample(list(equipos.keys()), k=2))
                juego_iniciado = True
                broadcast({"accion": "iniciar", "orden": orden_juego})
                anunciar_turno()

        while True:
            data = cliente_socket.recv(1024).decode()
            if not data:
                break
            mensaje = json.loads(data)
            if mensaje.get("accion") == "tirar_dado":
                equipo = nombres[cliente_socket]
                with bloqueo:
                    if equipo != orden_juego[turno_actual]:
                        cliente_socket.send(json.dumps({"accion": "error", "mensaje": "No es tu turno"}).encode())
                        continue
                    tirada = random.randint(1, 6)
                    puntos[equipo] += tirada
                    broadcast({
                        "accion": "actualizar",
                        "equipo": equipo,
                        "tirada": tirada,
                        "puntos": puntos[equipo]
                    })
                    if puntos[equipo] >= 100:
                        broadcast({"accion": "fin", "ganador": equipo})
                        break
                    turno_actual = (turno_actual + 1) % len(orden_juego)
                    anunciar_turno()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cliente_socket.close()

def anunciar_turno():
    equipo = orden_juego[turno_actual]
    broadcast({"accion": "turno", "equipo": equipo})

def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((HOST, PORT))
    servidor.listen()
    print(f"Servidor iniciado en {HOST}:{PORT}")
    while True:
        cliente, addr = servidor.accept()
        print(f"Conexión de {addr}")
        hilo = threading.Thread(target=manejar_cliente, args=(cliente,))
        hilo.start()

if __name__ == "__main__":
    iniciar_servidor()
