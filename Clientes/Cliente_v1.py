import socket
import json
import threading

HOST = 'localhost'
PORT = 5000

def escuchar_servidor(sock):
    while True:
        try:
            data = sock.recv(1024).decode()
            if not data:
                break
            mensaje = json.loads(data)
            accion = mensaje.get("accion")

            if accion == "registrarse":
                equipo = input("Ingresa tu equipo (Equipo1 o Equipo2): ")
                equipo_local = equipo
                sock.send(json.dumps({"equipo": equipo}).encode())

            elif accion == "iniciar":
                print(f"Juego iniciado. Orden: {mensaje['orden']}")

            elif accion == "turno":
                print(f"Turno del equipo: {mensaje['equipo']}")
                if mensaje['equipo'] == equipo_local:
                    input("Presiona Enter para lanzar el dado...")
                    sock.send(json.dumps({"accion": "tirar_dado"}).encode())

            elif accion == "actualizar":
                print(f"{mensaje['equipo']} lanzó y avanzó {mensaje['tirada']} puntos. Total: {mensaje['puntos']}")

            elif accion == "fin":
                print(f"¡El equipo {mensaje['ganador']} ha ganado!")
                break

            elif accion == "error":
                print(f"Error: {mensaje['mensaje']}")
        except Exception as e:
            print(f"Error de conexión: {e}")
            break

if __name__ == "__main__":
    equipo_local = None
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    hilo = threading.Thread(target=escuchar_servidor, args=(sock,))
    hilo.start()
    hilo.join()
