import socket
import sys

def iniciar_cliente(host='localhost', puerto=5000):
    # Configuración del socket TCP/IP (Cliente)
    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        cliente_socket.connect((host, puerto))
        print(f"Conectado exitosamente al servidor {host}:{puerto}")
        print("Escribe tus mensajes. Ingresa la palabra 'éxito' para finalizar la sesión.\n")

        while True:
            # Captura de mensaje del usuario
            mensaje = input("Tú: ")

            # Verificamos si el usuario desea salir del bucle
            if mensaje.strip().lower() == 'éxito':
                print("Desconectando del servidor...")
                break

            # Evitamos enviar mensajes vacíos
            if mensaje.strip():
                # Enviamos la data codificada
                cliente_socket.sendall(mensaje.encode('utf-8'))

                # Quedamos a la espera de la confirmación del servidor
                respuesta = cliente_socket.recv(1024)
                print(f"Servidor dice -> {respuesta.decode('utf-8')}")

    except ConnectionRefusedError:
        print(f"Error: No se pudo conectar a {host}:{puerto}. Verifica que el servidor esté activo.")
    except Exception as e:
        print(f"Error en el cliente: {e}")
    finally:
        cliente_socket.close()
        sys.exit(0)

if __name__ == "__main__":
    iniciar_cliente()