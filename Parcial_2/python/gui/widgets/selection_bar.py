# -*- coding: utf-8 -*-
"""SelectionActionBar: Barra flotante contextual para acciones sobre filas seleccionadas."""

from typing import Optional, Callable
import customtkinter as ctk

from gui.styles import (
    COLORS,
    RADIUS,
    SPACING,
    CONTROL_HEIGHT,
    font,
    button,
)


class SelectionActionBar(ctk.CTkFrame):
    """Barra contextual que se muestra sobre la tabla únicamente cuando hay registros seleccionados.

    Características:
    - Muestra chip indicando 'N seleccionados'.
    - Botón 'Editar' (activo solo con 1 registro seleccionado).
    - Botón unificado 'Activar / Desactivar' con texto dinámico.
    - Botón 'Eliminar' con estilo destructivo (rojo suave).
    - Botón discreto para limpiar la selección.
    """

    def __init__(
        self,
        master,
        on_edit: Optional[Callable[[], None]] = None,
        on_toggle_active: Optional[Callable[[], None]] = None,
        on_delete: Optional[Callable[[], None]] = None,
        on_clear: Optional[Callable[[], None]] = None,
        **kwargs,
    ):
        base_kwargs = {
            'height': 48,
            'fg_color': COLORS['surface'],
            'corner_radius': RADIUS['control'],
            'border_width': 1,
            'border_color': COLORS['accent_border'],
        }
        merged_kwargs = {**base_kwargs, **kwargs}
        super().__init__(master, **merged_kwargs)

        self._on_edit = on_edit
        self._on_toggle_active = on_toggle_active
        self._on_delete = on_delete
        self._on_clear = on_clear

        # Contenedor izquierdo: Chip de conteo y botón para limpiar
        self.left_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.left_frame.pack(side='left', padx=SPACING['md'], pady=6)

        self.chip_badge = ctk.CTkFrame(
            self.left_frame,
            fg_color=COLORS['accent_soft'],
            corner_radius=RADIUS['badge'],
        )
        self.chip_badge.pack(side='left', padx=(0, SPACING['sm']))

        self.chip_label = ctk.CTkLabel(
            self.chip_badge,
            text="0 seleccionados",
            font=font('badge'),
            text_color=COLORS['accent'],
        )
        self.chip_label.pack(padx=SPACING['sm'], pady=4)

        self.btn_clear = button(
            self.left_frame,
            text="Deseleccionar",
            variant='tertiary',
            command=self._handle_clear,
            height=30,
        )
        self.btn_clear.pack(side='left')

        # Contenedor derecho: Acciones contextuales sobre la selección
        self.right_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.right_frame.pack(side='right', padx=SPACING['md'], pady=6)

        # Botón Editar
        self.btn_edit = button(
            self.right_frame,
            text="Editar",
            variant='secondary',
            command=self._handle_edit,
            height=CONTROL_HEIGHT,
        )
        self.btn_edit.pack(side='left', padx=(0, SPACING['sm']))

        # Botón unificado Activar / Desactivar
        self.btn_toggle = button(
            self.right_frame,
            text="Desactivar",
            variant='secondary',
            command=self._handle_toggle,
            height=CONTROL_HEIGHT,
        )
        self.btn_toggle.pack(side='left', padx=(0, SPACING['sm']))

        # Separador vertical fino
        self.separator = ctk.CTkFrame(
            self.right_frame,
            width=1,
            height=24,
            fg_color=COLORS['border'],
            corner_radius=0,
        )
        self.separator.pack(side='left', padx=SPACING['xs'], pady=6)

        # Botón destructivo Eliminar
        self.btn_delete = button(
            self.right_frame,
            text="Eliminar",
            variant='danger',
            command=self._handle_delete,
            height=CONTROL_HEIGHT,
        )
        self.btn_delete.pack(side='left', padx=(SPACING['xs'], 0))

    def update_selection(self, count: int, is_active: bool = True):
        """Actualiza el estado visual y visibilidad de los botones según la selección."""
        if count == 0:
            self.chip_label.configure(text="0 seleccionados")
            self.btn_edit.configure(state='disabled')
            self.btn_toggle.configure(state='disabled', text="Desactivar")
            self.btn_delete.configure(state='disabled')
            return

        suffix = "seleccionado" if count == 1 else "seleccionados"
        self.chip_label.configure(text=f"{count} {suffix}")

        # Editar solo permitido con exactamente 1 seleccionado
        if count == 1:
            self.btn_edit.configure(state='normal')
        else:
            self.btn_edit.configure(state='disabled')

        # Unificación de Activar / Desactivar
        toggle_text = "Desactivar" if is_active else "Activar"
        self.btn_toggle.configure(state='normal', text=toggle_text)
        self.btn_delete.configure(state='normal')

    def _handle_edit(self):
        if self._on_edit:
            self._on_edit()

    def _handle_toggle(self):
        if self._on_toggle_active:
            self._on_toggle_active()

    def _handle_delete(self):
        if self._on_delete:
            self._on_delete()

    def _handle_clear(self):
        if self._on_clear:
            self._on_clear()
