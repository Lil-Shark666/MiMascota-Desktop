"""Design system for MiMascota Desktop."""

COLORS = {
    # Brand
    "navy": "#14263D",
    "navy_deep": "#101F32",
    "navy_soft": "#1D3854",
    "blue": "#3574E8",
    "blue_hover": "#2863D1",
    "blue_soft": "#EAF1FF",
    "teal": "#159A8A",
    "teal_soft": "#E5F6F2",
    # App surfaces
    "bg": "#F4F6FA",
    "surface": "#FFFFFF",
    "surface_alt": "#F8FAFC",
    "surface_hover": "#F0F4F8",
    "border": "#E4EAF1",
    "border_strong": "#D5DEE8",
    # Typography
    "text": "#172536",
    "text_soft": "#45566B",
    "muted": "#77869A",
    "muted_light": "#A6B1BF",
    # Semantic
    "green": "#16845D",
    "green_bg": "#E8F6EF",
    "orange": "#B96C18",
    "orange_bg": "#FFF4E5",
    "red": "#B54747",
    "red_bg": "#FCEDEE",
    "purple": "#7357C8",
    "purple_bg": "#F1EEFC",
    "cyan": "#247EAA",
    "cyan_bg": "#EAF5FA",
    "white": "#FFFFFF",
}

FONT = "Segoe UI"
FONT_DISPLAY = "Segoe UI Semibold"

RADIUS = {
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 20,
}


def font(size: int = 11, weight: str = "normal"):
    family = FONT_DISPLAY if weight in {"bold", "semibold"} else FONT
    return (family, size)
