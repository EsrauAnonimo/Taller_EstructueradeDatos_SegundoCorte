# -*- coding: utf-8 -*-
"""StatCard widget for displaying summary metrics."""

from typing import Optional
import customtkinter as ctk
from gui.styles import COLORS, RADIUS, SPACING, font


class StatCard(ctk.CTkFrame):
    """Tarjeta de métricas estadísticas con borde fino, barra vertical y tipografía destacada."""

    def __init__(
        self,
        master,
        title: str,
        value: str = "0",
        note: Optional[str] = None,
        accent_color: Optional[str] = None,
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

        # Contenedor interno con espaciado consistente de 16 px
        self.inner_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.inner_frame.pack(fill='both', expand=True, padx=SPACING['md'], pady=SPACING['md'])

        # Barra lateral indicadora de color (4 px de ancho)
        self.bar = ctk.CTkFrame(
            self.inner_frame,
            width=4,
            corner_radius=2,
            fg_color=self.accent_color,
        )
        self.bar.pack(side='left', fill='y', padx=(0, SPACING['md']))

        # Contenedor de textos vertical
        self.content_frame = ctk.CTkFrame(self.inner_frame, fg_color='transparent')
        self.content_frame.pack(side='left', fill='both', expand=True)

        # Etiqueta de título en tipografía muted pequeña
        self.lbl_title = ctk.CTkLabel(
            self.content_frame,
            text=title,
            font=font('small'),
            text_color=COLORS['muted'],
            anchor='w',
        )
        self.lbl_title.pack(fill='x', anchor='w')

        # Valor numérico en fuente stat grande
        self.lbl_value = ctk.CTkLabel(
            self.content_frame,
            text=str(value),
            font=font('stat'),
            text_color=COLORS['ink'],
            anchor='w',
        )
        self.lbl_value.pack(fill='x', anchor='w', pady=(2, 2))

        # Nota descriptiva inferior opcional
        self.lbl_note = ctk.CTkLabel(
            self.content_frame,
            text=note or "",
            font=font('small'),
            text_color=COLORS['muted'],
            anchor='w',
        )
        if note:
            self.lbl_note.pack(fill='x', anchor='w')

    def set_value(self, value, note: Optional[str] = None):
        """Actualiza el valor numérico mostrado y opcionalmente su nota auxiliar."""
        self.lbl_value.configure(text=str(value))
        if note is not None:
            self.lbl_note.configure(text=str(note))
            if not self.lbl_note.winfo_ismapped():
                self.lbl_note.pack(fill='x', anchor='w')
