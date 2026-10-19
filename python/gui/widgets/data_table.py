# -*- coding: utf-8 -*-
"""DataTable widget: Reusable Treeview con casillas de selección múltiple, hover, estado vacío y menú contextual."""

from typing import List, Tuple, Dict, Any, Optional, Callable, Union, Set
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
    """Componente reutilizable de tabla con diseño limpio, casillas de selección múltiple,
    ordenación por clic en cabecera, estados interactivos y callbacks de eventos."""

    ICON_UNCHECKED = "☐"
    ICON_CHECKED = "☑"
    _COL_CHK = "__chk__"

    def __init__(
        self,
        master,
        columns: Optional[List[Union[str, Tuple]]] = None,
        on_select: Optional[Callable[[Optional[str], Optional[Tuple]], None]] = None,
        on_selection_change: Optional[Callable[[List[str]], None]] = None,
        on_double_click: Optional[Callable[[str, Tuple], None]] = None,
        on_delete_key: Optional[Callable[[], None]] = None,
        on_context_menu: Optional[Callable[[Any, List[str]], None]] = None,
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
        self._on_selection_change_callback = on_selection_change
        self._on_double_click_callback = on_double_click
        self._on_delete_key_callback = on_delete_key
        self._on_context_menu_callback = on_context_menu

        # Configuración de estado vacío enriquecido
        self._empty_icon = empty_icon
        self._empty_title = empty_title
        self._empty_message = empty_message
        self._empty_action_text = empty_action_text
        self._empty_action_command = empty_action_command

        # Diccionarios de almacenamiento interno
        self._selected_ids: Set[str] = set()
        self._raw_values: Dict[str, Tuple[Any, ...]] = {}
        self._active_status: Dict[str, bool] = {}

        # Seguimiento para el efecto hover
        self._last_hovered_item: Optional[str] = None
        self._original_tags: Dict[str, Tuple[str, ...]] = {}

        # Árbol Treeview con estilo personalizado Pea.Treeview
        self.tree = ttk.Treeview(self, show='headings', style='Pea.Treeview', selectmode='extended')
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
        self.tree.bind('<Button-1>', self._on_tree_click, add='+')
        self.tree.bind('<Button-3>', self._on_right_click, add='+')
        self.tree.bind('<Double-1>', self._handle_double_click)
        self.tree.bind('<Return>', lambda e: self._handle_enter_key())
        self.tree.bind('<Delete>', lambda e: self._handle_delete_key())
        self.tree.bind('<space>', lambda e: self._handle_space_key())
        self.tree.bind('<Control-a>', lambda e: (self.select_all(), "break")[1])
        self.tree.bind('<Control-A>', lambda e: (self.select_all(), "break")[1])

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
        """Define las columnas, encabezados, anchos y alineación del Treeview, incluyendo la columna de casillas."""
        col_ids = [self._COL_CHK]
        col_configs = [(self._COL_CHK, self.ICON_UNCHECKED, 46, 'center')]

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

        # Columna especial de casillas con comando en el encabezado para seleccionar todo
        self.tree.heading(
            self._COL_CHK,
            text=self.ICON_UNCHECKED,
            anchor='center',
            command=self._toggle_select_all,
        )
        self.tree.column(self._COL_CHK, width=46, minwidth=46, stretch=False, anchor='center')

        # Configuración de las columnas de datos
        for col_id, heading_text, width, anchor in col_configs[1:]:
            self.tree.heading(col_id, text=heading_text, anchor=anchor)
            self.tree.column(col_id, width=width, anchor=anchor, stretch=True)

    def insert_row(
        self,
        values: Union[List, Tuple],
        iid: Optional[str] = None,
        is_active: bool = True,
    ) -> str:
        """Inserta una fila con alternancia zebra, badge de estado y casilla de selección."""
        count = len(self.tree.get_children())
        zebra_tag = 'odd' if count % 2 == 0 else 'even'
        badge_tag = 'active_badge' if is_active else 'inactive_badge'
        tags = (zebra_tag, badge_tag)

        # Genera identificador si no se especificó
        target_iid = str(iid) if iid is not None else f"item_{count + 1}"

        chk_val = self.ICON_CHECKED if target_iid in self._selected_ids else self.ICON_UNCHECKED
        row_display_values = (chk_val,) + tuple(values)

        item_id = self.tree.insert('', 'end', iid=target_iid, values=row_display_values, tags=tags)
        self._raw_values[item_id] = tuple(values)
        self._active_status[item_id] = bool(is_active)

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
        """Elimina todos los elementos de la tabla y limpia selecciones y estados temporales."""
        self._clear_hover()
        self._original_tags.clear()
        self._selected_ids.clear()
        self._raw_values.clear()
        self._active_status.clear()
        self.tree.heading(self._COL_CHK, text=self.ICON_UNCHECKED)

        for child in self.tree.get_children():
            self.tree.delete(child)

        self._update_empty_state()
        self._notify_selection_change()

    # --- Gestión de Selección Múltiple y Casillas ---

    def _toggle_select_all(self):
        """Alterna entre seleccionar todas las filas visibles o deseleccionarlas."""
        all_children = self.tree.get_children()
        if not all_children:
            return

        if len(self._selected_ids) == len(all_children):
            self.clear_selection()
        else:
            self.select_all()

    def select_all(self):
        """Marca y selecciona todas las filas de la tabla."""
        all_children = self.tree.get_children()
        self._selected_ids = set(all_children)
        self.tree.heading(self._COL_CHK, text=self.ICON_CHECKED)

        for iid in all_children:
            vals = list(self.tree.item(iid, 'values'))
            if vals:
                vals[0] = self.ICON_CHECKED
                self.tree.item(iid, values=vals)

        self.tree.selection_set(all_children)
        self._notify_selection_change()

    def clear_selection(self):
        """Deselecciona y desmarca todas las filas."""
        self._selected_ids.clear()
        self.tree.heading(self._COL_CHK, text=self.ICON_UNCHECKED)

        for iid in self.tree.get_children():
            vals = list(self.tree.item(iid, 'values'))
            if vals:
                vals[0] = self.ICON_UNCHECKED
                self.tree.item(iid, values=vals)

        self.tree.selection_set([])
        self._notify_selection_change()

    def toggle_row_selection(self, item_id: str):
        """Invierte la selección de una fila específica."""
        if not self.tree.exists(item_id):
            return

        if item_id in self._selected_ids:
            self._selected_ids.remove(item_id)
            new_icon = self.ICON_UNCHECKED
        else:
            self._selected_ids.add(item_id)
            new_icon = self.ICON_CHECKED

        vals = list(self.tree.item(item_id, 'values'))
        if vals:
            vals[0] = new_icon
            self.tree.item(item_id, values=vals)

        self._refresh_header_checkbox()
        self.tree.selection_set(list(self._selected_ids))
        self._notify_selection_change()

    def select_single_row(self, item_id: str):
        """Selecciona exclusivamente una fila, deseleccionando las demás."""
        if not self.tree.exists(item_id):
            return

        for prev_id in list(self._selected_ids):
            if prev_id != item_id and self.tree.exists(prev_id):
                vals = list(self.tree.item(prev_id, 'values'))
                if vals:
                    vals[0] = self.ICON_UNCHECKED
                    self.tree.item(prev_id, values=vals)

        self._selected_ids = {item_id}
        vals = list(self.tree.item(item_id, 'values'))
        if vals:
            vals[0] = self.ICON_CHECKED
            self.tree.item(item_id, values=vals)

        self._refresh_header_checkbox()
        self.tree.selection_set([item_id])
        self._notify_selection_change()

    def _refresh_header_checkbox(self):
        """Actualiza el ícono del encabezado según si todas o algunas filas están seleccionadas."""
        total = len(self.tree.get_children())
        if total > 0 and len(self._selected_ids) == total:
            self.tree.heading(self._COL_CHK, text=self.ICON_CHECKED)
        else:
            self.tree.heading(self._COL_CHK, text=self.ICON_UNCHECKED)

    def _notify_selection_change(self):
        """Dispara los callbacks de selección registrados."""
        ids = self.get_selected_ids()
        if self._on_selection_change_callback:
            self._on_selection_change_callback(ids)
        if self._on_select_callback:
            first_id = ids[0] if ids else None
            first_val = self.get_selected_values()
            self._on_select_callback(first_id, first_val)

    # --- Consultas Públicas de Selección y Datos ---

    def get_selected_ids(self) -> List[str]:
        """Retorna la lista de identificadores (iids) actualmente seleccionados."""
        return [iid for iid in self._selected_ids if self.tree.exists(iid)]

    def get_selected_id(self) -> Optional[str]:
        """Retorna el primer identificador seleccionado, o None."""
        selected = self.get_selected_ids()
        return selected[0] if selected else None

    def get_selected_values(self) -> Optional[Tuple[Any, ...]]:
        """Retorna los valores sin la columna de casilla de la primera fila seleccionada."""
        selected_id = self.get_selected_id()
        if selected_id:
            return self._raw_values.get(selected_id)
        return None

    def get_row_values(self, iid: str) -> Optional[Tuple[Any, ...]]:
        """Retorna los valores crudos originales para un identificador específico."""
        return self._raw_values.get(iid)

    def is_row_active(self, iid: str) -> bool:
        """Indica si la fila especificada se encuentra en estado activo."""
        return self._active_status.get(iid, True)

    def are_selected_active(self) -> bool:
        """Determina si la mayoría o el primer elemento seleccionado está activo."""
        selected = self.get_selected_ids()
        if not selected:
            return True
        active_count = sum(1 for sid in selected if self.is_row_active(sid))
        return active_count >= (len(selected) / 2)

    def select_row(self, iid: str):
        """Selecciona y enfoca una fila específica por su iid."""
        if self.tree.exists(iid):
            self.select_single_row(iid)
            self.tree.focus(iid)
            self.tree.see(iid)

    def get_row_count(self) -> int:
        """Retorna el número actual de registros en la tabla."""
        return len(self.tree.get_children())

    # --- Configuración de Callbacks ---

    def set_on_select(self, callback: Optional[Callable[[Optional[str], Optional[Tuple]], None]]):
        self._on_select_callback = callback

    def set_on_selection_change(self, callback: Optional[Callable[[List[str]], None]]):
        self._on_selection_change_callback = callback

    def set_on_double_click(self, callback: Optional[Callable[[str, Tuple], None]]):
        self._on_double_click_callback = callback

    def set_on_delete_key(self, callback: Optional[Callable[[], None]]):
        self._on_delete_key_callback = callback

    def set_on_context_menu(self, callback: Optional[Callable[[Any, List[str]], None]]):
        self._on_context_menu_callback = callback

    # --- Manejadores Internos de Interacción y Eventos ---

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

            cleaned_tags = tuple(t for t in current_tags if t not in ('odd', 'even'))
            hover_tags = cleaned_tags + ('hover',)
            self.tree.item(item, tags=hover_tags)

    def _on_leave(self, event=None):
        """Limpia el efecto hover cuando el puntero sale del área de la tabla."""
        self._clear_hover()

    def _on_tree_click(self, event):
        """Gestiona clics en encabezados, casillas o celdas."""
        region = self.tree.identify_region(event.x, event.y)
        if region == 'heading':
            col = self.tree.identify_column(event.x)
            if col == '#1':
                self._toggle_select_all()
                return "break"
            return

        if region in ('tree', 'cell'):
            row_id = self.tree.identify_row(event.y)
            col = self.tree.identify_column(event.x)
            if not row_id:
                return

            if col == '#1':
                self.toggle_row_selection(row_id)
                return "break"

            # Clic en cualquier otra celda: si se presiona Ctrl, alterna; si no, selecciona exclusivamente
            if event.state & 0x0004:
                self.toggle_row_selection(row_id)
                return "break"
            else:
                self.select_single_row(row_id)

    def _on_right_click(self, event):
        """Abre el menú contextual al hacer clic derecho sobre una fila."""
        row_id = self.tree.identify_row(event.y)
        if row_id:
            if row_id not in self._selected_ids:
                self.select_single_row(row_id)

            if self._on_context_menu_callback:
                self._on_context_menu_callback(event, self.get_selected_ids())

    def _handle_double_click(self, event):
        """Dispara el callback de edición al hacer doble clic en una fila."""
        if self._on_double_click_callback:
            item_id = self.tree.identify_row(event.y)
            if item_id and self.tree.exists(item_id):
                values = self._raw_values.get(item_id, ())
                self._on_double_click_callback(item_id, values)

    def _handle_enter_key(self):
        """Dispara el callback de edición al presionar la tecla Enter."""
        selected = self.get_selected_ids()
        if selected and self._on_double_click_callback:
            first_id = selected[0]
            values = self._raw_values.get(first_id, ())
            self._on_double_click_callback(first_id, values)

    def _handle_delete_key(self):
        """Dispara el callback de eliminación al presionar la tecla Supr (Delete)."""
        if self._on_delete_key_callback and self.get_selected_ids():
            self._on_delete_key_callback()

    def _handle_space_key(self):
        """Alterna la casilla de la fila actualmente enfocada con la barra espaciadora."""
        focused = self.tree.focus()
        if focused and self.tree.exists(focused):
            self.toggle_row_selection(focused)
