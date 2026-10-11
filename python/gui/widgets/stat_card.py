# -*- coding: utf-8 -*-
"""StatCard widget – tarjeta KPI compacta con barra de acento lateral."""

from typing import Optional
import customtkinter as ctk
from gui.styles import COLORS, RADIUS, SPACING, font


class StatCard(ctk.CTkFrame):
    """Tarjeta KPI compacta (~110 px) con barra de acento lateral izquierda,
    icono, numero grande y texto secundario.
    """

    _ACCENT_W = 4  # ancho de la barra lateral

    def __init__(
        self,
        master,
        title: str,
        value: str = "0",
        note: Optional[str] = None,
        icon: str = "",
        accent_color: Optional[str] = None,
        variation: Optional[str] = None,
        **kwargs,
    ):
        base_kwargs = {
            "corner_radius": RADIUS["card"],
            "fg_color": COLORS["surface"],
            "border_width": 1,
            "border_color": COLORS["border"],
            "height": 110,
        }
        merged_kwargs = {**base_kwargs, **kwargs}
        super().__init__(master, **merged_kwargs)
        self.grid_propagate(False)
        self.pack_propagate(False)

        self.accent_color = accent_color or COLORS["accent"]

        # Barra de acento lateral izquierda
        self._accent_bar = ctk.CTkFrame(
            self,
            width=self._ACCENT_W,
            corner_radius=0,
            fg_color=self.accent_color,
        )
        self._accent_bar.pack(side="left", fill="y")

        # Cuerpo principal
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(side="left", fill="both", expand=True,
                  padx=SPACING["md"], pady=SPACING["sm"])

        # Fila superior: titulo + icono
        top = ctk.CTkFrame(body, fg_color="transparent")
        top.pack(fill="x", anchor="w")

        self.lbl_title = ctk.CTkLabel(
            top,
            text=title.upper(),
            font=font("small"),
            text_color=COLORS["muted"],
            anchor="w",
        )
        self.lbl_title.pack(side="left", fill="x", expand=True)

        if icon:
            self.icon_badge = ctk.CTkLabel(
                top,
                text=icon,
                font=font("body"),
                width=30,
                height=30,
                corner_radius=8,
                fg_color=COLORS["accent_soft"],
                text_color=self.accent_color,
            )
            self.icon_badge.pack(side="right")

        # Valor numerico
        self.lbl_value = ctk.CTkLabel(
            body,
            text=str(value),
            font=font("stat"),
            text_color=COLORS["ink"],
            anchor="w",
        )
        self.lbl_value.pack(fill="x", anchor="w", pady=(2, 0))

        # Variacion / subtexto
        self.lbl_variation = ctk.CTkLabel(
            body,
            text=variation or "",
            font=font("small"),
            text_color=self._variation_color(variation),
            anchor="w",
        )
        self.lbl_variation.pack(fill="x", anchor="w")

        # Nota auxiliar (opcional)
        self.lbl_note = None
        if note:
            self.lbl_note = ctk.CTkLabel(
                body,
                text=note,
                font=font("small"),
                text_color=COLORS["muted_light"],
                anchor="w",
            )
            self.lbl_note.pack(fill="x", anchor="w")

    @staticmethod
    def _variation_color(text: Optional[str]) -> str:
        if not text:
            return COLORS["muted"]
        t = text.lower()
        if "activo" in t or "validado" in t:
            return COLORS["badge_active_text"]
        return COLORS["muted"]

    def set_value(self, value, variation: Optional[str] = None, note: Optional[str] = None):
        """Actualiza el valor numerico, variacion y nota."""
        self.lbl_value.configure(text=str(value))
        if variation is not None:
            self.lbl_variation.configure(
                text=str(variation),
                text_color=self._variation_color(variation),
            )
        if note is not None and self.lbl_note is not None:
            self.lbl_note.configure(text=note)
