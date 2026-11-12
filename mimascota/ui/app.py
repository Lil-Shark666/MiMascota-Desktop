from __future__ import annotations

import csv
import tkinter as tk
from datetime import date, datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any

import customtkinter as ctk

from mimascota.config import APP_NAME, APP_VERSION
from mimascota.data.schema import NAV_ITEMS, RESOURCES
from mimascota.services.data_service import DataService
from mimascota.ui.form_dialog import FormDialog
from mimascota.ui.theme import COLORS, FONT, FONT_DISPLAY


NAV_GROUPS = [
    ("INICIO", [("dashboard", "Panel principal", "⌂")]),
    ("GESTIÓN", [
        ("owners", "Propietarios", "♙"),
        ("pets", "Mascotas", "♧"),
        ("vets", "Veterinarios", "✚"),
        ("services", "Servicios", "▤"),
    ]),
    ("ATENCIÓN", [
        ("appointments", "Citas y agenda", "◷"),
        ("records", "Historial clínico", "▧"),
        ("vaccines", "Vacunación", "♡"),
    ]),
]

PAGE_COPY = {
    "dashboard": ("Panel principal", "Resumen general de la operación veterinaria."),
    "owners": ("Propietarios", "Administra los responsables y sus datos de contacto."),
    "pets": ("Mascotas", "Consulta y administra las fichas de los pacientes."),
    "vets": ("Veterinarios", "Gestiona los profesionales y sus datos de contacto."),
    "services": ("Servicios", "Mantén actualizado el catálogo y las tarifas de atención."),
    "appointments": ("Citas y agenda", "Programa, consulta y gestiona las atenciones."),
    "records": ("Historial clínico", "Consulta diagnósticos, tratamientos y evolución clínica."),
    "vaccines": ("Vacunación", "Controla las dosis aplicadas y las próximas fechas."),
}

FILTERS = {
    "owners": ["Todos", "Activos", "Inactivos"],
    "pets": ["Todos", "Activas", "Fallecidas", "Adoptadas", "Inactivas"],
    "vets": ["Todos", "Activos", "Inactivos"],
    "services": ["Todos", "Activos", "Inactivos"],
    "appointments": ["Todas", "Programada", "Confirmada", "Atendida", "Cancelada"],
    "records": ["Todos"],
    "vaccines": ["Todos", "Vencida", "Por vencer", "Al día", "Sin refuerzo"],
}

STATUS_STYLES = {
    "activo": (COLORS["green_bg"], COLORS["green"]),
    "activa": (COLORS["green_bg"], COLORS["green"]),
    "confirmada": (COLORS["green_bg"], COLORS["green"]),
    "atendida": (COLORS["blue_soft"], COLORS["blue"]),
    "programada": (COLORS["cyan_bg"], COLORS["cyan"]),
    "por vencer": (COLORS["orange_bg"], COLORS["orange"]),
    "vencida": (COLORS["red_bg"], COLORS["red"]),
    "cancelada": (COLORS["red_bg"], COLORS["red"]),
    "inactivo": ("#EEF1F5", COLORS["muted"]),
    "fallecida": ("#EEF1F5", COLORS["muted"]),
    "adoptada": (COLORS["purple_bg"], COLORS["purple"]),
    "al día": (COLORS["green_bg"], COLORS["green"]),
}


class MiMascotaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.service = DataService()
        self.current_page = "dashboard"
        self.current_items: list[dict[str, Any]] = []
        self.filtered_items: list[dict[str, Any]] = []
        self.search_var = tk.StringVar(value="")
        self.filter_var = tk.StringVar(value="Todos")
        self.tree: ttk.Treeview | None = None
        self.count_label: ctk.CTkLabel | None = None
        self.page_scroll: ctk.CTkScrollableFrame | None = None
        self.nav_buttons: dict[str, ctk.CTkButton] = {}
        self.stat_labels: dict[str, ctk.CTkLabel] = {}

        self.title(f"{APP_NAME} | Sistema de gestión veterinaria")
        self.geometry("1480x930")
        self.minsize(1180, 760)
        self.configure(fg_color=COLORS["bg"])
        self._center_window()
        self._configure_tree_style()
        self._build_shell()
        self._bind_shortcuts()
        self.show_page("dashboard")

    # ------------------------------------------------------------------
    # Window, styles and shell
    # ------------------------------------------------------------------
    def _center_window(self) -> None:
        self.update_idletasks()
        width, height = 1480, 930
        x = max(0, (self.winfo_screenwidth() - width) // 2)
        y = max(0, (self.winfo_screenheight() - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _configure_tree_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "Mi.Treeview",
            background=COLORS["surface"],
            foreground=COLORS["text"],
            fieldbackground=COLORS["surface"],
            rowheight=39,
            borderwidth=0,
            relief="flat",
            font=(FONT, 10),
        )
        style.configure(
            "Mi.Treeview.Heading",
            background=COLORS["surface_alt"],
            foreground=COLORS["muted"],
            relief="flat",
            borderwidth=0,
            font=(FONT_DISPLAY, 9),
            padding=(10, 13),
        )
        style.map(
            "Mi.Treeview",
            background=[("selected", COLORS["blue_soft"])],
            foreground=[("selected", COLORS["navy"])],
        )
        style.map("Mi.Treeview.Heading", background=[("active", COLORS["surface_hover"])])

    def _build_shell(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=258, corner_radius=0, fg_color=COLORS["navy_deep"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(3, weight=1)

        brand = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=20, pady=(24, 25))
        logo = ctk.CTkFrame(brand, width=46, height=46, corner_radius=14, fg_color=COLORS["blue"])
        logo.pack(side="left")
        logo.pack_propagate(False)
        ctk.CTkLabel(logo, text="M", text_color=COLORS["white"], font=(FONT_DISPLAY, 24)).pack(expand=True)
        brand_text = ctk.CTkFrame(brand, fg_color="transparent")
        brand_text.pack(side="left", padx=12)
        ctk.CTkLabel(brand_text, text="MiMascota", text_color=COLORS["white"], font=(FONT_DISPLAY, 20)).pack(anchor="w")
        ctk.CTkLabel(brand_text, text="GESTIÓN VETERINARIA", text_color="#92A7BE", font=(FONT_DISPLAY, 8)).pack(anchor="w", pady=(2, 0))

        clinic = ctk.CTkFrame(self.sidebar, fg_color=COLORS["navy_soft"], corner_radius=12)
        clinic.pack(fill="x", padx=15, pady=(0, 21))
        ctk.CTkLabel(clinic, text="ESPACIO DE TRABAJO", text_color="#9DB1C8", font=(FONT_DISPLAY, 8)).pack(anchor="w", padx=13, pady=(11, 3))
        ctk.CTkLabel(clinic, text="Clínica veterinaria", text_color=COLORS["white"], font=(FONT_DISPLAY, 11)).pack(anchor="w", padx=13, pady=(0, 11))

        nav_scroll = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent", corner_radius=0)
        nav_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        for group_title, items in NAV_GROUPS:
            ctk.CTkLabel(nav_scroll, text=group_title, text_color="#7188A2", font=(FONT_DISPLAY, 8)).pack(anchor="w", padx=12, pady=(13, 7))
            for key, title, icon in items:
                button = ctk.CTkButton(
                    nav_scroll,
                    text=f"{icon}     {title}",
                    anchor="w",
                    height=43,
                    corner_radius=10,
                    fg_color="transparent",
                    hover_color=COLORS["navy_soft"],
                    text_color="#D2DCE7",
                    font=(FONT, 11),
                    command=lambda page=key: self.show_page(page),
                )
                button.pack(fill="x", padx=2, pady=2)
                self.nav_buttons[key] = button

        sidebar_footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        sidebar_footer.pack(fill="x", padx=17, pady=(5, 17))
        ctk.CTkFrame(sidebar_footer, height=1, fg_color="#30445B").pack(fill="x", pady=(0, 13))
        row = ctk.CTkFrame(sidebar_footer, fg_color="transparent")
        row.pack(fill="x")
        avatar = ctk.CTkFrame(row, width=34, height=34, corner_radius=17, fg_color="#29435E")
        avatar.pack(side="left")
        avatar.pack_propagate(False)
        ctk.CTkLabel(avatar, text="AD", text_color=COLORS["white"], font=(FONT_DISPLAY, 9)).pack(expand=True)
        user = ctk.CTkFrame(row, fg_color="transparent")
        user.pack(side="left", padx=9)
        ctk.CTkLabel(user, text="Administrador", text_color=COLORS["white"], font=(FONT_DISPLAY, 10)).pack(anchor="w")
        ctk.CTkLabel(user, text=f"MiMascota v{APP_VERSION}", text_color="#8EA2B9", font=(FONT, 8)).pack(anchor="w", pady=(1, 0))

        self.main = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=0)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_rowconfigure(1, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        self.topbar = ctk.CTkFrame(self.main, height=72, fg_color=COLORS["surface"], corner_radius=0, border_width=0)
        self.topbar.grid(row=0, column=0, sticky="ew")
        self.topbar.grid_columnconfigure(0, weight=1)
        self.top_title = ctk.CTkLabel(self.topbar, text="CLÍNICA VETERINARIA", text_color=COLORS["muted"], font=(FONT_DISPLAY, 9))
        self.top_title.grid(row=0, column=0, sticky="sw", padx=30, pady=(12, 2))
        self.top_subtitle = ctk.CTkLabel(self.topbar, text="Panel principal", text_color=COLORS["text"], font=(FONT_DISPLAY, 14))
        self.top_subtitle.grid(row=1, column=0, sticky="nw", padx=30, pady=(0, 12))

        right = ctk.CTkFrame(self.topbar, fg_color="transparent")
        right.grid(row=0, column=1, rowspan=2, sticky="e", padx=27)
        self.mode_badge = ctk.CTkLabel(
            right,
            text="●  MODO DEMOSTRACIÓN" if self.service.demo_mode else "●  API CONFIGURADA",
            text_color=COLORS["orange"] if self.service.demo_mode else COLORS["green"],
            fg_color=COLORS["orange_bg"] if self.service.demo_mode else COLORS["green_bg"],
            corner_radius=8,
            font=(FONT_DISPLAY, 8),
            padx=11,
            pady=8,
        )
        self.mode_badge.pack(side="left", padx=(0, 14))
        self.date_label = ctk.CTkLabel(right, text=self._today_label(), text_color=COLORS["muted"], font=(FONT, 9))
        self.date_label.pack(side="left")

        self.content = ctk.CTkFrame(self.main, fg_color=COLORS["bg"], corner_radius=0)
        self.content.grid(row=1, column=0, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

    def _today_label(self) -> str:
        now = datetime.now()
        weekdays = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        months = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        return f"{weekdays[now.weekday()]}, {now.day} de {months[now.month - 1]} de {now.year}"

    @staticmethod
    def _greeting() -> str:
        hour = datetime.now().hour
        if hour < 12:
            return "Buenos días, administrador"
        if hour < 19:
            return "Buenas tardes, administrador"
        return "Buenas noches, administrador"

    def _bind_shortcuts(self) -> None:
        self.bind("<Control-f>", lambda _e: self._focus_search())
        self.bind("<Control-n>", lambda _e: self._open_create(self.current_page) if self.current_page in RESOURCES else self.show_page("appointments"))
        self.bind("<F5>", lambda _e: self._refresh_current())

    def _focus_search(self) -> None:
        if hasattr(self, "search_entry") and self.search_entry.winfo_exists():
            self.search_entry.focus_set()

    def _refresh_current(self) -> None:
        if self.current_page == "dashboard":
            self.show_page("dashboard")
        elif self.current_page in RESOURCES:
            self._load_resource(self.current_page)

    # ------------------------------------------------------------------
    # Navigation and shared components
    # ------------------------------------------------------------------
    def _set_nav_active(self, page: str) -> None:
        for key, button in self.nav_buttons.items():
            active = key == page
            button.configure(
                fg_color=COLORS["blue"] if active else "transparent",
                text_color=COLORS["white"] if active else "#D2DCE7",
                hover_color=COLORS["blue_hover"] if active else COLORS["navy_soft"],
                font=(FONT_DISPLAY if active else FONT, 11),
            )

    def _clear_content(self) -> None:
        for child in self.content.winfo_children():
            child.destroy()
        self.tree = None
        self.count_label = None
        self.page_scroll = None

    def show_page(self, page: str) -> None:
        if page not in {"dashboard", *RESOURCES.keys()}:
            return
        self.current_page = page
        self.search_var.set("")
        self.filter_var.set(FILTERS.get(page, ["Todos"])[0])
        self._set_nav_active(page)
        self.top_subtitle.configure(text=PAGE_COPY[page][0])
        self._clear_content()
        if page == "dashboard":
            self._show_dashboard()
        else:
            self._show_resource_page(page)

    def _scroll_page(self) -> ctk.CTkScrollableFrame:
        scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent", corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=0, pady=0)
        self.page_scroll = scroll
        return scroll

    def _page_heading(self, parent, title: str, subtitle: str, action_text: str | None = None, action=None) -> ctk.CTkFrame:
        heading = ctk.CTkFrame(parent, fg_color="transparent")
        heading.pack(fill="x", padx=30, pady=(25, 17))
        text_frame = ctk.CTkFrame(heading, fg_color="transparent")
        text_frame.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(text_frame, text=title, text_color=COLORS["text"], font=(FONT_DISPLAY, 24)).pack(anchor="w")
        ctk.CTkLabel(text_frame, text=subtitle, text_color=COLORS["muted"], font=(FONT, 10)).pack(anchor="w", pady=(5, 0))
        if action_text and action:
            ctk.CTkButton(
                heading,
                text=action_text,
                width=158,
                height=42,
                corner_radius=10,
                fg_color=COLORS["blue"],
                hover_color=COLORS["blue_hover"],
                text_color=COLORS["white"],
                font=(FONT_DISPLAY, 10),
                command=action,
            ).pack(side="right", padx=(15, 0), pady=(4, 0))
        return heading

    def _panel(self, parent, title: str, subtitle: str | None = None) -> ctk.CTkFrame:
        panel = ctk.CTkFrame(parent, fg_color=COLORS["surface"], corner_radius=15, border_width=1, border_color=COLORS["border"])
        panel.grid_columnconfigure(0, weight=1)
        head = ctk.CTkFrame(panel, fg_color="transparent")
        head.pack(fill="x", padx=18, pady=(16, 10))
        labels = ctk.CTkFrame(head, fg_color="transparent")
        labels.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(labels, text=title, text_color=COLORS["text"], font=(FONT_DISPLAY, 12)).pack(anchor="w")
        if subtitle:
            ctk.CTkLabel(labels, text=subtitle, text_color=COLORS["muted"], font=(FONT, 9)).pack(anchor="w", pady=(3, 0))
        return panel

    def _metric_card(self, parent, title: str, value: Any, caption: str, icon: str, accent: str, soft: str) -> None:
        card = ctk.CTkFrame(parent, fg_color=COLORS["surface"], corner_radius=15, border_width=1, border_color=COLORS["border"])
        card.pack(side="left", fill="both", expand=True, padx=6)
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(15, 6))
        ctk.CTkLabel(top, text=title.upper(), text_color=COLORS["muted"], font=(FONT_DISPLAY, 8)).pack(side="left")
        icon_box = ctk.CTkFrame(top, width=34, height=34, corner_radius=10, fg_color=soft)
        icon_box.pack(side="right")
        icon_box.pack_propagate(False)
        ctk.CTkLabel(icon_box, text=icon, text_color=accent, font=(FONT_DISPLAY, 15)).pack(expand=True)
        ctk.CTkLabel(card, text=str(value), text_color=COLORS["text"], font=(FONT_DISPLAY, 26)).pack(anchor="w", padx=16, pady=(0, 1))
        ctk.CTkLabel(card, text=caption, text_color=COLORS["muted"], font=(FONT, 9)).pack(anchor="w", padx=16, pady=(0, 15))

    def _small_tree(self, parent, headings, keys, rows, widths, height=6) -> None:
        table_wrap = ctk.CTkFrame(parent, fg_color="transparent")
        table_wrap.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        table_wrap.grid_rowconfigure(0, weight=1)
        table_wrap.grid_columnconfigure(0, weight=1)
        tree = ttk.Treeview(table_wrap, columns=keys, show="headings", style="Mi.Treeview", height=height)
        for heading, key, width in zip(headings, keys, widths):
            tree.heading(key, text=heading)
            tree.column(key, width=width, minwidth=58, anchor="w", stretch=True)
        tree.grid(row=0, column=0, sticky="nsew")
        for idx, row in enumerate(rows):
            values = [self._display_value(key, row.get(key)) for key in keys]
            tree.insert("", "end", values=values, tags=("even" if idx % 2 == 0 else "odd",))
        tree.tag_configure("even", background=COLORS["surface"])
        tree.tag_configure("odd", background=COLORS["surface_alt"])
        if not rows:
            ctk.CTkLabel(parent, text="No hay registros para mostrar.", text_color=COLORS["muted"], font=(FONT, 10)).pack(pady=(0, 16))

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------
    def _show_dashboard(self) -> None:
        scroll = self._scroll_page()
        try:
            data = self.service.dashboard()
        except Exception as exc:
            self._page_heading(scroll, "Panel principal", "No fue posible cargar el resumen de la clínica.")
            self._error_panel(scroll, "No se pudo consultar el panel", str(exc), lambda: self.show_page("dashboard"))
            return

        self._page_heading(scroll, self._greeting(), "Este es el resumen operativo de tu clínica veterinaria.")

        hero = ctk.CTkFrame(scroll, fg_color=COLORS["navy"], corner_radius=18)
        hero.pack(fill="x", padx=30, pady=(0, 18))
        hero.grid_columnconfigure(0, weight=1)
        hero_text = ctk.CTkFrame(hero, fg_color="transparent")
        hero_text.grid(row=0, column=0, sticky="w", padx=24, pady=22)
        ctk.CTkLabel(hero_text, text="CUIDADO, CONTROL Y SEGUIMIENTO", text_color="#A9C5E6", font=(FONT_DISPLAY, 8)).pack(anchor="w")
        ctk.CTkLabel(hero_text, text="Todo sobre tus pacientes,\nen un solo lugar.", text_color=COLORS["white"], font=(FONT_DISPLAY, 20), justify="left").pack(anchor="w", pady=(7, 5))
        ctk.CTkLabel(hero_text, text="Organiza la atención, consulta historiales y mantén al día las vacunas.", text_color="#D0DCE9", font=(FONT, 9)).pack(anchor="w")
        ctk.CTkButton(
            hero, text="＋  Agendar una cita", width=157, height=40, corner_radius=10,
            fg_color=COLORS["teal"], hover_color="#108576", text_color=COLORS["white"],
            font=(FONT_DISPLAY, 9), command=lambda: self._open_create("appointments"),
        ).grid(row=0, column=1, padx=24, pady=24, sticky="e")

        cards = ctk.CTkFrame(scroll, fg_color="transparent")
        cards.pack(fill="x", padx=24, pady=(0, 17))
        self._metric_card(cards, "Propietarios activos", data.get("owners", 0), "Responsables registrados", "♙", COLORS["blue"], COLORS["blue_soft"])
        self._metric_card(cards, "Mascotas activas", data.get("pets", 0), "Pacientes en seguimiento", "♧", COLORS["teal"], COLORS["teal_soft"])
        self._metric_card(cards, "Citas de hoy", data.get("appointments_today", 0), "Atenciones programadas", "◷", COLORS["purple"], COLORS["purple_bg"])
        self._metric_card(cards, "Alertas de vacunas", data.get("vaccines_alerts", 0), "Vencidas o próximas", "♡", COLORS["orange"], COLORS["orange_bg"])

        content_row = ctk.CTkFrame(scroll, fg_color="transparent")
        content_row.pack(fill="both", expand=True, padx=30, pady=(0, 18))
        content_row.grid_columnconfigure(0, weight=3)
        content_row.grid_columnconfigure(1, weight=2)
        content_row.grid_rowconfigure(0, weight=1)

        agenda = self._panel(content_row, "Próximas citas", "Agenda de atención y seguimiento")
        agenda.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ctk.CTkButton(
            agenda, text="Ver agenda", width=94, height=28, corner_radius=8,
            fg_color=COLORS["blue_soft"], hover_color="#DDE8FF", text_color=COLORS["blue"],
            font=(FONT_DISPLAY, 8), command=lambda: self.show_page("appointments"),
        ).place(relx=1.0, x=-17, y=14, anchor="ne")
        upcoming = data.get("upcoming", [])
        self._small_tree(agenda, ["Fecha", "Hora", "Mascota", "Veterinario", "Estado"],
                         ["appointment_date", "appointment_time", "pet_name", "vet_name", "status"],
                         upcoming, [90, 65, 120, 145, 95], height=7)

        right_stack = ctk.CTkFrame(content_row, fg_color="transparent")
        right_stack.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        alerts = self._panel(right_stack, "Alertas de vacunación", "Dosis vencidas o próximas a vencer")
        alerts.pack(fill="both", expand=True, pady=(0, 12))
        vaccine_items = data.get("vaccine_alerts", [])
        if vaccine_items:
            for item in vaccine_items[:4]:
                self._vaccine_alert_row(alerts, item)
        else:
            self._empty_hint(alerts, "✓", "Todo al día", "No hay alertas de vacunación pendientes.")

        quick = self._panel(right_stack, "Accesos rápidos", "Tareas frecuentes")
        quick.pack(fill="x")
        quick_grid = ctk.CTkFrame(quick, fg_color="transparent")
        quick_grid.pack(fill="x", padx=13, pady=(0, 13))
        quick_grid.grid_columnconfigure((0, 1), weight=1)
        self._quick_action(quick_grid, 0, 0, "＋", "Nuevo propietario", COLORS["blue"], lambda: self._open_create("owners"))
        self._quick_action(quick_grid, 0, 1, "♧", "Nueva mascota", COLORS["teal"], lambda: self._open_create("pets"))
        self._quick_action(quick_grid, 1, 0, "◷", "Agendar cita", COLORS["purple"], lambda: self._open_create("appointments"))
        self._quick_action(quick_grid, 1, 1, "♡", "Registrar vacuna", COLORS["orange"], lambda: self._open_create("vaccines"))

        foot = ctk.CTkFrame(scroll, fg_color="transparent")
        foot.pack(fill="x", padx=30, pady=(0, 22))
        ctk.CTkLabel(foot, text="MiMascota · Gestión veterinaria", text_color=COLORS["muted"], font=(FONT, 8)).pack(side="left")
        ctk.CTkLabel(foot, text="Los datos del panel se actualizan al entrar o presionar F5.", text_color=COLORS["muted"], font=(FONT, 8)).pack(side="right")

    def _vaccine_alert_row(self, parent, item: dict[str, Any]) -> None:
        row = ctk.CTkFrame(parent, fg_color=COLORS["surface_alt"], corner_radius=10)
        row.pack(fill="x", padx=13, pady=4)
        icon = ctk.CTkFrame(row, width=33, height=33, corner_radius=9, fg_color=COLORS["orange_bg"])
        icon.pack(side="left", padx=(9, 8), pady=8)
        icon.pack_propagate(False)
        ctk.CTkLabel(icon, text="♡", text_color=COLORS["orange"], font=(FONT_DISPLAY, 14)).pack(expand=True)
        text = ctk.CTkFrame(row, fg_color="transparent")
        text.pack(side="left", fill="x", expand=True, pady=7)
        ctk.CTkLabel(text, text=item.get("pet_name", "Mascota"), text_color=COLORS["text"], font=(FONT_DISPLAY, 9)).pack(anchor="w")
        detail = f"{item.get('vaccine_name', 'Vacuna')} · {self._format_date(item.get('next_dose_date'))}"
        ctk.CTkLabel(text, text=detail, text_color=COLORS["muted"], font=(FONT, 8)).pack(anchor="w", pady=(2, 0))
        status = str(item.get("status", "Por vencer"))
        bg, fg = STATUS_STYLES.get(status.lower(), (COLORS["orange_bg"], COLORS["orange"]))
        ctk.CTkLabel(row, text=status, fg_color=bg, text_color=fg, corner_radius=7, font=(FONT_DISPLAY, 8), padx=8, pady=5).pack(side="right", padx=9)

    def _quick_action(self, parent, row: int, col: int, icon: str, label: str, accent: str, command) -> None:
        button = ctk.CTkButton(
            parent, text=f"{icon}  {label}", anchor="w", height=38, corner_radius=9,
            fg_color=COLORS["surface_alt"], hover_color=COLORS["surface_hover"],
            text_color=COLORS["text_soft"], font=(FONT, 9), command=command,
        )
        button.grid(row=row, column=col, sticky="ew", padx=4, pady=4)

    def _empty_hint(self, parent, icon: str, title: str, description: str) -> None:
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=20, pady=22)
        ctk.CTkLabel(wrap, text=icon, text_color=COLORS["green"], font=(FONT_DISPLAY, 22)).pack()
        ctk.CTkLabel(wrap, text=title, text_color=COLORS["text"], font=(FONT_DISPLAY, 10)).pack(pady=(5, 2))
        ctk.CTkLabel(wrap, text=description, text_color=COLORS["muted"], font=(FONT, 8), wraplength=260, justify="center").pack()

    # ------------------------------------------------------------------
    # Resource pages and table actions
    # ------------------------------------------------------------------
    def _show_resource_page(self, resource: str) -> None:
        config = RESOURCES[resource]
        scroll = self._scroll_page()
        self._page_heading(
            scroll,
            config["title"],
            config["description"],
            f"＋  Nuevo {config['singular'].lower()}",
            lambda: self._open_create(resource),
        )

        overview = ctk.CTkFrame(scroll, fg_color=COLORS["surface"], corner_radius=13, border_width=1, border_color=COLORS["border"])
        overview.pack(fill="x", padx=30, pady=(0, 14))
        overview.grid_columnconfigure((0, 1, 2), weight=1)
        self.stat_labels = {}
        for col, (key, title) in enumerate((("total", "REGISTROS"), ("active", "ACTIVOS / VIGENTES"), ("inactive", "INACTIVOS / OTROS"))):
            cell = ctk.CTkFrame(overview, fg_color="transparent")
            cell.grid(row=0, column=col, sticky="ew", padx=18, pady=13)
            if col > 0:
                ctk.CTkFrame(overview, width=1, height=34, fg_color=COLORS["border"]).place(relx=col / 3, rely=0.5, anchor="center")
            ctk.CTkLabel(cell, text=title, text_color=COLORS["muted"], font=(FONT_DISPLAY, 8)).pack(anchor="w")
            number = ctk.CTkLabel(cell, text="—", text_color=COLORS["text"], font=(FONT_DISPLAY, 18))
            number.pack(anchor="w", pady=(3, 0))
            self.stat_labels[key] = number

        toolbar = ctk.CTkFrame(scroll, fg_color="transparent")
        toolbar.pack(fill="x", padx=30, pady=(0, 12))
        search_box = ctk.CTkFrame(toolbar, fg_color=COLORS["surface"], border_width=1, border_color=COLORS["border"], corner_radius=10)
        search_box.pack(side="left", fill="x", expand=True, padx=(0, 9))
        ctk.CTkLabel(search_box, text="⌕", text_color=COLORS["muted"], font=(FONT_DISPLAY, 18)).pack(side="left", padx=(12, 5))
        self.search_entry = ctk.CTkEntry(
            search_box, textvariable=self.search_var, placeholder_text=f"Buscar por nombre, documento, teléfono…",
            border_width=0, fg_color="transparent", height=40, font=(FONT, 10), text_color=COLORS["text"],
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda _event: self._render_table(resource))

        filter_values = FILTERS.get(resource, ["Todos"])
        self.filter_menu = ctk.CTkOptionMenu(
            toolbar, values=filter_values, variable=self.filter_var, width=142, height=40,
            corner_radius=9, fg_color=COLORS["surface"], button_color=COLORS["surface_hover"],
            button_hover_color=COLORS["border"], text_color=COLORS["text"],
            dropdown_fg_color=COLORS["surface"], dropdown_text_color=COLORS["text"],
            font=(FONT, 9), command=lambda _value: self._render_table(resource),
        )
        self.filter_menu.pack(side="left", padx=(0, 9))
        self._outline_button(toolbar, "↻  Actualizar", 103, lambda: self._load_resource(resource)).pack(side="left", padx=(0, 8))
        self._outline_button(toolbar, "⇩  Exportar", 96, lambda: self._export_csv(resource)).pack(side="left")

        table_card = ctk.CTkFrame(scroll, fg_color=COLORS["surface"], corner_radius=15, border_width=1, border_color=COLORS["border"])
        table_card.pack(fill="both", expand=True, padx=30, pady=(0, 22))
        table_card.grid_rowconfigure(1, weight=1)
        table_card.grid_columnconfigure(0, weight=1)
        table_head = ctk.CTkFrame(table_card, fg_color="transparent")
        table_head.grid(row=0, column=0, sticky="ew", padx=18, pady=(15, 10))
        ctk.CTkLabel(table_head, text="Listado de registros", text_color=COLORS["text"], font=(FONT_DISPLAY, 12)).pack(side="left")
        self.count_label = ctk.CTkLabel(table_head, text="Cargando…", text_color=COLORS["muted"], font=(FONT, 9))
        self.count_label.pack(side="right")

        table_wrap = ctk.CTkFrame(table_card, fg_color="transparent")
        table_wrap.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 9))
        table_wrap.grid_rowconfigure(0, weight=1)
        table_wrap.grid_columnconfigure(0, weight=1)
        keys = [col[0] for col in config["columns"]]
        self.tree = ttk.Treeview(table_wrap, columns=keys, show="headings", style="Mi.Treeview", selectmode="browse")
        for key, title, width in config["columns"]:
            self.tree.heading(key, text=title)
            self.tree.column(key, width=width, minwidth=68, anchor="w", stretch=True)
        yscroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        xscroll = ttk.Scrollbar(table_wrap, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        self.tree.bind("<Double-1>", lambda _event: self._open_edit(resource))
        self.tree.tag_configure("even", background=COLORS["surface"])
        self.tree.tag_configure("odd", background=COLORS["surface_alt"])
        self.tree.tag_configure("warning", foreground=COLORS["orange"])
        self.tree.tag_configure("danger", foreground=COLORS["red"])

        actions = ctk.CTkFrame(table_card, fg_color=COLORS["surface_alt"], corner_radius=10)
        actions.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))
        ctk.CTkLabel(actions, text="Doble clic sobre un registro para editarlo", text_color=COLORS["muted"], font=(FONT, 8)).pack(side="left", padx=13, pady=11)
        if resource == "appointments":
            self._action_button(actions, "Registrar atención", COLORS["teal"], "white", lambda: self._attend_selected(resource), width=132).pack(side="right", padx=5, pady=6)
            self._action_button(actions, "Cancelar cita", COLORS["red_bg"], COLORS["red"], lambda: self._cancel_selected(resource), width=112).pack(side="right", padx=5, pady=6)
        elif config.get("deactivate"):
            self._action_button(actions, "Desactivar", COLORS["red_bg"], COLORS["red"], lambda: self._deactivate_selected(resource), width=100).pack(side="right", padx=5, pady=6)
        self._action_button(actions, "Editar seleccionado", COLORS["surface"], COLORS["text"], lambda: self._open_edit(resource), width=145, border=True).pack(side="right", padx=5, pady=6)

        self._load_resource(resource)

    def _outline_button(self, parent, text: str, width: int, command):
        return ctk.CTkButton(
            parent, text=text, width=width, height=40, corner_radius=9,
            fg_color=COLORS["surface"], hover_color=COLORS["surface_hover"],
            text_color=COLORS["text_soft"], border_width=1, border_color=COLORS["border"],
            font=(FONT_DISPLAY, 9), command=command,
        )

    def _action_button(self, parent, text, fg, text_color, command, width=120, border=False):
        return ctk.CTkButton(
            parent, text=text, width=width, height=33, corner_radius=8,
            fg_color=fg, hover_color=COLORS["surface_hover"] if fg == COLORS["surface"] else fg,
            text_color=COLORS["white"] if text_color == "white" else text_color,
            border_width=1 if border else 0, border_color=COLORS["border"],
            font=(FONT_DISPLAY, 8), command=command,
        )

    def _load_resource(self, resource: str) -> None:
        try:
            self.current_items = self.service.list(resource)
            self._render_table(resource)
            self._update_resource_stats(resource)
        except Exception as exc:
            self.current_items = []
            self._render_table(resource)
            self._error_panel(self.page_scroll or self.content, "No se pudieron cargar los registros", str(exc), lambda: self._load_resource(resource))

    def _update_resource_stats(self, resource: str) -> None:
        total = len(self.current_items)
        active = sum(1 for item in self.current_items if item.get("active", True) and str(item.get("status", "")).lower() not in {"inactivo", "fallecida", "adoptada", "cancelada"})
        inactive = max(0, total - active)
        if resource == "appointments":
            active = sum(1 for item in self.current_items if item.get("status") in {"Programada", "Confirmada"})
            inactive = sum(1 for item in self.current_items if item.get("status") in {"Cancelada", "Atendida"})
        elif resource == "vaccines":
            active = sum(1 for item in self.current_items if item.get("status") == "Al día")
            inactive = sum(1 for item in self.current_items if item.get("status") in {"Vencida", "Por vencer"})
        for key, value in (("total", total), ("active", active), ("inactive", inactive)):
            label = self.stat_labels.get(key)
            if label and label.winfo_exists():
                label.configure(text=str(value))

    def _filter_matches(self, resource: str, item: dict[str, Any], selected: str) -> bool:
        if selected in {"Todos", "Todas"}:
            return True
        status = str(item.get("status", ""))
        active = item.get("active", True)
        if selected == "Activos":
            return active is not False and status.lower() not in {"inactivo", "fallecida", "adoptada"}
        if selected in {"Inactivos", "Inactivas"}:
            return active is False or status.lower() == "inactivo"
        if selected == "Activas":
            return active is not False and status.lower() == "activa"
        return status.lower() == selected.lower()

    def _render_table(self, resource: str) -> None:
        if self.tree is None or not self.tree.winfo_exists():
            return
        self.tree.delete(*self.tree.get_children())
        config = RESOURCES[resource]
        term = self.search_var.get().strip().lower()
        selected_filter = self.filter_var.get()
        visible: list[dict[str, Any]] = []
        for item in self.current_items:
            if not self._filter_matches(resource, item, selected_filter):
                continue
            haystack = " ".join(str(item.get(key, "")) for key in config["search"]).lower()
            if term and term not in haystack:
                continue
            visible.append(item)
        self.filtered_items = visible
        for idx, item in enumerate(visible):
            values = [self._display_value(key, item.get(key)) for key, _heading, _width in config["columns"]]
            status = str(item.get("status", "")).lower()
            tag = "even" if idx % 2 == 0 else "odd"
            if status in {"vencida", "cancelada"}:
                tag = "danger"
            elif status == "por vencer":
                tag = "warning"
            self.tree.insert("", "end", iid=str(item.get("id", idx)), values=values, tags=(tag,))
        if self.count_label and self.count_label.winfo_exists():
            self.count_label.configure(text=f"{len(visible)} de {len(self.current_items)} registros")
        if not visible:
            # Keep the table clean; the count label communicates the empty result.
            pass

    def _display_value(self, key: str, value: Any) -> str:
        if value in (None, ""):
            return "—"
        if key == "price":
            try:
                return f"$ {int(float(value)):,.0f}".replace(",", ".")
            except (ValueError, TypeError):
                return str(value)
        if key in {"birth_date", "appointment_date", "administered_date", "next_dose_date", "created_at"}:
            return self._format_date(value)
        if key == "weight_kg":
            return f"{value} kg"
        return str(value)

    @staticmethod
    def _format_date(value: Any) -> str:
        if not value:
            return "—"
        try:
            parsed = date.fromisoformat(str(value)[:10])
            return parsed.strftime("%d/%m/%Y")
        except ValueError:
            return str(value)

    def _selected_item(self, resource: str) -> dict[str, Any] | None:
        if self.tree is None:
            return None
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Selecciona un registro", "Primero selecciona una fila de la tabla.", parent=self)
            return None
        record_id = selection[0]
        return next((item for item in self.current_items if str(item.get("id")) == str(record_id)), None)

    def _open_create(self, resource: str) -> None:
        if resource not in RESOURCES:
            return
        config = RESOURCES[resource]
        title = "Registrar atención clínica" if resource == "records" else f"Nuevo {config['singular'].lower()}"
        try:
            FormDialog(self, title, config["fields"], self.service, lambda payload: self._save_create(resource, payload))
        except Exception as exc:
            messagebox.showerror("No se pudo abrir el formulario", str(exc), parent=self)

    def _save_create(self, resource: str, payload: dict[str, Any]) -> None:
        if resource == "records":
            appointment_id = payload.pop("appointment_id")
            self.service.attend_appointment(appointment_id, payload)
        else:
            self.service.create(resource, payload)
        self.show_page(resource)
        messagebox.showinfo("Registro guardado", "La información se guardó correctamente.", parent=self)

    def _open_edit(self, resource: str) -> None:
        item = self._selected_item(resource)
        if not item:
            return
        config = RESOURCES[resource]
        initial = {field[0]: item.get(field[0]) for field in config["fields"]}
        try:
            FormDialog(self, f"Editar {config['singular'].lower()}", config["fields"], self.service,
                       lambda payload: self._save_edit(resource, item["id"], payload), initial=initial)
        except Exception as exc:
            messagebox.showerror("No se pudo abrir el formulario", str(exc), parent=self)

    def _save_edit(self, resource: str, record_id: Any, payload: dict[str, Any]) -> None:
        self.service.update(resource, record_id, payload)
        self.show_page(resource)
        messagebox.showinfo("Cambios guardados", "El registro se actualizó correctamente.", parent=self)

    def _deactivate_selected(self, resource: str) -> None:
        item = self._selected_item(resource)
        if not item:
            return
        if not messagebox.askyesno("Desactivar registro", "El registro se marcará como inactivo. No se eliminará físicamente ni se perderá su historial.", parent=self):
            return
        try:
            self.service.deactivate(resource, item["id"])
            self.show_page(resource)
            messagebox.showinfo("Registro desactivado", "El registro se conservó y quedó inactivo.", parent=self)
        except Exception as exc:
            messagebox.showerror("No se pudo desactivar", str(exc), parent=self)

    def _cancel_selected(self, resource: str) -> None:
        item = self._selected_item(resource)
        if not item:
            return
        if item.get("status") == "Atendida":
            messagebox.showwarning("Cita atendida", "Una cita atendida no se puede cancelar.", parent=self)
            return
        if not messagebox.askyesno("Cancelar cita", "¿Confirmas la cancelación de esta cita?", parent=self):
            return
        try:
            self.service.cancel_appointment(item["id"])
            self.show_page(resource)
            messagebox.showinfo("Cita cancelada", "La cita quedó marcada como cancelada.", parent=self)
        except Exception as exc:
            messagebox.showerror("No se pudo cancelar", str(exc), parent=self)

    def _attend_selected(self, resource: str) -> None:
        item = self._selected_item(resource)
        if not item:
            return
        if item.get("status") == "Cancelada":
            messagebox.showwarning("Cita cancelada", "No se puede registrar la atención de una cita cancelada.", parent=self)
            return
        try:
            existing_records = self.service.list("records")
            if any(str(row.get("appointment_id")) == str(item.get("id")) for row in existing_records):
                messagebox.showwarning("Atención existente", "Esta cita ya tiene un registro de historial clínico.", parent=self)
                return
        except Exception as exc:
            messagebox.showerror("No se pudo validar el historial", str(exc), parent=self)
            return
        fields = [
            ("diagnosis", "Diagnóstico", "multiline", True, None),
            ("treatment", "Tratamiento", "multiline", False, None),
            ("weight_kg", "Peso (kg)", "text", False, None),
            ("medications", "Medicamentos", "multiline", False, None),
            ("notes", "Observaciones", "multiline", False, None),
        ]
        FormDialog(self, f"Registrar atención · {item.get('pet_name', 'Mascota')}", fields, self.service,
                   lambda payload: self._save_attendance(item["id"], payload), width=650)

    def _save_attendance(self, appointment_id: Any, payload: dict[str, Any]) -> None:
        self.service.attend_appointment(appointment_id, payload)
        self.show_page("appointments")
        messagebox.showinfo("Atención registrada", "Se registró el historial clínico y se actualizó el estado de la cita.", parent=self)

    def _export_csv(self, resource: str) -> None:
        if not self.filtered_items:
            messagebox.showinfo("Sin registros", "No hay registros para exportar con los filtros actuales.", parent=self)
            return
        config = RESOURCES[resource]
        path = filedialog.asksaveasfilename(
            parent=self,
            title="Exportar registros",
            defaultextension=".csv",
            initialfile=f"mimascota_{resource}_{date.today().isoformat()}.csv",
            filetypes=[("Archivo CSV", "*.csv")],
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file, delimiter=";")
                writer.writerow([heading for _key, heading, _width in config["columns"]])
                for item in self.filtered_items:
                    writer.writerow([self._display_value(key, item.get(key)) for key, _heading, _width in config["columns"]])
            messagebox.showinfo("Exportación completada", f"Se exportaron {len(self.filtered_items)} registros.", parent=self)
        except OSError as exc:
            messagebox.showerror("No se pudo exportar", str(exc), parent=self)

    # ------------------------------------------------------------------
    # Shared feedback
    # ------------------------------------------------------------------
    def _error_panel(self, parent, title: str, detail: str, retry) -> None:
        panel = ctk.CTkFrame(parent, fg_color=COLORS["surface"], corner_radius=14, border_width=1, border_color=COLORS["border"])
        panel.pack(fill="x", padx=30, pady=16)
        ctk.CTkLabel(panel, text="!", text_color=COLORS["red"], font=(FONT_DISPLAY, 24)).pack(anchor="w", padx=19, pady=(17, 0))
        ctk.CTkLabel(panel, text=title, text_color=COLORS["text"], font=(FONT_DISPLAY, 13)).pack(anchor="w", padx=19, pady=(5, 3))
        ctk.CTkLabel(panel, text=detail, text_color=COLORS["muted"], font=(FONT, 9), wraplength=850, justify="left").pack(anchor="w", padx=19)
        ctk.CTkButton(panel, text="Reintentar", width=110, height=34, corner_radius=8, fg_color=COLORS["blue"], hover_color=COLORS["blue_hover"], command=retry).pack(anchor="w", padx=19, pady=15)


def run() -> None:
    app = MiMascotaApp()
    app.mainloop()
