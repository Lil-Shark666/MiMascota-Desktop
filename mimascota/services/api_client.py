from __future__ import annotations

from typing import Any
import requests


class APIError(RuntimeError):
    pass


class APIClient:
    """Cliente HTTP. No contiene ni utiliza credenciales de MySQL."""

    def __init__(self, base_url: str, timeout: float = 12, token: str = ""):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json", "Content-Type": "application/json"})
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
        except requests.RequestException as exc:
            raise APIError(f"No fue posible comunicarse con el backend: {exc}") from exc
        if response.status_code == 204:
            return None
        try:
            payload = response.json() if response.content else None
        except ValueError:
            payload = None
        if not response.ok:
            message = "La API devolvió un error."
            if isinstance(payload, dict):
                error = payload.get("error", payload)
                if isinstance(error, dict):
                    message = error.get("message", message)
                elif isinstance(error, str):
                    message = error
            raise APIError(f"HTTP {response.status_code}: {message}")
        return payload

    def list(self, resource: str) -> list[dict[str, Any]]:
        payload = self._request("GET", resource)
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict) and isinstance(payload.get("items"), list):
            return payload["items"]
        raise APIError(f"La respuesta GET /{resource} debe ser una lista JSON o contener 'items'.")

    def create(self, resource: str, payload: dict[str, Any]) -> dict[str, Any]:
        result = self._request("POST", resource, json=payload)
        return result if isinstance(result, dict) else {**payload}

    def update(self, resource: str, record_id: Any, payload: dict[str, Any]) -> dict[str, Any]:
        result = self._request("PUT", f"{resource}/{record_id}", json=payload)
        return result if isinstance(result, dict) else {"id": record_id, **payload}

    def deactivate(self, resource: str, record_id: Any) -> None:
        # DELETE debe ser lógico (active=false), nunca un borrado físico.
        self._request("DELETE", f"{resource}/{record_id}")

    def cancel_appointment(self, record_id: Any) -> None:
        self._request("POST", f"appointments/{record_id}/cancel", json={})

    def attend_appointment(self, appointment_id: Any, clinical_data: dict[str, Any]) -> dict[str, Any]:
        # El backend debe crear el historial y marcar la cita como atendida en una transacción.
        result = self._request("POST", f"appointments/{appointment_id}/attend", json=clinical_data)
        return result if isinstance(result, dict) else clinical_data

    def health(self) -> dict[str, Any]:
        result = self._request("GET", "health")
        return result if isinstance(result, dict) else {"status": "unknown"}
