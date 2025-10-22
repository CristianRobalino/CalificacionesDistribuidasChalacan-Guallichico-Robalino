import socket
import csv
import json
import os
import pathlib

# Archivo nrcs.csv en el mismo directorio `laboratorio_2`
ARCHIVO_NRCS = str(pathlib.Path(__file__).parent.joinpath('nrcs.csv').resolve())


def inicializar_nrcs():
    if not os.path.exists(ARCHIVO_NRCS):
        with open(ARCHIVO_NRCS, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['NRC', 'Materia'])
            # Ejemplo de NRCs
            writer.writerow(['MAT101', 'Matematicas'])
            writer.writerow(['FIS201', 'Fisica'])


def buscar_nrc(nrc):
    try:
        with open(ARCHIVO_NRCS, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['NRC'] == nrc:
                    return {"status": "ok", "data": row}
            return {"status": "not_found", "mensaje": "NRC no encontrado"}
    except Exception as e:
        return {"status": "error", "mensaje": str(e)}


def procesar_comando(comando):
    partes = comando.strip().split('|')
    op = partes[0]
    if op == 'BUSCAR NRC' and len(partes) == 2:
        return buscar_nrc(partes[1])
    elif op == 'LISTAR':
        try:
            with open(ARCHIVO_NRCS, 'r') as f:
                reader = csv.DictReader(f)
                data = list(reader)
            return {"status": "ok", "data": data}
        except Exception as e:
            return {"status": "error", "mensaje": str(e)}
    else:
        return {"status": "error", "mensaje": "Comando invalido"}


def main():
    inicializar_nrcs()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12346))
    server_socket.listen(1)
    print('Servidor NRCs escuchando en puerto 12346...')
    try:
        while True:
            client_socket, addr = server_socket.accept()
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if data:
                    respuesta = procesar_comando(data)
                    client_socket.send(json.dumps(respuesta).encode('utf-8'))
            except Exception as e:
                client_socket.send(json.dumps({"status": "error", "mensaje": str(e)}).encode('utf-8'))
            finally:
                client_socket.close()
    except KeyboardInterrupt:
        print('Servidor NRCs detenido.')
    finally:
        server_socket.close()


if __name__ == '__main__':
    main()
