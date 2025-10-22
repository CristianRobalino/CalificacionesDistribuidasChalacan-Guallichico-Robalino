# Sistema de Gestión de Calificaciones - Laboratorio 2

## Descripción del Proyecto

Sistema distribuido cliente-servidor para la gestión de calificaciones estudiantiles. El proyecto implementa un servidor TCP que procesa solicitudes de clientes para realizar operaciones CRUD (Crear, Leer, Actualizar, Eliminar) sobre un archivo CSV compartido que almacena las calificaciones.

## Arquitectura del Sistema

### Modelo Cliente-Servidor

El sistema sigue una arquitectura cliente-servidor con las siguientes características:

- **Protocolo de Comunicación**: TCP/IP (Sockets)
- **Puerto**: 12345
- **Host**: localhost
- **Formato de Datos**: JSON para respuestas, comandos delimitados por `|` para peticiones
- **Persistencia**: Archivo CSV compartido (`calificaciones.csv`) en el directorio raíz del laboratorio

## Estructura del Proyecto

```
laboratorio_2/
├── README.md              # Documentación del proyecto
├── calificaciones.csv     # Archivo CSV compartido (persistencia)
├── sin_hilos/             # Implementación secuencial (actual)
│   ├── server.py          # Servidor TCP secuencial
│   └── client.py          # Cliente interactivo mejorado
└── con_hilos/             # Implementación futura con hilos (vacío)
    ├── server.py
    └── client.py
```

## Descripción de Archivos

### `sin_hilos/server.py` - Servidor TCP Secuencial

Servidor que escucha conexiones en el puerto 12345 y procesa comandos de forma secuencial (un cliente a la vez). Utiliza rutas relativas para acceder al archivo CSV compartido en el directorio padre.

#### Funciones Principales:

- **`inicializar_csv()`**: Crea el archivo CSV con encabezados si no existe en el directorio raíz
- **`agregar_calificacion(id_est, nombre, materia, calif)`**: Agrega un nuevo registro de calificación
- **`buscar_por_id(id_est)`**: Busca y retorna los datos de un estudiante por su ID
- **`actualizar_calificacion(id_est, nueva_calif)`**: Actualiza la calificación de un estudiante existente
- **`listar_todas()`**: Retorna todas las calificaciones almacenadas como lista de diccionarios
- **`eliminar_por_id(id_est)`**: Elimina el registro de un estudiante por su ID
- **`procesar_comando(comando)`**: Parsea y ejecuta comandos recibidos del cliente

#### Características Técnicas:

- Usa `pathlib` para manejar rutas de forma robusta y multiplataforma
- El archivo CSV se ubica en `laboratorio_2/calificaciones.csv` (directorio padre)
- Manejo de excepciones en todas las operaciones de archivo

#### Formato de Comandos:

Los comandos se envían como strings delimitados por `|`:

- `AGREGAR|ID|Nombre|Materia|Calificacion`
- `BUSCAR|ID`
- `ACTUALIZAR|ID|NuevaCalificacion`
- `LISTAR`
- `ELIMINAR|ID`

#### Formato de Respuestas:

Todas las respuestas son objetos JSON con la estructura:

```json
{
  "status": "ok|error|not_found",
  "mensaje": "Descripción del resultado",
  "data": {}  // Opcional, solo en consultas
}
```

### `sin_hilos/client.py` - Cliente Interactivo Mejorado

Cliente con interfaz de menú que permite al usuario interactuar con el servidor de forma intuitiva. Incluye manejo robusto de errores y excepciones.

#### Funciones Principales:

- **`mostrar_menu()`**: Muestra el menú de opciones disponibles y maneja interrupciones (Ctrl+C)
- **`enviar_comando(comando)`**: Establece conexión con el servidor, envía comando y retorna respuesta parseada
- **`main()`**: Función principal que ejecuta el bucle del menú

#### Opciones del Menú:

1. **Agregar calificación**: Solicita ID, nombre, materia y calificación
2. **Buscar por ID**: Busca y muestra los datos de un estudiante
3. **Actualizar calificación**: Modifica la calificación de un estudiante existente
4. **Listar todas**: Muestra todas las calificaciones registradas
5. **Eliminar por ID**: Elimina el registro de un estudiante
6. **Salir**: Cierra el cliente

#### Mejoras Implementadas:

- **Manejo de interrupciones**: Captura `KeyboardInterrupt` y `EOFError` para salir limpiamente
- **Validación de entrada**: Verifica que las opciones sean números válidos
- **Manejo de errores de conexión**: Usa bloques `try-finally` para cerrar sockets correctamente
- **Buffer ampliado**: Recibe hasta 4096 bytes para respuestas grandes
- **Acceso seguro a diccionarios**: Usa `.get()` para evitar errores de clave no encontrada

## Cómo Ejecutar el Proyecto

### Requisitos Previos

- Python 3.x instalado
- Módulos estándar de Python (socket, csv, json, os, pathlib)

### Pasos para Ejecutar

#### 1. Iniciar el Servidor

Abrir una terminal y ejecutar:

```bash
cd laboratorio_2/sin_hilos
python server.py
```

Salida esperada:
```
Servidor secuencial escuchando en puerto 12345...
```

#### 2. Iniciar el Cliente

En una **nueva terminal**, ejecutar:

```bash
cd laboratorio_2/sin_hilos
python client.py
```

Aparecerá el menú interactivo:
```
--- Menú de Calificaciones ---
1. Agregar calificación
2. Buscar por ID
3. Actualizar calificación
4. Listar todas
5. Eliminar por ID
6. Salir
Elija opción:
```

#### 3. Interactuar con el Sistema

Seleccionar las opciones del menú e ingresar los datos solicitados.

**Ejemplo de uso:**

```
Elija opción: 1
ID: 001
Nombre: Juan Pérez
Materia: Matemáticas
Calificación: 95
```

### Detener el Servidor

Presionar `Ctrl+C` en la terminal del servidor para detenerlo de forma segura.

## Persistencia de Datos

El archivo `calificaciones.csv` se crea automáticamente en el directorio `con_hilos/` con la siguiente estructura:

```csv
ID_Estudiante,Nombre,Materia,Calificacion
001,Juan Pérez,Matemáticas,95
002,María López,Física,88
```

## Características Técnicas

### Implementación Actual (No Recurrente)

- **Modelo**: Servidor secuencial que atiende un cliente a la vez
- **Concurrencia**: No soporta múltiples clientes simultáneos
- **Conexión**: El cliente se conecta, envía un comando, recibe respuesta y se desconecta
- **Bloqueo**: El servidor se bloquea esperando cada cliente

### Ventajas

- Simplicidad en la implementación
- No requiere manejo de concurrencia
- Fácil de depurar y entender

### Limitaciones

- Solo puede atender un cliente a la vez
- Los demás clientes deben esperar en cola
- No escalable para múltiples usuarios simultáneos

## Próximos Pasos

La carpeta `sin_hilos/` está preparada para implementar una versión con hilos que permita:

- Atención simultánea de múltiples clientes
- Mejor rendimiento y escalabilidad
- Manejo de concurrencia en operaciones de archivo

## Autores

- Chalacan
- Guallichico
- Robalino

## Notas Adicionales

- El servidor debe estar corriendo antes de ejecutar el cliente
- Cada operación del cliente abre y cierra una nueva conexión
- Los datos persisten en el archivo CSV entre ejecuciones
- El servidor imprime logs de conexiones y desconexiones en la consola
