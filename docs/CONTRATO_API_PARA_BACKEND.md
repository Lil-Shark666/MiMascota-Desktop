# Contrato de integración — MiMascota Escritorio

Este documento se entrega a la persona responsable del backend. La aplicación de escritorio consume una API HTTP/JSON; **no abre conexiones MySQL y no contiene credenciales de la base de datos**.

## 1. URL base

La aplicación lee la URL desde `.env`:

```ini
MIMASCOTA_DEMO_MODE=false
MIMASCOTA_API_BASE_URL=https://HOST_O_IP_DEL_SERVIDOR/api
MIMASCOTA_REQUEST_TIMEOUT=12
MIMASCOTA_API_TOKEN=
```

Si se utiliza autenticación Bearer, la interfaz enviará `Authorization: Bearer <token>` cuando `MIMASCOTA_API_TOKEN` tenga un valor.

La URL es ilustrativa. La compañera de backend debe comunicar la URL y el puerto reales, junto con el mecanismo de autenticación que acuerde el equipo.

## 2. Endpoints esperados

Todas las rutas se encuentran bajo `/api`.

| Recurso | GET colección | POST crear | PUT actualizar | DELETE lógico |
|---|---|---|---|---|
| Propietarios | `/owners` | `/owners` | `/owners/{id}` | `/owners/{id}` |
| Mascotas | `/pets` | `/pets` | `/pets/{id}` | `/pets/{id}` |
| Veterinarios | `/vets` | `/vets` | `/vets/{id}` | `/vets/{id}` |
| Servicios | `/services` | `/services` | `/services/{id}` | `/services/{id}` |
| Citas | `/appointments` | `/appointments` | `/appointments/{id}` | No usar; cancelar con ruta específica |
| Historial clínico | `/records` | No crear directamente | `/records/{id}` | No exponer borrado |
| Vacunación | `/vaccines` | `/vaccines` | `/vaccines/{id}` | No requerido por esta interfaz |
| Salud | `/health` | — | — | — |

Acciones especiales:

- `POST /appointments/{id}/cancel`: marca la cita como `Cancelada`.
- `POST /appointments/{id}/attend`: registra la atención clínica y cambia la cita a `Atendida` en **una sola transacción SQL**.

La aplicación acepta para GET colección un arreglo JSON directo (`[...]`) o un objeto con la propiedad `items` (`{"items": [...]}`). Las operaciones de creación y actualización deben devolver el registro resultante como objeto JSON. DELETE y acciones pueden responder `204 No Content`.

## 3. Campos que consume la interfaz

Los nombres siguientes forman el contrato del cliente de escritorio. El backend puede mapearlos a nombres distintos en las tablas SQL, pero debe conservar estos nombres en el JSON o coordinar el cambio con el frontend.

### Propietario — `/owners`

```json
{
  "id": 1,
  "full_name": "Laura Méndez",
  "document_type": "CC",
  "document_number": "1061700234",
  "phone": "3004567812",
  "email": "laura@email.com",
  "address": "Centro",
  "active": true,
  "status": "Activo"
}
```

### Mascota — `/pets`

```json
{
  "id": 12,
  "name": "Luna",
  "owner_id": 1,
  "owner_name": "Laura Méndez",
  "species": "Perro",
  "breed": "Golden Retriever",
  "birth_date": "2021-04-12",
  "sex": "Hembra",
  "status": "Activa",
  "active": true,
  "notes": "Control preventivo"
}
```

### Veterinario — `/vets`

```json
{
  "id": 4,
  "full_name": "Dra. María Ruiz",
  "license_number": "TP-45871",
  "specialty": "Medicina general",
  "phone": "3105550101",
  "email": "veterinaria@email.com",
  "active": true,
  "status": "Activo"
}
```

### Servicio — `/services`

```json
{
  "id": 2,
  "name": "Consulta general",
  "description": "Valoración clínica general",
  "price": 65000,
  "duration_minutes": 30,
  "active": true,
  "status": "Activo"
}
```

### Cita — `/appointments`

```json
{
  "id": 31,
  "pet_id": 12,
  "pet_name": "Luna",
  "owner_id": 1,
  "owner_name": "Laura Méndez",
  "vet_id": 4,
  "vet_name": "Dra. María Ruiz",
  "service_id": 2,
  "service_name": "Consulta general",
  "appointment_date": "2026-11-12",
  "appointment_time": "09:30",
  "status": "Confirmada",
  "notes": "Control general"
}
```

### Historial clínico — `/records`

```json
{
  "id": 51,
  "appointment_id": 31,
  "pet_id": 12,
  "pet_name": "Luna",
  "vet_id": 4,
  "vet_name": "Dra. María Ruiz",
  "created_at": "2026-11-12",
  "diagnosis": "Examen general",
  "treatment": "Control preventivo",
  "weight_kg": 24.1,
  "medications": "No aplica",
  "notes": "Paciente estable"
}
```

### Vacuna — `/vaccines`

```json
{
  "id": 14,
  "pet_id": 12,
  "pet_name": "Luna",
  "vaccine_name": "Rabia",
  "administered_date": "2026-10-12",
  "next_dose_date": "2027-10-12",
  "batch_number": "RB-2401",
  "notes": "Dosis anual",
  "status": "Al día"
}
```

## 4. Reglas de negocio que debe validar el servidor

Las validaciones visuales de escritorio no sustituyen las del backend ni las restricciones SQL. El servidor debe garantizar:

1. Una mascota pertenece a un solo propietario a la vez; los cambios de propietario deben quedar registrados según el modelo de datos del equipo. Si se usa `PUT /pets/{id}` para cambiar `owner_id`, el backend debe escribir también la trazabilidad del cambio de propietario, o exponer una acción de transferencia dedicada.
2. Un veterinario no puede tener dos citas cuyos intervalos se crucen. Debe considerarse la duración del servicio, no solo que las horas de inicio sean diferentes.
3. Una cita atendida debe producir exactamente un registro clínico. `POST /appointments/{id}/attend` debe crear el registro y actualizar la cita a `Atendida` dentro de una transacción.
4. No se registra una vacuna con fecha futura ni para una mascota inactiva.
5. Ningún registro con historial se elimina físicamente. `DELETE` en propietarios, mascotas, veterinarios y servicios debe implementar desactivación lógica. No debe existir DELETE físico para el historial clínico.

## 5. Formato de errores

Se recomienda responder con JSON consistente:

```json
{
  "error": {
    "code": "APPOINTMENT_OVERLAP",
    "message": "El veterinario ya tiene una cita que se cruza con ese horario."
  }
}
```

Códigos HTTP sugeridos: `200` lectura/actualización, `201` creación, `204` acción sin cuerpo, `400` datos inválidos, `401/403` autenticación/permisos, `404` no encontrado, `409` conflicto de regla de negocio, `500` error interno.

## 6. Conectividad y seguridad

- Esta es una aplicación de escritorio: no requiere CORS como una web que corre dentro del navegador.
- La VM debe permitir la conexión de red al puerto HTTPS de la API y restringir el acceso a lo necesario.
- Usar HTTPS y autenticación si el backend lo implementa. No incluir claves privadas ni contraseñas de MySQL en el cliente de escritorio.
- MySQL debe ser accedido exclusivamente desde el backend con un usuario de aplicación de privilegios mínimos; nunca con `root`.
- El backend en Ubuntu y su servicio `systemd` pertenecen al despliegue del backend, no a esta interfaz.
