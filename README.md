## Distribuidos-p2p-problema B1 y B2 

## Intrgrantes del grupo: Bastian Gavilan y Martin Suarez


## Tecnologías utilizadas

 **Python**: tanto para el cliente como para el servidor.
 **Sockets TCP**: para la comunicación directa entre cliente y servidor.
 **Threading**: para manejar múltiples jugadores simultáneamente.
 **JSON**: como formato de intercambio de mensajes y activacion de comandos.
 **dotenv**: para parametrizar fácilmente el entorno del juego, incluye atributos como cantidad maxima de euqipos, casillas en tablero, numeros minimos y maximos del dado, etc.
 **Sistema de RMI**: se simula RMI simplemente usando un socket adicional para enviar eventos desde el servidor a un servicio de log externo que genera un arrchivo con los pricnipales eventos.

## Estructura general

servidor.py: maneja las conexiones, controla el flujo del juego y coordina los turnos.
cliente.py: se conecta al servidor, participa en el juego y envía acciones.
log_rmi.py: actúa como receptor de logs enviados desde el servidor, guardando los eventos con marcas de tiempo.
  
## Lógica del juego 

1. Cada jugador se conecta al servidor y se une a un equipo existente o crea uno nuevo (si aún hay cupos).
2. Todos los jugadores indican cuándo están listos.
3. Se inicia el juego y los equipos juegan por turnos.
4. En cada turno, un miembro del equipo lanza el dado.
5. El servidor actualiza los puntajes y revisa si algún equipo ganó.
6. Todos los eventos importantes (jugador se une, dado lanzado, juego finalizado, etc.) se envían al servicio de log RMI.