from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from mimascota.config import API_BASE_URL, API_TOKEN, DEMO_MODE, REQUEST_TIMEOUT, PROJECT_ROOT
from mimascota.data.demo_repository import DemoRepository
from mimascota.services.api_client import APIClient


class DataService:
    def __init__(self):
        self.demo_mode = DEMO_MODE
        if self.demo_mode:
            self.backend = DemoRepository(PROJECT_ROOT / "data" / "demo_data.json")
        else:
            self.backend = APIClient(API_BASE_URL, REQUEST_TIMEOUT, API_TOKEN)

    def list(self, resource: str) -> list[dict[str, Any]]:
        return self.backend.list(resource)

    def create(self, resource: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self.backend.create(resource, payload)

    def update(self, resource: str, record_id: Any, payload: dict[str, Any]) -> dict[str, Any]:
        return self.backend.update(resource, record_id, payload)

    def deactivate(self, resource: str, record_id: Any) -> None:
        self.backend.deactivate(resource, record_id)

    def cancel_appointment(self, record_id: Any) -> None:
        self.backend.cancel_appointment(record_id)

    def attend_appointment(self, appointment_id: Any, payload: dict[str, Any]) -> dict[str, Any]:
        return self.backend.attend_appointment(appointment_id, payload)

    def dashboard(self) -> dict[str, Any]:
        if self.demo_mode:
            return self.backend.dashboard()
        owners = self.list("owners")
        pets = self.list("pets")
        appointments = self.list("appointments")
        vaccines = self.list("vaccines")
        today = date.today().isoformat()
        upcoming = [x for x in appointments if x.get("appointment_date", "") >= today and x.get("status") not in {"Cancelada", "Atendida"}]
        upcoming.sort(key=lambda x: (x.get("appointment_date", ""), x.get("appointment_time", "")))
        due = [x for x in vaccines if x.get("status") in {"Vencida", "Por vencer"}]
        due.sort(key=lambda x: x.get("next_dose_date", ""))
        return {
            "owners": sum(1 for x in owners if x.get("active", True)),
            "pets": sum(1 for x in pets if x.get("active", True) and x.get("status") == "Activa"),
            "appointments_today": sum(1 for x in appointments if x.get("appointment_date") == today and x.get("status") != "Cancelada"),
            "vaccines_alerts": len(due),
            "upcoming": upcoming[:6],
            "vaccine_alerts": due[:5],
        }

    def health(self) -> dict[str, Any]:
        if self.demo_mode:
            return {"status": "demo"}
        return self.backend.health()
