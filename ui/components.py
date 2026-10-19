import customtkinter as ctk
from typing import Tuple, Optional
from ui.theme import (
    CORNER_RADIUS,
    COLOR_BG,
    COLOR_SURFACE_1,
    COLOR_SURFACE_2,
    COLOR_SURFACE_HOVER,
    COLOR_BORDER,
    COLOR_BORDER_FOCUS,
    COLOR_NEON_LIME,
    COLOR_HAZARD_ORANGE,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_DIM,
    COLOR_DANGER,
    COLOR_SUCCESS,
    FONT_FAMILY_MONO,
    FONT_TELEMETRY,
    FONT_TELEMETRY_BOLD,
    FONT_TELEMETRY_SMALL,
    FONT_BUTTON_PRIMARY,
    FONT_BADGE
)


class TacticalBadge(ctk.CTkFrame):
    """Streetwear / Industrial Monospace Telemetry Badge."""
    def __init__(
        self,
        parent,
        text: str,
        bg_color: str = COLOR_SURFACE_2,
        fg_color: str = COLOR_SURFACE_2,
        border_color: str = COLOR_BORDER,
        text_color: str = COLOR_NEON_LIME,
        **kwargs
    ):
        super().__init__(
            parent,
            corner_radius=CORNER_RADIUS,
            fg_color=fg_color,
            border_width=1,
            border_color=border_color,
            **kwargs
        )
        self.label = ctk.CTkLabel(
            self,
            text=text,
            font=FONT_BADGE,
            text_color=text_color,
            padx=8,
            pady=3
        )
        self.label.pack(fill="both", expand=True)

    def set_text(self, text: str, text_color: Optional[str] = None):
        self.label.configure(text=text)
        if text_color:
            self.label.configure(text_color=text_color)


class BrutalistButton(ctk.CTkButton):
    """Zero-radius, high-contrast industrial button."""
    def __init__(
        self,
        parent,
        text: str,
        variant: str = "primary",  # "primary", "secondary", "danger", "outline"
        command=None,
        width: int = 140,
        height: int = 36,
        **kwargs
    ):
        if variant == "primary":
            fg = COLOR_NEON_LIME
            hover_fg = "#E6FF4D"
            text_c = "#0A0A0A"
            border_c = COLOR_NEON_LIME
        elif variant == "danger":
            fg = COLOR_DANGER
            hover_fg = "#FF5555"
            text_c = "#FFFFFF"
            border_c = COLOR_DANGER
        elif variant == "outline":
            fg = "transparent"
            hover_fg = COLOR_SURFACE_2
            text_c = COLOR_NEON_LIME
            border_c = COLOR_NEON_LIME
        else:  # secondary / tactical
            fg = COLOR_SURFACE_2
            hover_fg = COLOR_SURFACE_HOVER
            text_c = COLOR_TEXT_PRIMARY
            border_c = COLOR_BORDER

        super().__init__(
            parent,
            text=text,
            corner_radius=CORNER_RADIUS,
            fg_color=fg,
            hover_color=hover_fg,
            text_color=text_c,
            border_width=1,
            border_color=border_c,
            font=FONT_BUTTON_PRIMARY,
            command=command,
            width=width,
            height=height,
            **kwargs
        )


class ConflictDialog(ctk.CTkToplevel):
    """
    Industrial Brutalist Conflict Resolution Modal.
    Prompts user when filename collision is detected at target destination.
    """
    def __init__(self, parent, src_path: str, dst_path: str):
        super().__init__(parent)
        self.title("[CONFL // RESOLUTION]")
        self.geometry("540x360")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG)

        # Make it modal
        self.transient(parent)
        self.grab_set()

        self.choice = "rename"  # default
        self.apply_to_all = False

        # Header Frame
        header = ctk.CTkFrame(self, fg_color=COLOR_SURFACE_1, corner_radius=CORNER_RADIUS, border_width=1, border_color=COLOR_HAZARD_ORANGE)
        header.pack(fill="x", padx=16, pady=(16, 8))

        ctk.CTkLabel(
            header,
            text="[!] FILE COLLISION DETECTED",
            font=FONT_TELEMETRY_BOLD,
            text_color=COLOR_HAZARD_ORANGE
        ).pack(anchor="w", padx=12, pady=(8, 2))

        ctk.CTkLabel(
            header,
            text="A file with identical naming already exists in the target directory.",
            font=FONT_TELEMETRY_SMALL,
            text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w", padx=12, pady=(0, 8))

        # File details container
        details_frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE_1, corner_radius=CORNER_RADIUS, border_width=1, border_color=COLOR_BORDER)
        details_frame.pack(fill="x", padx=16, pady=8)

        # Source
        ctk.CTkLabel(details_frame, text="SOURCE:", font=FONT_TELEMETRY_BOLD, text_color=COLOR_TEXT_MUTED).grid(row=0, column=0, sticky="w", padx=10, pady=(8, 2))
        ctk.CTkLabel(details_frame, text=src_path, font=FONT_TELEMETRY_SMALL, text_color=COLOR_TEXT_PRIMARY, wraplength=420, justify="left").grid(row=0, column=1, sticky="w", padx=4, pady=(8, 2))

        # Target
        ctk.CTkLabel(details_frame, text="TARGET:", font=FONT_TELEMETRY_BOLD, text_color=COLOR_TEXT_MUTED).grid(row=1, column=0, sticky="w", padx=10, pady=(2, 8))
        ctk.CTkLabel(details_frame, text=dst_path, font=FONT_TELEMETRY_SMALL, text_color=COLOR_NEON_LIME, wraplength=420, justify="left").grid(row=1, column=1, sticky="w", padx=4, pady=(2, 8))

        # Checkbox Apply To All
        self.var_apply_all = ctk.BooleanVar(value=False)
        cb = ctk.CTkCheckBox(
            self,
            text="Apply selection to all remaining collisions in this run",
            variable=self.var_apply_all,
            corner_radius=CORNER_RADIUS,
            font=FONT_TELEMETRY,
            fg_color=COLOR_NEON_LIME,
            checkmark_color="#0A0A0A",
            text_color=COLOR_TEXT_PRIMARY
        )
        cb.pack(anchor="w", padx=20, pady=10)

        # Action Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(12, 16))

        BrutalistButton(btn_frame, text="[RENAME]", variant="primary", width=120, command=lambda: self._select("rename")).pack(side="left", padx=4)
        BrutalistButton(btn_frame, text="[SKIP FILE]", variant="secondary", width=120, command=lambda: self._select("skip")).pack(side="left", padx=4)
        BrutalistButton(btn_frame, text="[OVERWRITE]", variant="danger", width=120, command=lambda: self._select("replace")).pack(side="left", padx=4)

        # Center on parent
        self.update_idletasks()
        try:
            px = parent.winfo_x() + (parent.winfo_width() // 2) - 270
            py = parent.winfo_y() + (parent.winfo_height() // 2) - 180
            self.geometry(f"+{px}+{py}")
        except Exception:
            pass

    def _select(self, action: str):
        self.choice = action
        self.apply_to_all = self.var_apply_all.get()
        self.destroy()

    def get_result(self) -> Tuple[str, bool]:
        self.master.wait_window(self)
        return self.choice, self.apply_to_all
