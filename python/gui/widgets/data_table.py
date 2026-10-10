# -*- coding: utf-8 -*-
"""DataTable widget: Reusable Treeview with card container, zebra rows, hover, empty state, and event callbacks."""

from typing import List, Tuple, Dict, Any, Optional, Callable, Union
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

from gui.styles import (
    COLORS,
    RADIUS,
    SPACING,
    font,
    button,
    apply_treeview_tags,
)


class DataTable(ctk.CTkFrame):
    """Componente reutilizable de tabla con diseño limpio, estados interactivos y callbacks."""

    def __init__(
        self,
        master,
        columns: Optional[List[Union[str, Tuple]]] = None,
        on_select: Optional[Callable[[Optional[str], Optional[Tuple]], None]] = None,
        on_double_click: Optional[Callable[[str, Tuple], None]] = None,
        empty_icon: str = "",
        empty_title: str = "No hay registros disponibles",
        empty_message: str = "No se encontraron datos para mostrar con los criterios actuales.",
        empty_action_text: Optional[str] = None,
        empty_action_command: Optional[Callable[[], None]] = None,
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

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._on_select_callback = on_select
        self._on_double_click_callback = on_double_click

        # Configuración de estado vacío enriquecido
        self._empty_icon = empty_icon
        self._empty_title = empty_title
        self._empty_message = empty_message
        self._empty_action_text = empty_action_text
        self._empty_action_command = empty_action_command

        # Seguimiento para el efecto hover
        self._last_hovered_item: Optional[str] = None
        self._original_tags: Dict[str, Tuple[str, ...]] = {}

        # Árbol Treeview con estilo personalizado Pea.Treeview
        self.tree = ttk.Treeview(self, show='headings', style='Pea.Treeview')
        apply_treeview_tags(self.tree)

        # Scrollbar vertical delgada y minimalista
        self.scrollbar = ttk.Scrollbar(
            self,
            orient='vertical',
            style='Pea.Vertical.TScrollbar',
            command=self.tree.yview,
        )
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Disposición dentro del contenedor redondeado
        self.tree.grid(row=0, column=0, sticky='nsew', padx=(1, 0), pady=1)
        self.scrollbar.grid(row=0, column=1, sticky='ns', padx=(0, 1), pady=1)

        # Contenedor enriquecido para el estado vacío
        self.empty_container = ctk.CTkFrame(self, fg_color=COLORS['surface'])

        self.empty_icon_label = ctk.CTkLabel(
            self.empty_container,
            text=self._empty_icon,
            font=font('heading'),
            text_color=COLORS['muted_light'],
        )
        if self._empty_icon:
            self.empty_icon_label.pack(pady=(0, SPACING['xs']))

        self.empty_title_label = ctk.CTkLabel(
            self.empty_container,
            text=self._empty_title,
            font=font('heading'),
            text_color=COLORS['ink'],
        )
        self.empty_title_label.pack(pady=(0, SPACING['xs']))

        self.empty_message_label = ctk.CTkLabel(
            self.empty_container,
            text=self._empty_message,
            font=font('body'),
            text_color=COLORS['muted'],
            wraplength=380,
            justify='center',
        )
        self.empty_message_label.pack(pady=(0, SPACING['md']))

        self.empty_action_btn = button(
            self.empty_container,
            text=self._empty_action_text or "Acción sugerida",
            variant='primary',
            command=self._handle_empty_action,
        )
        if self._empty_action_text and self._empty_action_command:
            self.empty_action_btn.pack()

        # Enlace de eventos de interacción
        self.tree.bind('<Motion>', self._on_motion)
        self.tree.bind('<Leave>', self._on_leave)
        self.tree.bind('<<TreeviewSelect>>', self._handle_select)
        self.tree.bind('<Double-1>', self._handle_double_click)

        if columns:
            self.set_columns(columns)

        self._update_empty_state()

    def set_empty_state(
        self,
        icon: Optional[str] = None,
        title: Optional[str] = None,
        message: Optional[str] = None,
        action_text: Optional[str] = None,
        action_command: Optional[Callable[[], None]] = None,
    ):
        """Actualiza dinámicamente la apariencia y acción del estado vacío."""
        if icon is not None:
            self._empty_icon = icon
            self.empty_icon_label.configure(text=icon)
        if title is not None:
            self._empty_title = title
            self.empty_title_label.configure(text=title)
        if message is not None:
            self._empty_message = message
            self.empty_message_label.configure(text=message)
        if action_text is not None:
            self._empty_action_text = action_text
            self.empty_action_btn.configure(text=action_text)
        if action_command is not None:
            self._empty_action_command = action_command

        if self._empty_action_text and self._empty_action_command:
            if not self.empty_action_btn.winfo_ismapped():
                self.empty_action_btn.pack()
        else:
            self.empty_action_btn.pack_forget()

        self._update_empty_state()

    def _handle_empty_action(self):
        """Ejecuta la acción configurada para el estado vacío."""
        if self._empty_action_command:
            self._empty_action_command()

    def set_columns(self, columns: List[Union[str, Tuple]]):
        """Define las columnas, encabezados, anchos y alineación del Treeview."""
        col_ids = []
        col_configs = []

        for col in columns:
            if isinstance(col, (tuple, list)):
                col_id = str(col[0])
                heading_text = str(col[1]) if len(col) > 1 else col_id.capitalize()
                width = int(col[2]) if len(col) > 2 else 120
                anchor = str(col[3]) if len(col) > 3 else 'w'
            else:
                col_id = str(col)
                heading_text = col_id.replace('_', ' ').capitalize()
                width = 120
                anchor = 'w'

            col_ids.append(col_id)
            col_configs.append((col_id, heading_text, width, anchor))

        self.tree['columns'] = col_ids
        for col_id, heading_text, width, anchor in col_configs:
            self.tree.heading(col_id, text=heading_text, anchor=anchor)
            self.tree.column(col_id, width=width, anchor=anchor, stretch=True)

    def insert_row(
        self,
        values: Union[List, Tuple],
        iid: Optional[str] = None,
        is_active: bool = True,
    ) -> str:
        """Inserta una fila con alternancia zebra y badge de estado."""
        count = len(self.tree.get_children())
        zebra_tag = 'odd' if count % 2 == 0 else 'even'
        badge_tag = 'active_badge' if is_active else 'inactive_badge'
        tags = (zebra_tag, badge_tag)

        item_id = self.tree.insert('', 'end', iid=iid, values=values, tags=tags)
        self._update_empty_state()
        return item_id

    def set_rows(
        self,
        rows: List[Union[List, Tuple]],
        id_index: Optional[int] = None,
        active_index: Optional[int] = None,
    ):
        """Reemplaza todas las filas de la tabla con una nueva lista de datos."""
        self.clear()
        for idx, row in enumerate(rows):
            row_tuple = tuple(row)
            iid = str(row_tuple[id_index]) if id_index is not None and id_index < len(row_tuple) else None
            is_active = True
            if active_index is not None and active_index < len(row_tuple):
                val = row_tuple[active_index]
                if isinstance(val, bool):
                    is_active = val
                elif isinstance(val, (int, float)):
                    is_active = bool(val)
                elif isinstance(val, str):
                    is_active = 'inactiv' not in val.strip().lower() and val.strip().lower() not in ('no', 'false', '0')

            self.insert_row(row_tuple, iid=iid, is_active=is_active)

    def clear(self):
        """Elimina todos los elementos de la tabla y limpia estados temporales."""
        self._clear_hover()
        self._original_tags.clear()
        for child in self.tree.get_children():
            self.tree.delete(child)
        self._update_empty_state()
        if self._on_select_callback:
            self._on_select_callback(None, None)

    def get_selected_id(self) -> Optional[str]:
        """Retorna el identificador (iid) de la fila seleccionada, o None."""
        selected = self.tree.selection()
        return selected[0] if selected else None

    def get_selected_values(self) -> Optional[Tuple[Any, ...]]:
        """Retorna los valores de la fila seleccionada, o None."""
        selected_id = self.get_selected_id()
        if selected_id and self.tree.exists(selected_id):
            return tuple(self.tree.item(selected_id, 'values'))
        return None

    def select_row(self, iid: str):
        """Selecciona y enfoca una fila específica por su iid."""
        if self.tree.exists(iid):
            self.tree.selection_set(iid)
            self.tree.focus(iid)
            self.tree.see(iid)

    def get_row_count(self) -> int:
        """Retorna el número actual de registros en la tabla."""
        return len(self.tree.get_children())

    def set_on_select(self, callback: Optional[Callable[[Optional[str], Optional[Tuple]], None]]):
        """Asigna o actualiza el callback de selección de fila."""
        self._on_select_callback = callback

    def set_on_double_click(self, callback: Optional[Callable[[str, Tuple], None]]):
        """Asigna o actualiza el callback de doble clic en una fila."""
        self._on_double_click_callback = callback

    # --- Manejadores internos de eventos ---

    def _update_empty_state(self):
        """Muestra u oculta el contenedor centrado de estado vacío."""
        if len(self.tree.get_children()) == 0:
            self.empty_container.place(relx=0.5, rely=0.5, anchor='center')
        else:
            self.empty_container.place_forget()

    def _clear_hover(self):
        """Restaura las etiquetas originales de la fila actualmente en hover."""
        if self._last_hovered_item:
            if self.tree.exists(self._last_hovered_item):
                orig_tags = self._original_tags.pop(self._last_hovered_item, ('odd',))
                self.tree.item(self._last_hovered_item, tags=orig_tags)
            else:
                self._original_tags.pop(self._last_hovered_item, None)
            self._last_hovered_item = None

    def _on_motion(self, event):
        """Gestiona el efecto hover al mover el puntero sobre las filas."""
        item = self.tree.identify_row(event.y)
        if item == self._last_hovered_item:
            return

        self._clear_hover()

        if item and self.tree.exists(item):
            self._last_hovered_item = item
            current_tags = tuple(self.tree.item(item, 'tags'))
            self._original_tags[item] = current_tags

            # Quita los tags de zebra (odd/even) para que no compitan con el fondo de hover
            cleaned_tags = tuple(t for t in current_tags if t not in ('odd', 'even'))
            hover_tags = cleaned_tags + ('hover',)
            self.tree.item(item, tags=hover_tags)

    def _on_leave(self, event=None):
        """Limpia el efecto hover cuando el puntero sale del área de la tabla."""
        self._clear_hover()

    def _handle_select(self, event=None):
        """Notifica al callback de selección cuando cambia la fila seleccionada."""
        if self._on_select_callback:
            selected = self.tree.selection()
            if selected:
                item_id = selected[0]
                values = tuple(self.tree.item(item_id, 'values'))
                self._on_select_callback(item_id, values)
            else:
                self._on_select_callback(None, None)

    def _handle_double_click(self, event):
        """Notifica al callback de doble clic cuando se presiona dos veces una fila."""
        if self._on_double_click_callback:
            item_id = self.tree.identify_row(event.y)
            if item_id and self.tree.exists(item_id):
                values = tuple(self.tree.item(item_id, 'values'))
                self._on_double_click_callback(item_id, values)
