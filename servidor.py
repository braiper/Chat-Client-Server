import socket
import sqlite3
import datetime
import sys

# ==========================================
# MÓDULO DE BASE DE DATOS
# ==========================================

def inicializar_db():
    """Crea la base de datos y la tabla si no existen."""
    try:
        conexion = sqlite3.connect('chat.db')
        cursor = conexion.cursor()
        # Se crean los campos: id, contenido, fecha_envio, ip_cliente
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contenido TEXT NOT NULL,
                fecha_envio TEXT NOT NULL,
                ip_cliente TEXT NOT NULL
            )
        ''')
        conexion.commit()
        conexion.close()
        print("Base de datos SQLite inicializada correctamente.")
    except sqlite3.Error as e:
        print(f"Error grave: DB no accesible. Detalle: {e}")
        sys.exit(1) # Salimos si no hay acceso a DB

def guardar_mensaje(contenido, fecha_envio, ip_cliente):
    """Guarda cada mensaje recibido en la base de datos."""
    try:
        conexion = sqlite3.connect('chat.db')
        cursor = conexion.cursor()
        cursor.execute('''
            INSERT INTO mensajes (contenido, fecha_envio, ip_cliente)
            VALUES (?, ?, ?)
        ''', (contenido, fecha_envio, ip_cliente))
        conexion.commit()
        conexion.close()
    except sqlite3.Error as e:
        print(f"Error al guardar el mensaje en la DB: {e}")

# ==========================================
# MÓDULO DE RED (SOCKETS)
# ==========================================

def inicializar_socket(host='localhost', puerto=5000):
    """Inicializa el socket para escuchar en el puerto especificado."""
    try:
        # Configuración del socket TCP/IP
        servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Permitir reutilizar la dirección local (evita error de puerto ocupado inmediato tras reinicio)
        servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        servidor_socket.bind((host, puerto))
        servidor_socket.listen(5)
        print(f"Servidor escuchando exitosamente en {host}:{puerto}")
        return servidor_socket
    except OSError as e:
        # Manejo de error específico (ej: puerto ocupado)
        print(f"Error al iniciar el servidor (¿Puerto {puerto} ocupado?): {e}")
        sys.exit(1)

def aceptar_y_recibir(servidor_socket):
    """Acepta conexiones entrantes y recibe mensajes en un bucle."""
    while True:
        try:
            # Aceptamos la conexión
            cliente_socket, direccion_cliente = servidor_socket.accept()
            ip_cliente = direccion_cliente[0]
            print(f"\n[+] Nueva conexión entrante desde: {ip_cliente}")

            while True:
                mensaje_bytes = cliente_socket.recv(1024)
                
                # Si no hay datos, el cliente cerró la conexión
                if not mensaje_bytes:
                    print(f"[-] Cliente {ip_cliente} desconectado.")
                    break
                
                contenido = mensaje_bytes.decode('utf-8')
                print(f"Mensaje de {ip_cliente}: {contenido}")

                # Generamos timestamp exacto del momento de recepción
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Guardamos el registro en DB
                guardar_mensaje(contenido, timestamp, ip_cliente)

                # Respondemos al cliente el formato solicitado
                respuesta = f"Mensaje recibido: {timestamp}"
                cliente_socket.sendall(respuesta.encode('utf-8'))

            cliente_socket.close()

        except KeyboardInterrupt:
            print("\nServidor apagado manualmente.")
            break
        except Exception as e:
            print(f"Error inesperado al manejar la conexión con {ip_cliente}: {e}")

# ==========================================
# PUNTO DE ENTRADA PRINCIPAL
# ==========================================
if __name__ == "__main__":
    inicializar_db()
    socket_activo = inicializar_socket('localhost', 5000)
    
    if socket_activo:
        aceptar_y_recibir(socket_activo)
        socket_activo.close()