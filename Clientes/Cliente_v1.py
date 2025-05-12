import socket
import json
import threading

HOST = 'localhost'
PORT = 5000


def escuchar_servidor(sock, peers):
    equipo_local = None
    jugadores_listos = set()
    total_jugadores = len(peers) + 1

    def enviar_a_peers(mensaje):
        for peer in peers:
            try:
                peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                peer_sock.connect((peer['host'], peer['port']))
                peer_sock.send(json.dumps(mensaje).encode())
                peer_sock.close()
            except Exception as e:
                print(f"Error al enviar a {peer}: {e}")

    while True:
        try:
            data = sock.recv(1024).decode()
            if not data:
                print("Conexión cerrada por el servidor.")
                break
            mensaje = json.loads(data)
            accion = mensaje.get("accion")

            if accion == "registrarse":
                equipo = input("Ingresa tu equipo: ")
                equipo_local = equipo
                sock.send(json.dumps({"equipo": equipo}).encode())
                peers = mensaje.get("peers", [])
                print(f"Peers: {peers}")
                input(
                    "Escribe 'listo' y presiona Enter para indicar que estás listo para comenzar...")
                sock.send(json.dumps({"accion": "listo"}).encode())
                print("Esperando a los demás jugadores...")

            elif accion == "iniciar":
                print(f"Juego iniciado. Orden: {mensaje['orden']}")

            elif accion == "turno":
                print(f"Turno del equipo: {mensaje['equipo']}")
                if mensaje['equipo'] == equipo_local:
                    input("Presiona Enter para lanzar el dado...")
                    sock.send(json.dumps({"accion": "tirar_dado"}).encode())

            elif accion == "actualizar":
                print(
                    f"{mensaje['equipo']} lanzó y avanzó {mensaje['tirada']} puntos. Total: {mensaje['puntos']}")

            elif accion == "fin":
                print(f"¡El equipo {mensaje['ganador']} ha ganado!")
                break

            elif accion == "error":
                print(f"Error: {mensaje['mensaje']}")

            elif accion == "votar":
                voto = input(f"{mensaje['mensaje']} (aceptar/rechazar): ")
                sock.send(json.dumps(
                    {"accion": "voto", "voto": voto}).encode())

        except Exception as e:
            print(f"Error de conexión: {e}")
            break


if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    hilo = threading.Thread(target=escuchar_servidor, args=(sock, []))
    hilo.start()
    hilo.join()
