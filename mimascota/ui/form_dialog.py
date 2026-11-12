from __future__ import annotations

import re
from datetime import date, datetime
from tkinter import messagebox
from typing import Any, Callable

import customtkinter as ctk

from mimascota.ui.theme import COLORS, FONT, FONT_DISPLAY


class FormDialog(ctk.CTkToplevel):
    """Consistent modal forms for create/update workflows."""

    def __init__(
        self,
        parent,
        title: str,
        fields: list[tuple],
        service,
        on_submit: Callable[[dict[str, Any]], None],
        initial: dict[str, Any] | None = None,
        width: int = 620,
    ):
        super().__init__(parent)
        self.parent = parent
        self.fields = fields
        self.service = service
        self.on_submit = on_submit
        self.initial = initial or {}
        self.inputs: dict[str, tuple[Any, str, bool]] = {}
        self.relation_maps: dict[str, dict[str, Any]] = {}
        self.error_var = ctk.StringVar(value="")

        self.title(f"MiMascota · {title}")
        self.geometry(f"{width}x760")
        self.minsize(520, 570)
        self.configure(fg_color=COLORS["bg"])
        self.transient(parent)
        self.grab_set()
        self._center()
        self._build(title)
        self.bind("<Escape>", lambda _event: self.destroy())

    def _center(self) -> None:
        self.update_idletasks()
        parent = self.parent
        x = parent.winfo_rootx() + max(0, (parent.winfo_width() - self.winfo_width()) // 2)
        y = parent.winfo_rooty() + max(0, (parent.winfo_height() - self.winfo_height()) // 2)
        self.geometry(f"+{x}+{y}")

    def _build(self, title: str) -> None:
        header = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=0)
        header.pack(fill="x")
        top = ctk.CTkFrame(header, fg_color="transparent")
        top.pack(fill="x", padx=25, pady=(20, 4))
        icon_box = ctk.CTkFrame(top, width=42, height=42, corner_radius=12, fg_color=COLORS["blue_soft"])
        icon_box.pack(side="left")
        icon_box.pack_propagate(False)
        ctk.CTkLabel(icon_box, text="✎", text_color=COLORS["blue"], font=(FONT_DISPLAY, 17)).pack(expand=True)
        title_box = ctk.CTkFrame(top, fg_color="transparent")
        title_box.pack(side="left", padx=12, fill="x", expand=True)
        ctk.CTkLabel(title_box, text=title, text_color=COLORS["text"], font=(FONT_DISPLAY, 18)).pack(anchor="w")
        ctk.CTkLabel(title_box, text="Los campos marcados con * son obligatorios.", text_color=COLORS["muted"], font=(FONT, 9)).pack(anchor="w", pady=(3, 0))
        ctk.CTkFrame(header, height=1, fg_color=COLORS["border"]).pack(fill="x", pady=(17, 0))

        body = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        body.pack(fill="both", expand=True, padx=20, pady=15)

        for index, field in enumerate(self.fields):
            key, label, field_type, required, options = field
            self._create_field(body, key, label, field_type, required, options, index)

        self.error_label = ctk.CTkLabel(
            self, textvariable=self.error_var, text_color=COLORS["red"],
            fg_color=COLORS["red_bg"], corner_radius=8, font=(FONT, 9),
            anchor="w", justify="left", wraplength=550,
        )

        footer = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=0)
        footer.pack(fill="x", side="bottom")
        ctk.CTkFrame(footer, height=1, fg_color=COLORS["border"]).pack(fill="x")
        ctk.CTkButton(
            footer, text="Cancelar", width=104, height=39, corner_radius=9,
            fg_color=COLORS["surface_alt"], hover_color=COLORS["surface_hover"],
            text_color=COLORS["text_soft"], border_width=1, border_color=COLORS["border"],
            font=(FONT_DISPLAY, 9), command=self.destroy,
        ).pack(side="right", padx=(7, 22), pady=13)
        ctk.CTkButton(
            footer, text="Guardar información", width=158, height=39, corner_radius=9,
            fg_color=COLORS["blue"], hover_color=COLORS["blue_hover"],
            font=(FONT_DISPLAY, 9), command=self._save,
        ).pack(side="right", padx=4, pady=13)

    def _create_field(self, parent, key, label, field_type, required, options, index) -> None:
        group = ctk.CTkFrame(parent, fg_color=COLORS["surface"], corner_radius=11, border_width=1, border_color=COLORS["border"])
        group.pack(fill="x", padx=3, pady=5)
        label_row = ctk.CTkFrame(group, fg_color="transparent")
        label_row.pack(fill="x", padx=14, pady=(10, 5))
        ctk.CTkLabel(label_row, text=label, text_color=COLORS["text"], font=(FONT_DISPLAY, 9)).pack(side="left")
        if required:
            ctk.CTkLabel(label_row, text="OBLIGATORIO", text_color=COLORS["blue"], font=(FONT_DISPLAY, 7)).pack(side="right")

        widget = None
        if field_type == "choice":
            values = list(options or [])
            widget = ctk.CTkComboBox(
                group, values=values or ["Sin opciones"], height=39,
                font=(FONT, 10), border_color=COLORS["border"],
                button_color=COLORS["blue"], button_hover_color=COLORS["blue_hover"],
                dropdown_fg_color=COLORS["surface"], dropdown_text_color=COLORS["text"],
            )
            current = self.initial.get(key)
            widget.set(str(current) if current in values else (values[0] if values else ""))
        elif field_type == "relation":
            records = self.service.list(options)
            relation_map: dict[str, Any] = {}
            for record in records:
                if record.get("active") is False:
                    continue
                if options == "pets" and record.get("status") != "Activa":
                    continue
                if options == "appointments" and record.get("status") in {"Cancelada", "Atendida"}:
                    continue
                name = record.get("full_name") or record.get("name") or record.get("pet_name") or record.get("appointment_date") or f"Registro {record.get('id')}"
                extra = ""
                if options == "appointments":
                    extra = f" · {record.get('appointment_time', '')} · {record.get('pet_name', '')}"
                display = f"{record.get('id')} · {name}{extra}"
                relation_map[display] = record.get("id")
            self.relation_maps[key] = relation_map
            values = list(relation_map.keys())
            if not required:
                values = ["— Sin seleccionar —"] + values
                relation_map["— Sin seleccionar —"] = None
            widget = ctk.CTkComboBox(
                group, values=values or ["Sin registros disponibles"], height=39,
                font=(FONT, 10), border_color=COLORS["border"], button_color=COLORS["blue"],
                dropdown_fg_color=COLORS["surface"], dropdown_text_color=COLORS["text"],
            )
            current_id = self.initial.get(key)
            selected = next((name for name, rid in relation_map.items() if rid is not None and str(rid) == str(current_id)), None)
            widget.set(selected or ("— Sin seleccionar —" if not required else (values[0] if values else "Sin registros disponibles")))
            if not relation_map and required:
                widget.configure(state="disabled")
        elif field_type == "multiline":
            widget = ctk.CTkTextbox(
                group, height=92, corner_radius=8, border_width=1,
                border_color=COLORS["border"], fg_color=COLORS["surface_alt"],
                text_color=COLORS["text"], font=(FONT, 10), wrap="word",
            )
            value = self.initial.get(key)
            if value:
                widget.insert("1.0", str(value))
        else:
            placeholders = {
                "birth_date": "AAAA-MM-DD",
                "appointment_date": "AAAA-MM-DD",
                "administered_date": "AAAA-MM-DD",
                "next_dose_date": "AAAA-MM-DD",
                "appointment_time": "HH:MM",
                "email": "nombre@correo.com",
                "phone": "Número de contacto",
                "price": "Ej. 65000",
                "duration_minutes": "Ej. 30",
                "weight_kg": "Ej. 12.5",
            }
            widget = ctk.CTkEntry(
                group, height=39, font=(FONT, 10), border_color=COLORS["border"],
                fg_color=COLORS["surface_alt"], text_color=COLORS["text"],
                placeholder_text=placeholders.get(key, "Escribe aquí…"),
            )
            value = self.initial.get(key, "")
            if value is not None:
                widget.insert(0, str(value))

        widget.pack(fill="x", padx=14, pady=(0, 13))
        self.inputs[key] = (widget, field_type, required)

    def _read_widget(self, widget, field_type: str) -> str:
        if field_type == "multiline":
            return widget.get("1.0", "end-1c").strip()
        return widget.get().strip()

    def _save(self) -> None:
        payload: dict[str, Any] = {}
        self.error_var.set("")
        try:
            for key, (widget, field_type, required) in self.inputs.items():
                raw = self._read_widget(widget, field_type)
                if field_type == "relation":
                    value = self.relation_maps[key].get(raw)
                    if required and value is None:
                        raise ValueError(f"Selecciona un valor válido para «{key}».")
                    if value is not None:
                        try:
                            value = int(value)
                        except (ValueError, TypeError):
                            pass
                else:
                    value = raw

                if required and (value is None or str(value).strip() == ""):
                    raise ValueError(f"El campo «{key}» es obligatorio.")
                if value == "" and not required:
                    value = None

                if key in {"appointment_date", "administered_date", "next_dose_date", "birth_date"} and value:
                    try:
                        parsed = date.fromisoformat(str(value)[:10])
                    except ValueError as exc:
                        raise ValueError(f"La fecha de «{key}» debe tener formato AAAA-MM-DD.") from exc
                    if key == "administered_date" and parsed > date.today():
                        raise ValueError("No se puede registrar una vacuna con fecha futura.")
                    if key == "next_dose_date" and parsed < date.today():
                        raise ValueError("La próxima dosis no puede tener una fecha anterior a hoy.")
                    if key == "birth_date" and parsed > date.today():
                        raise ValueError("La fecha de nacimiento no puede ser futura.")

                if key == "appointment_time" and value:
                    try:
                        datetime.strptime(str(value), "%H:%M")
                    except ValueError as exc:
                        raise ValueError("La hora debe tener formato HH:MM (24 horas).") from exc

                if key == "email" and value:
                    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", str(value)):
                        raise ValueError("Escribe un correo electrónico válido.")

                if key in {"price", "duration_minutes", "weight_kg"} and value not in (None, ""):
                    try:
                        value = float(value) if key == "weight_kg" else int(float(value))
                    except (ValueError, TypeError) as exc:
                        raise ValueError(f"El campo «{key}» debe ser numérico.") from exc
                    if value < 0:
                        raise ValueError(f"El campo «{key}» no puede ser negativo.")

                payload[key] = value

            self.on_submit(payload)
            self.destroy()
        except Exception as exc:
            self.error_var.set(str(exc))
            if not self.error_label.winfo_manager():
                self.error_label.pack(fill="x", padx=22, pady=(0, 8), before=self.winfo_children()[-1])
