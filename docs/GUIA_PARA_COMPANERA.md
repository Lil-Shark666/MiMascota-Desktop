# Entrega de interfaz de escritorio — MiMascota

## Alcance de esta entrega

Este paquete contiene **el frontend de escritorio** en Python con CustomTkinter. Incluye navegación, dashboard, tablas, formularios, búsqueda, edición, desactivación lógica de registros y una capa cliente para consumir una API REST.

El `main.py` del ZIP solo inicia la interfaz en el computador; no es el proceso de backend que se ejecutará como servicio `systemd` en la VM.

No incluye el backend, la conexión directa a MySQL, la máquina virtual Azure ni el servicio `systemd`. Esos componentes quedan del lado de quien desarrolla y despliega el backend.

## Qué recibe la compañera

1. Código fuente ejecutable de la interfaz de escritorio.
2. Modo de demostración con datos ficticios persistidos en `data/demo_data.json`.
3. Cliente HTTP intercambiable mediante variables de entorno.
4. Contrato de endpoints y JSON en `CONTRATO_API_PARA_BACKEND.md`.

## Qué debe entregar el backend para integrar

- URL base accesible desde el computador donde se ejecute la interfaz.
- Endpoints REST descritos en el contrato.
- Campos JSON compatibles o un acuerdo de mapeo.
- Autenticación y protocolo de acceso que defina el equipo.
- Validación en servidor de las cinco reglas de negocio.
- Servicio desplegado en Ubuntu con systemd, si corresponde a la responsabilidad del equipo.

## Texto breve para acompañar el ZIP

> Te comparto la interfaz de escritorio de MiMascota desarrollada en Python con CustomTkinter. Incluye los módulos de propietarios, mascotas, veterinarios, servicios, citas, historial clínico y vacunación. Por ahora funciona en modo demostración con datos ficticios. La aplicación está preparada para consumir una API REST, sin conectarse directamente a MySQL. Adjunto el contrato de integración con los endpoints y formatos JSON que necesita el cliente. Cuando tengas la URL y los endpoints reales del backend, configuramos la conexión y probamos cada módulo.
