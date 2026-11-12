# MiMascota Desktop · Interfaz profesional

Aplicación de escritorio para gestión veterinaria, desarrollada con **Python y CustomTkinter**. Esta entrega corresponde al frontend de escritorio y está preparada para consumir una API REST del backend del equipo.

> La aplicación de escritorio se ejecuta en el computador del usuario. El backend y MySQL se ejecutan en la máquina virtual Ubuntu de Azure. La interfaz no se conecta directamente a MySQL.

## Módulos incluidos

- **Panel principal:** indicadores operativos, agenda próxima, alertas de vacunación y accesos rápidos.
- **Propietarios:** alta, consulta, edición, búsqueda y desactivación lógica.
- **Mascotas:** ficha del paciente, propietario, especie, raza, nacimiento, sexo y estado.
- **Veterinarios:** profesionales, registro, especialidad y contacto.
- **Servicios:** catálogo, descripción, precio y duración.
- **Citas y agenda:** programación, consulta, edición, cancelación y registro de atención.
- **Historial clínico:** diagnóstico, tratamiento, peso, medicamentos y observaciones.
- **Vacunación:** registro de dosis y control de próximas aplicaciones.

## Mejoras de esta versión

- Diseño visual unificado con barra lateral, navegación por secciones y encabezado contextual.
- Panel principal renovado con tarjetas de indicadores, agenda, alertas y accesos rápidos.
- Tablas con filas alternadas, encabezados estilizados, filtros, búsqueda y recarga.
- Exportación de los registros filtrados a CSV compatible con Excel.
- Formularios modales con jerarquía visual, campos obligatorios, validación de fechas, hora, correo y valores numéricos.
- Atajos de teclado: `Ctrl + F` enfoca la búsqueda, `Ctrl + N` inicia un registro y `F5` actualiza la vista.
- Persistencia de los datos de demostración en un archivo JSON local.
- Separación entre interfaz, servicio de datos, repositorio de demostración y cliente HTTP.

## Requisitos

- Windows 10/11, Linux o macOS.
- Python 3.10 o superior.
- Dependencias declaradas en `requirements.txt`.

## Instalación en Windows

1. Descomprime el ZIP.
2. Abre PowerShell dentro de la carpeta `MiMascota_Desktop`.
3. Ejecuta:

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python main.py
```

Si ya creaste el entorno virtual y tienes las dependencias instaladas, no repitas la instalación. Para volver a ejecutar la aplicación en otra sesión:

```powershell
.\.venv\Scripts\Activate.ps1
python main.py
```

Si PowerShell bloquea la activación, ejecuta primero `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` en esa misma ventana. También se incluye `INICIAR_MIMASCOTA.bat` para iniciar la aplicación con doble clic después de instalar las dependencias.

## Modo demostración

Por defecto, `.env.example` establece:

```ini
MIMASCOTA_DEMO_MODE=true
```

En este modo se utilizan datos ficticios almacenados localmente en `mimascota/data/demo_data.json`. Puedes probar navegación, formularios, edición, desactivación, citas y alertas sin conexión a Azure. No introduzcas datos personales reales en el modo de demostración.

## Conectar con la API del equipo

Cuando el backend esté disponible:

1. Solicita la URL base, autenticación y endpoints definitivos.
2. Compara el backend con `docs/CONTRATO_API_PARA_BACKEND.md`.
3. Configura `.env`:

```ini
MIMASCOTA_DEMO_MODE=false
MIMASCOTA_API_BASE_URL=https://DOMINIO_DEL_SERVIDOR/api
MIMASCOTA_REQUEST_TIMEOUT=15
MIMASCOTA_API_TOKEN=
```

4. Si el backend exige un token Bearer, configura `MIMASCOTA_API_TOKEN` localmente. No compartas `.env`, contraseñas ni tokens.
5. Cierra y vuelve a abrir la aplicación.

El cliente espera respuestas JSON y los endpoints definidos en el contrato. El backend debe aplicar las reglas de negocio y las transacciones; las validaciones de la interfaz no sustituyen las validaciones del servidor.

## Reglas de negocio que debe respetar el backend

- Una mascota pertenece a un solo propietario a la vez y los cambios de dueño deben quedar registrados.
- Un veterinario no puede tener citas con horarios cruzados.
- Una cita atendida debe generar exactamente un registro clínico.
- No se debe registrar una vacuna con fecha futura ni para una mascota inactiva.
- Los registros con historial no se eliminan físicamente: se desactivan cuando corresponda.

## Alcance de la entrega

Esta versión entrega la interfaz de escritorio y el cliente de integración. La conexión real con Azure no se considera verificada hasta que el backend publique los endpoints del contrato, responda correctamente y se realicen pruebas de extremo a extremo.
