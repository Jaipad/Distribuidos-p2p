from datetime import datetime

LOG_FILE = "eventos_del juego.log"

def registrar_evento(origen, mensaje):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entrada = f"[{timestamp}] [{origen}] {mensaje}"
    print(entrada)  # Muestra en consola
    with open(LOG_FILE, "a") as f:
        f.write(entrada + "\n")
