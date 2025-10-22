import socket
import csv
import json
import os
import pathlib
import threading

# Ruta del CSV relativa al directorio del script (dos niveles arriba está el CSV)
ARCHIVO_CSV = str(pathlib.Path(__file__).parent.joinpath('..', 'calificaciones.csv').resolve())


def inicializar_csv():
    if not os.path.exists(ARCHIVO_CSV):
        with open(ARCHIVO_CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID_Estudiante', 'Nombre', 'Materia', 'Calificacion'])


def consultar_nrc(nrc):
    """Consulta al servicio de NRCs en localhost:12346.
    Retorna el objeto JSON parseado o un dict con status:error en caso de fallo.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        s.connect(('localhost', 12346))
        mensaje = f"BUSCAR NRC|{nrc}"
        s.send(mensaje.encode('utf-8'))
        respuesta = s.recv(4096).decode('utf-8')
        s.close()
        try:
            return json.loads(respuesta)
        except Exception:
            return {"status": "error", "mensaje": "Respuesta inválida del servicio NRC"}
    except Exception as e:
        return {"status": "error", "mensaje": f"Fallo conexión NRC: {e}"}


def agregar_calificacion(id_est, nombre, materia, calif):
    # Validar NRC/Materia usando servicio externo
    res_nrc = consultar_nrc(materia)
    if res_nrc.get('status') != 'ok':
        return {"status": "error", "mensaje": "Materia/NRC no válida"}
    try:
        with open(ARCHIVO_CSV, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([id_est, nombre, materia, calif])
        return {"status": "ok", "mensaje": f"Calificación agregada para {nombre}"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}


def buscar_por_id(id_est):
    try:
        with open(ARCHIVO_CSV, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['ID_Estudiante'] == id_est:
                    return {"status": "ok", "data": row}
            return {"status": "not_found", "mensaje": "ID no encontrado"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}


def actualizar_calificacion(id_est, nueva_calif):
    try:
        rows = []
        found = False
        with open(ARCHIVO_CSV, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['ID_Estudiante'] == id_est:
                    # Si la "nueva_calif" viene como materia/NRC en algunos casos no aplica;
                    # aquí asumimos que actualizar_calificacion sólo recibe la nueva calificación.
                    row['Calificacion'] = nueva_calif
                    found = True
                rows.append(row)
        if not found:
            return {"status": "not_found", "mensaje": "ID no encontrado"}
        with open(ARCHIVO_CSV, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['ID_Estudiante', 'Nombre', 'Materia', 'Calificacion'])
            writer.writeheader()
            writer.writerows(rows)
        return {"status": "ok", "mensaje": f"Calificación actualizada a {nueva_calif}"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}


def listar_todas():
    try:
        with open(ARCHIVO_CSV, 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        return {"status": "ok", "data": data}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}


def eliminar_por_id(id_est):
    try:
        rows = []
        found = False
        with open(ARCHIVO_CSV, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['ID_Estudiante'] != id_est:
                    rows.append(row)
                else:
                    found = True
        if not found:
            return {"status": "not_found", "mensaje": "ID no encontrado"}
        with open(ARCHIVO_CSV, 'w', newline='') as f:

            writer = csv.DictWriter(f, fieldnames=['ID_Estudiante', 'Nombre', 'Materia', 'Calificacion'])
            writer.writeheader()
            writer.writerows(rows)
        return {"status": "ok", "mensaje": f"Registro eliminado para ID {id_est}"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}


def procesar_comando(comando):
    partes = comando.strip().split('|')
    op = partes[0]
    if op == "AGREGAR" and len(partes) == 5:
        return agregar_calificacion(partes[1], partes[2], partes[3], partes[4])
    elif op == "BUSCAR" and len(partes) == 2:
        return buscar_por_id(partes[1])
    elif op == "ACTUALIZAR" and len(partes) == 3:
        return actualizar_calificacion(partes[1], partes[2])
    elif op == "LISTAR":
        return listar_todas()
    elif op == "ELIMINAR" and len(partes) == 2:
        return eliminar_por_id(partes[1])
    else:
        return {"status": "error", "mensaje": "Comando inválido"}


def manejar_cliente(client_socket, addr):
    print(f"Cliente conectado desde {addr} en hilo {threading.current_thread().name}")
    try:
        data = client_socket.recv(4096).decode('utf-8')
        if data:
            respuesta = procesar_comando(data)
            client_socket.send(json.dumps(respuesta).encode('utf-8'))
    except Exception as e:
        print(f"Error en hilo: {e}")
    finally:
        client_socket.close()
        print(f"Cliente {addr} desconectado.")


if __name__ == '__main__':
    inicializar_csv()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12345))
    server_socket.listen(5)  # Cola para múltiples conexiones
    print("Servidor concurrente escuchando en puerto 12345...")
    try:
        while True:
            client_socket, addr = server_socket.accept()
            hilo = threading.Thread(target=manejar_cliente, args=(client_socket, addr), daemon=True)
            hilo.start()
    except KeyboardInterrupt:
        print("Servidor detenido.")
    finally:
        server_socket.close()
