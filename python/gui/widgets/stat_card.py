# -*- coding: utf-8 -*-
"""StatCard widget for displaying summary metrics."""

from typing import Optional
import customtkinter as ctk
from gui.styles import COLORS, RADIUS, SPACING, font


class StatCard(ctk.CTkFrame):
    """Tarjeta KPI compacta y moderna con ícono, métrica destacada y variación."""

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
            'corner_radius': RADIUS['card'],
            'fg_color': COLORS['surface'],
            'border_width': 1,
            'border_color': COLORS['border'],
        }
        merged_kwargs = {**base_kwargs, **kwargs}
        super().__init__(master, **merged_kwargs)

        self.accent_color = accent_color or COLORS['accent']

        # Contenedor interno compacto
        self.inner_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.inner_frame.pack(fill='both', expand=True, padx=SPACING['md'], pady=12)

        # Fila superior: Título a la izquierda
        self.top_row = ctk.CTkFrame(self.inner_frame, fg_color='transparent')
        self.top_row.pack(fill='x')

        self.lbl_title = ctk.CTkLabel(
            self.top_row,
            text=title.upper(),
            font=font('small'),
            text_color=COLORS['muted'],
            anchor='w',
        )
        self.lbl_title.pack(side='left', fill='x', expand=True)

        if icon:
            self.icon_badge = ctk.CTkLabel(
                self.top_row,
                text=icon,
                font=font('small'),
                width=28,
                height=28,
                corner_radius=14,
                fg_color=COLORS['surface_alt'],
            )
            self.icon_badge.pack(side='right')

        # Fila central: Valor numérico destacado
        self.lbl_value = ctk.CTkLabel(
            self.inner_frame,
            text=str(value),
            font=font('stat'),
            text_color=COLORS['ink'],
            anchor='w',
        )
        self.lbl_value.pack(fill='x', anchor='w', pady=(2, 4))

        # Fila inferior: Variación / nota auxiliar
        self.bottom_row = ctk.CTkFrame(self.inner_frame, fg_color='transparent')
        self.bottom_row.pack(fill='x', anchor='w')

        self.lbl_variation = ctk.CTkLabel(
            self.bottom_row,
            text=variation or "Registrado",
            font=font('small'),
            text_color=COLORS['badge_active_text'] if (variation and 'activo' in variation.lower()) else COLORS['muted'],
            anchor='w',
        )
        self.lbl_variation.pack(side='left', anchor='w')

        if note:
            self.lbl_note = ctk.CTkLabel(
                self.bottom_row,
                text=f" · {note}",
                font=font('small'),
                text_color=COLORS['muted_light'],
                anchor='w',
            )
            self.lbl_note.pack(side='left', anchor='w')
        else:
            self.lbl_note = None

    def set_value(self, value, note: Optional[str] = None, variation: Optional[str] = None):
        """Actualiza el valor numérico, variación y nota de la tarjeta."""
        self.lbl_value.configure(text=str(value))
        if variation is not None:
            self.lbl_variation.configure(text=str(variation))
            is_active_var = 'activo' in variation.lower() or '100%' in variation
            color = COLORS['badge_active_text'] if is_active_var else COLORS['muted']
            self.lbl_variation.configure(text_color=color)

        if note is not None and self.lbl_note is not None:
            self.lbl_note.configure(text=f" · {note}")
