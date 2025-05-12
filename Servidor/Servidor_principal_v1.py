import socket
import threading
import json
import random
from collections import defaultdict
from dotenv import load_dotenv
import os

load_dotenv()

HOST = 'localhost'
PORT = 5000

max_teams = int(os.getenv('MAX_TEAMS'))
max_members_per_team = int(os.getenv('MAX_MEMBERS_PER_TEAM'))
board_positions = int(os.getenv('BOARD_POSITIONS'))
dice_min = int(os.getenv('DICE_MIN'))
dice_max = int(os.getenv('DICE_MAX'))

equipos = defaultdict(list)
puntos = defaultdict(int)
orden_juego = []
turno_actual = 0
clientes = []
nombres = {}
bloqueo = threading.Lock()
jugadores_listos = set()


def broadcast(mensaje):
    for cliente, _ in clientes:
        try:
            cliente.send(json.dumps(mensaje).encode())
        except Exception as e:
            print(f"Error al enviar mensaje: {e}")


def manejar_cliente(cliente_socket, addr):
    global turno_actual
    equipo_asignado = None
    try:
        equipos_disponibles = ', '.join(equipos.keys(
        )) if equipos else "Aun no se crean equipos. Puedes crear uno nuevo."

        peers = [{"host": c[1][0], "port": c[1][1]} for c in clientes]
        peers.append({"host": addr[0], "port": addr[1]})

        cliente_socket.send(json.dumps(
            {"accion": "registrarse", "equipos_disponibles": equipos_disponibles, "peers": peers}).encode())

        data = json.loads(cliente_socket.recv(1024).decode())
        equipo_asignado = data.get("equipo")

        if equipo_asignado not in equipos:
            if len(equipos) >= max_teams:
                print(
                    f"Jugador trato de crear equipo {equipo_asignado}, maximo de equipos alcanzado")
                cliente_socket.send(json.dumps(
                    {"accion": "error", "mensaje": f"Los equipos máximos ya fueron creados. Debe unirse a uno de los siguientes equipos: {equipos_disponibles}"}).encode())
                cliente_socket.close()
                return
            else:
                equipos[equipo_asignado] = []
                print(f"Equipo creado de manera correcta: {equipo_asignado}")

        with bloqueo:
            if len(equipos[equipo_asignado]) < max_members_per_team:
                if orden_juego:
                    votos = realizar_votacion(equipo_asignado, cliente_socket)
                    if votos.count('aceptar') > votos.count('rechazar'):
                        equipos[equipo_asignado].append(cliente_socket)
                        nombres[cliente_socket] = equipo_asignado
                        clientes.append((cliente_socket, addr))
                        print(f"Nuevo jugador aceptado en {equipo_asignado}")
                    else:
                        cliente_socket.send(json.dumps(
                            {"accion": "error", "mensaje": "Jugador rechazado por votación"}).encode())
                        cliente_socket.close()
                        return
                else:
                    equipos[equipo_asignado].append(cliente_socket)
                    nombres[cliente_socket] = equipo_asignado
                    clientes.append((cliente_socket, addr))
                    print(f"Nuevo jugador en {equipo_asignado}")
            else:
                cliente_socket.send(json.dumps(
                    {"accion": "error", "mensaje": "Equipo lleno"}).encode())
                cliente_socket.close()
                return

        while True:
            try:
                data = cliente_socket.recv(1024).decode()
                if not data:
                    print("Conexión cerrada por el cliente.")
                    break
                mensaje = json.loads(data)
                accion = mensaje.get("accion")

                if accion == "listo":
                    with bloqueo:
                        jugadores_listos.add(cliente_socket)
                        total_jugadores = sum(
                            len(equipos[equipo]) for equipo in equipos)
                        if len(jugadores_listos) == total_jugadores:
                            orden_juego.extend(random.sample(
                                list(equipos.keys()), k=len(equipos)))
                            broadcast(
                                {"accion": "iniciar", "orden": orden_juego})
                            turno_actual = 0
                            anunciar_turno()

                elif accion == "tirar_dado":
                    equipo = nombres[cliente_socket]
                    with bloqueo:
                        if equipo != orden_juego[turno_actual]:
                            cliente_socket.send(json.dumps(
                                {"accion": "error", "mensaje": "No es tu turno"}).encode())
                            continue
                        tirada = random.randint(dice_min, dice_max)
                        puntos[equipo] += tirada
                        broadcast({
                            "accion": "actualizar",
                            "equipo": equipo,
                            "tirada": tirada,
                            "puntos": puntos[equipo]
                        })
                        if puntos[equipo] >= board_positions:
                            broadcast({"accion": "fin", "ganador": equipo})
                            break
                        turno_actual = (turno_actual + 1) % len(orden_juego)
                        anunciar_turno()
            except Exception as e:
                print(f"Error: {e}")
                break
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
        hilo = threading.Thread(target=manejar_cliente, args=(cliente, addr))
        hilo.start()


def realizar_votacion(equipo_asignado, nuevo_cliente):
    votos = []

    def recibir_voto(cliente):
        try:
            cliente.send(json.dumps(
                {"accion": "votar", "mensaje": f"¿Aceptar nuevo jugador en {equipo_asignado}? (aceptar/rechazar)"}).encode())
            data = cliente.recv(1024).decode()
            voto = json.loads(data).get("voto")
            if voto in ['aceptar', 'rechazar']:
                votos.append(voto)
        except Exception as e:
            print(f"Error al recibir voto: {e}")

    for miembro in equipos[equipo_asignado]:
        if miembro != nuevo_cliente:  # Don't send voting request to the new client
            recibir_voto(miembro)

    return votos


if __name__ == "__main__":
    iniciar_servidor()
