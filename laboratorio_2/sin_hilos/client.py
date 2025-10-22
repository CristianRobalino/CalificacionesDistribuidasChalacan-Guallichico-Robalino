import socket
import json

def mostrar_menu():
    print("\n--- Menú de Calificaciones ---")
    print("1. Agregar calificación")
    print("2. Buscar por ID")
    print("3. Actualizar calificación")
    print("4. Listar todas")
    print("5. Eliminar por ID")
    print("6. Salir")
    try:
        return input("Elija opción: ")
    except (KeyboardInterrupt, EOFError):
        # El usuario presionó Ctrl+C o Ctrl+Z/EOF — tratar como salir
        print("\nEntrada interrumpida. Saliendo...")
        return '6'


def enviar_comando(comando):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('localhost', 12345))
        client_socket.send(comando.encode('utf-8'))
        respuesta = client_socket.recv(4096).decode('utf-8')
    finally:
        client_socket.close()
    try:
        return json.loads(respuesta)
    except Exception:
        return {"status": "error", "mensaje": "Respuesta no válida del servidor"}


def main():
    while True:
        opcion_str = mostrar_menu()
        # intentar convertir a entero, manejar entrada inválida
        try:
            opcion = int(opcion_str)
        except ValueError:
            print("Opción inválida (debe ser un número). Intente de nuevo.")
            continue

        if opcion == 1:
            try:
                id_est = input("ID: ")
                nombre = input("Nombre: ")
                materia = input("Materia: ")
                calif = input("Calificación: ")
            except (KeyboardInterrupt, EOFError):
                print("\nEntrada interrumpida. Volviendo al menú...")
                continue
            res = enviar_comando(f"AGREGAR|{id_est}|{nombre}|{materia}|{calif}")
            print(res.get("mensaje", "Sin mensaje"))
            
        elif opcion == 2:
            id_est = input("ID: ")
            res = enviar_comando(f"BUSCAR|{id_est}")
            if res.get("status") == "ok":
                data = res.get('data', {})
                print(f"Nombre: {data.get('Nombre')}, Materia: {data.get('Materia')}, Calificación: {data.get('Calificacion')}")
            
        elif opcion == 3:
            id_est = input("ID: ")
            nueva_calif = input("Nueva calificación: ")
            res = enviar_comando(f"ACTUALIZAR|{id_est}|{nueva_calif}")
            print(res.get("mensaje", "Sin mensaje"))
            
        elif opcion == 4:
            res = enviar_comando("LISTAR")
            if res.get("status") == "ok":
                for row in res.get("data", []):
                    print(row)
            else:
                print(res.get("mensaje", "Sin mensaje"))
        elif opcion == 5:
            id_est = input("ID: ")
            res = enviar_comando(f"ELIMINAR|{id_est}")
            print(res.get("mensaje", "Sin mensaje"))
        elif opcion == 6:
            print("Saliendo...")
            break
        else:
            print("Opción inválida")


if __name__ == '__main__':
    main()
