from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


class DemoRepository:
    """Repositorio local para demostraciones. No sustituye la base de datos del equipo."""

    def __init__(self, data_file: Path):
        self.data_file = data_file
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        if self.data_file.exists():
            try:
                self.data = json.loads(self.data_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                self.data = self._seed()
        else:
            self.data = self._seed()
            self._save()

    def _seed(self) -> dict[str, list[dict[str, Any]]]:
        today = date.today()
        owners = [
            {"id": 1, "full_name": "Laura Méndez", "document_type": "CC", "document_number": "1061700234", "phone": "300 456 7812", "email": "laura.mendez@email.com", "address": "Centro", "active": True},
            {"id": 2, "full_name": "Andrés Salazar", "document_type": "CC", "document_number": "1012456789", "phone": "310 555 1940", "email": "andres.salazar@email.com", "address": "La Esmeralda", "active": True},
            {"id": 3, "full_name": "Camila Rojas", "document_type": "CC", "document_number": "1058901234", "phone": "315 802 1144", "email": "camila.rojas@email.com", "address": "Campamento", "active": True},
            {"id": 4, "full_name": "Julián Torres", "document_type": "CC", "document_number": "1034567890", "phone": "312 444 2010", "email": "julian.torres@email.com", "address": "El Recuerdo", "active": True},
            {"id": 5, "full_name": "Valentina Muñoz", "document_type": "CC", "document_number": "1061700991", "phone": "300 701 8877", "email": "valentina.m@email.com", "address": "Modelo", "active": True},
        ]
        vets = [
            {"id": 1, "full_name": "Dra. María Fernanda Ruiz", "license_number": "TP-45871", "specialty": "Medicina general", "phone": "310 555 0101", "email": "m.ruiz@vet.com", "active": True},
            {"id": 2, "full_name": "Dr. Santiago López", "license_number": "TP-39210", "specialty": "Dermatología", "phone": "310 555 0102", "email": "s.lopez@vet.com", "active": True},
            {"id": 3, "full_name": "Dra. Paula Castillo", "license_number": "TP-51720", "specialty": "Cirugía", "phone": "310 555 0103", "email": "p.castillo@vet.com", "active": True},
        ]
        services = [
            {"id": 1, "name": "Consulta general", "description": "Valoración clínica general", "price": 65000, "duration_minutes": 30, "active": True},
            {"id": 2, "name": "Vacunación", "description": "Aplicación y registro de vacuna", "price": 45000, "duration_minutes": 20, "active": True},
            {"id": 3, "name": "Control dermatológico", "description": "Evaluación de piel y pelaje", "price": 85000, "duration_minutes": 40, "active": True},
            {"id": 4, "name": "Profilaxis", "description": "Limpieza dental veterinaria", "price": 180000, "duration_minutes": 60, "active": True},
        ]
        pets = [
            {"id": 1, "name": "Luna", "owner_id": 1, "species": "Perro", "breed": "Golden Retriever", "birth_date": "2021-04-12", "sex": "Hembra", "status": "Activa", "active": True, "notes": "Al día con controles"},
            {"id": 2, "name": "Milo", "owner_id": 2, "species": "Gato", "breed": "Criollo", "birth_date": "2022-09-03", "sex": "Macho", "status": "Activa", "active": True, "notes": ""},
            {"id": 3, "name": "Max", "owner_id": 3, "species": "Perro", "breed": "Labrador", "birth_date": "2019-01-22", "sex": "Macho", "status": "Activa", "active": True, "notes": "Control de peso"},
            {"id": 4, "name": "Nala", "owner_id": 1, "species": "Gato", "breed": "Siamés", "birth_date": "2023-06-15", "sex": "Hembra", "status": "Activa", "active": True, "notes": ""},
            {"id": 5, "name": "Rocky", "owner_id": 4, "species": "Perro", "breed": "Bulldog francés", "birth_date": "2020-11-08", "sex": "Macho", "status": "Activa", "active": True, "notes": ""},
            {"id": 6, "name": "Mora", "owner_id": 5, "species": "Conejo", "breed": "Mini Lop", "birth_date": "2024-02-20", "sex": "Hembra", "status": "Activa", "active": True, "notes": ""},
        ]
        appointments = [
            {"id": 1, "pet_id": 1, "vet_id": 1, "service_id": 1, "appointment_date": today.isoformat(), "appointment_time": "09:30", "status": "Confirmada", "notes": "Revisión general"},
            {"id": 2, "pet_id": 2, "vet_id": 2, "service_id": 3, "appointment_date": today.isoformat(), "appointment_time": "11:00", "status": "Programada", "notes": "Irritación en la piel"},
            {"id": 3, "pet_id": 3, "vet_id": 1, "service_id": 1, "appointment_date": (today + timedelta(days=1)).isoformat(), "appointment_time": "10:00", "status": "Confirmada", "notes": "Control de peso"},
            {"id": 4, "pet_id": 4, "vet_id": 3, "service_id": 2, "appointment_date": (today + timedelta(days=2)).isoformat(), "appointment_time": "14:00", "status": "Programada", "notes": "Refuerzo anual"},
        ]
        records = [
            {"id": 1, "appointment_id": 90, "pet_id": 3, "vet_id": 1, "created_at": (today - timedelta(days=7)).isoformat(), "diagnosis": "Condición corporal por encima del ideal", "treatment": "Ajuste de alimentación y actividad", "weight_kg": 28.4, "medications": "No aplica", "notes": "Control en 30 días"},
            {"id": 2, "appointment_id": 91, "pet_id": 1, "vet_id": 1, "created_at": (today - timedelta(days=15)).isoformat(), "diagnosis": "Examen general sin hallazgos relevantes", "treatment": "Continuar controles preventivos", "weight_kg": 24.1, "medications": "No aplica", "notes": "Paciente estable"},
        ]
        vaccines = [
            {"id": 1, "pet_id": 1, "vaccine_name": "Rabia", "administered_date": (today - timedelta(days=330)).isoformat(), "next_dose_date": (today + timedelta(days=15)).isoformat(), "batch_number": "RB-2401", "notes": "Dosis anual"},
            {"id": 2, "pet_id": 2, "vaccine_name": "Triple felina", "administered_date": (today - timedelta(days=360)).isoformat(), "next_dose_date": (today - timedelta(days=4)).isoformat(), "batch_number": "TF-1180", "notes": "Pendiente de refuerzo"},
            {"id": 3, "pet_id": 3, "vaccine_name": "Polivalente", "administered_date": (today - timedelta(days=120)).isoformat(), "next_dose_date": (today + timedelta(days=245)).isoformat(), "batch_number": "PV-9920", "notes": ""},
        ]
        return {"owners": owners, "pets": pets, "vets": vets, "services": services, "appointments": appointments, "records": records, "vaccines": vaccines}

    def _save(self) -> None:
        self.data_file.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _next_id(self, resource: str) -> int:
        return max((int(item.get("id", 0)) for item in self.data[resource]), default=0) + 1

    def _enrich(self, resource: str, item: dict[str, Any]) -> dict[str, Any]:
        result = dict(item)
        if resource == "pets":
            owner = self._find("owners", result.get("owner_id"))
            result["owner_name"] = owner.get("full_name", "Sin propietario") if owner else "Sin propietario"
        elif resource == "appointments":
            pet = self._find("pets", result.get("pet_id"))
            vet = self._find("vets", result.get("vet_id"))
            service = self._find("services", result.get("service_id"))
            owner = self._find("owners", pet.get("owner_id")) if pet else None
            result.update({
                "pet_name": pet.get("name", "—") if pet else "—",
                "owner_name": owner.get("full_name", "—") if owner else "—",
                "vet_name": vet.get("full_name", "—") if vet else "—",
                "service_name": service.get("name", "—") if service else "—",
            })
        elif resource == "records":
            pet = self._find("pets", result.get("pet_id"))
            vet = self._find("vets", result.get("vet_id"))
            result["pet_name"] = pet.get("name", "—") if pet else "—"
            result["vet_name"] = vet.get("full_name", "—") if vet else "—"
        elif resource == "vaccines":
            pet = self._find("pets", result.get("pet_id"))
            result["pet_name"] = pet.get("name", "—") if pet else "—"
            due = result.get("next_dose_date")
            if due:
                try:
                    due_date = date.fromisoformat(str(due)[:10])
                    result["status"] = "Vencida" if due_date < date.today() else ("Por vencer" if (due_date - date.today()).days <= 30 else "Al día")
                except ValueError:
                    result["status"] = "Sin fecha"
            else:
                result["status"] = "Sin refuerzo"
        result["status"] = result.get("status") or ("Activo" if result.get("active", True) else "Inactivo")
        if result.get("active") is False:
            result["status"] = "Inactivo"
        return result

    def _find(self, resource: str, record_id: Any) -> dict[str, Any] | None:
        return next((row for row in self.data[resource] if str(row.get("id")) == str(record_id)), None)

    def list(self, resource: str) -> list[dict[str, Any]]:
        if resource not in self.data:
            raise ValueError(f"Recurso desconocido: {resource}")
        return [self._enrich(resource, item) for item in self.data[resource]]

    def dashboard(self) -> dict[str, Any]:
        today = date.today().isoformat()
        upcoming = [x for x in self.list("appointments") if x.get("appointment_date", "") >= today and x.get("status") not in {"Cancelada", "Atendida"}]
        upcoming.sort(key=lambda x: (x.get("appointment_date", ""), x.get("appointment_time", "")))
        due = [x for x in self.list("vaccines") if x.get("status") in {"Vencida", "Por vencer"}]
        due.sort(key=lambda x: x.get("next_dose_date", ""))
        return {
            "owners": sum(1 for x in self.data["owners"] if x.get("active", True)),
            "pets": sum(1 for x in self.data["pets"] if x.get("active", True) and x.get("status") == "Activa"),
            "appointments_today": sum(1 for x in self.data["appointments"] if x.get("appointment_date") == today and x.get("status") != "Cancelada"),
            "vaccines_alerts": len(due),
            "upcoming": upcoming[:6],
            "vaccine_alerts": due[:5],
        }

    def _validate_vaccine(self, payload: dict[str, Any]) -> None:
        try:
            applied = date.fromisoformat(str(payload.get("administered_date", ""))[:10])
        except ValueError as exc:
            raise ValueError("La fecha de aplicación debe tener formato AAAA-MM-DD.") from exc
        if applied > date.today():
            raise ValueError("No se puede registrar una vacuna con fecha futura.")
        pet = self._find("pets", payload.get("pet_id"))
        if not pet or pet.get("status") != "Activa" or pet.get("active") is False:
            raise ValueError("Solo se pueden registrar vacunas para mascotas activas.")

    def _validate_appointment(self, payload: dict[str, Any], exclude_id: Any = None) -> None:
        try:
            requested = datetime.strptime(f"{payload['appointment_date']} {payload['appointment_time']}", "%Y-%m-%d %H:%M")
        except (KeyError, ValueError) as exc:
            raise ValueError("La fecha debe ser AAAA-MM-DD y la hora HH:MM.") from exc
        pet = self._find("pets", payload.get("pet_id"))
        if not pet or pet.get("status") != "Activa" or pet.get("active") is False:
            raise ValueError("Solo se pueden agendar citas para mascotas activas.")
        vet = self._find("vets", payload.get("vet_id"))
        if not vet or vet.get("active") is False:
            raise ValueError("Selecciona un veterinario activo.")
        service = self._find("services", payload.get("service_id"))
        if not service or service.get("active") is False:
            raise ValueError("Selecciona un servicio activo.")
        duration = int(service.get("duration_minutes", 30))
        requested_end = requested + timedelta(minutes=duration)
        for item in self.data["appointments"]:
            if str(item.get("id")) == str(exclude_id) or str(item.get("vet_id")) != str(payload.get("vet_id")):
                continue
            if item.get("status") in {"Cancelada", "Atendida"}:
                continue
            try:
                existing = datetime.strptime(f"{item['appointment_date']} {item['appointment_time']}", "%Y-%m-%d %H:%M")
            except (KeyError, ValueError):
                continue
            existing_service = self._find("services", item.get("service_id"))
            existing_end = existing + timedelta(minutes=int(existing_service.get("duration_minutes", 30)) if existing_service else 30)
            if requested < existing_end and existing < requested_end:
                raise ValueError("El veterinario ya tiene una cita que se cruza con ese horario.")

    def create(self, resource: str, payload: dict[str, Any]) -> dict[str, Any]:
        if resource == "vaccines":
            self._validate_vaccine(payload)
        if resource == "appointments":
            self._validate_appointment(payload)
        if resource == "records":
            raise ValueError("Las atenciones se registran desde la cita mediante la acción Registrar atención.")
        new_item = dict(payload)
        new_item["id"] = self._next_id(resource)
        new_item.setdefault("active", True)
        if resource == "appointments":
            new_item.setdefault("status", "Programada")
        if resource == "records":
            new_item.setdefault("created_at", date.today().isoformat())
        self.data[resource].append(new_item)
        self._save()
        return self._enrich(resource, new_item)

    def update(self, resource: str, record_id: Any, payload: dict[str, Any]) -> dict[str, Any]:
        item = self._find(resource, record_id)
        if not item:
            raise ValueError("No se encontró el registro seleccionado.")
        candidate = {**item, **payload}
        if resource == "vaccines":
            self._validate_vaccine(candidate)
        if resource == "appointments":
            self._validate_appointment(candidate, exclude_id=record_id)
        item.update(payload)
        self._save()
        return self._enrich(resource, item)

    def deactivate(self, resource: str, record_id: Any) -> None:
        item = self._find(resource, record_id)
        if not item:
            raise ValueError("No se encontró el registro seleccionado.")
        item["active"] = False
        self._save()

    def cancel_appointment(self, record_id: Any) -> None:
        item = self._find("appointments", record_id)
        if not item:
            raise ValueError("No se encontró la cita seleccionada.")
        if item.get("status") == "Atendida":
            raise ValueError("Una cita atendida no se puede cancelar.")
        item["status"] = "Cancelada"
        self._save()

    def attend_appointment(self, appointment_id: Any, clinical_data: dict[str, Any]) -> dict[str, Any]:
        appointment = self._find("appointments", appointment_id)
        if not appointment:
            raise ValueError("No se encontró la cita.")
        if appointment.get("status") == "Cancelada":
            raise ValueError("No se puede atender una cita cancelada.")
        if appointment.get("status") == "Atendida":
            raise ValueError("La cita ya figura como atendida.")
        if any(str(r.get("appointment_id")) == str(appointment_id) for r in self.data["records"]):
            raise ValueError("Esta cita ya tiene un registro de atención.")
        pet = self._find("pets", appointment.get("pet_id"))
        vet = self._find("vets", appointment.get("vet_id"))
        record = {
            **clinical_data,
            "id": self._next_id("records"),
            "appointment_id": appointment["id"],
            "pet_id": appointment.get("pet_id"),
            "vet_id": appointment.get("vet_id"),
            "created_at": date.today().isoformat(),
        }
        # Una sola escritura del archivo simula la operación atómica del backend.
        self.data["records"].append(record)
        appointment["status"] = "Atendida"
        self._save()
        return self._enrich("records", record)
