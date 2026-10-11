# -*- coding: utf-8 -*-
"""TablaCRUD: Componente reutilizable para tablas de gestión con barra de herramientas,
acciones contextuales, selección múltiple, confirmación modal y filtrado avanzado."""

from typing import List, Tuple, Dict, Any, Optional, Callable, Union, Set
import datetime
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

from gui.styles import (
    COLORS,
    RADIUS,
    SPACING,
    CONTROL_HEIGHT,
    FONT_FAMILY,
    font,
    button,
    entry,
    boton_primario,
    boton_secundario,
    boton_peligro,
    boton_icono,
    entrada_busqueda,
    apply_treeview_tags,
    configurar_treeview,
    get_dpi_scale,
)


class ModalConfirmacionEliminar(ctk.CTkToplevel):
    """Ventana modal personalizada para confirmar la eliminación de registros."""

    def __init__(
        self,
        parent,
        count: int,
        entity_name: str = "registro",
        entity_name_plural: str = "registros",
        on_confirm: Optional[Callable[[], None]] = None,
    ):
        super().__init__(parent)
        self.parent = parent
        self._on_confirm = on_confirm

        self.title("Confirmar eliminación")
        self.geometry("450x230")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['bg'])

        self.transient(parent)
        self.grab_set()

        self._center_window()

        # Tarjeta principal
        self.card = ctk.CTkFrame(
            self,
            fg_color=COLORS['surface'],
            corner_radius=RADIUS['card'],
            border_width=1,
            border_color=COLORS['border'],
        )
        self.card.pack(fill='both', expand=True, padx=SPACING['md'], pady=SPACING['md'])

        # Encabezado con ícono de advertencia
        self.header_frame = ctk.CTkFrame(self.card, fg_color='transparent')
        self.header_frame.pack(fill='x', padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['sm']))

        self.icon_badge = ctk.CTkFrame(
            self.header_frame,
            width=42,
            height=42,
            fg_color=COLORS['danger_soft'],
            corner_radius=RADIUS['control'],
            border_width=1,
            border_color=COLORS['danger_border'],
        )
        self.icon_badge.pack(side='left', padx=(0, SPACING['md']))
        self.icon_badge.pack_propagate(False)

        self.icon_label = ctk.CTkLabel(
            self.icon_badge,
            text="⚠️",
            font=font('heading'),
            text_color=COLORS['danger'],
        )
        self.icon_label.place(relx=0.5, rely=0.5, anchor='center')

        self.texts_frame = ctk.CTkFrame(self.header_frame, fg_color='transparent')
        self.texts_frame.pack(side='left', fill='x', expand=True)

        singular = (count == 1)
        title_text = f"¿Eliminar {entity_name} seleccionado?" if singular else f"¿Eliminar {count} {entity_name_plural} seleccionados?"
        self.lbl_title = ctk.CTkLabel(
            self.texts_frame,
            text=title_text,
            font=font('heading'),
            text_color=COLORS['ink'],
            anchor='w',
        )
        self.lbl_title.pack(fill='x', anchor='w')

        desc_text = (
            f"Se eliminará permanentemente {count} {entity_name if singular else entity_name_plural}. "
            "Esta acción no se puede deshacer."
        )
        self.lbl_desc = ctk.CTkLabel(
            self.texts_frame,
            text=desc_text,
            font=font('small'),
            text_color=COLORS['muted'],
            anchor='w',
            wraplength=300,
            justify='left',
        )
        self.lbl_desc.pack(fill='x', anchor='w', pady=(SPACING['xs'], 0))

        # Botones de acción
        self.actions_frame = ctk.CTkFrame(self.card, fg_color='transparent')
        self.actions_frame.pack(side='bottom', fill='x', padx=SPACING['lg'], pady=(0, SPACING['lg']))

        btn_text = f"Eliminar {entity_name}" if singular else f"Eliminar {count} {entity_name_plural}"
        self.btn_delete = boton_peligro(
            self.actions_frame,
            text=btn_text,
            command=self._confirm,
            height=CONTROL_HEIGHT,
        )
        self.btn_delete.pack(side='right', padx=(SPACING['sm'], 0))

        self.btn_cancel = boton_secundario(
            self.actions_frame,
            text="Cancelar",
            command=self.destroy,
            height=CONTROL_HEIGHT,
        )
        self.btn_cancel.pack(side='right')

        self.bind('<Escape>', lambda e: self.destroy())
        self.bind('<Return>', lambda e: self._confirm())
        self.after(50, self.btn_delete.focus_set)

    def _center_window(self):
        """Centra la ventana modal sobre su padre."""
        self.update_idletasks()
        try:
            pw = self.parent.winfo_width()
            ph = self.parent.winfo_height()
            px = self.parent.winfo_x()
            py = self.parent.winfo_y()
            w, h = 450, 230
            x = px + max(0, (pw - w) // 2)
            y = py + max(0, (ph - h) // 2)
            self.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            self.geometry("450x230")

    def _confirm(self):
        """Ejecuta el callback de confirmación y destruye el diálogo."""
        self.destroy()
        if self._on_confirm:
            self._on_confirm()


class TablaCRUD(ctk.CTkFrame):
    """Componente integral y reutilizable para vistas de gestión CRUD.

    Incluye:
    1. Barra superior: buscador interactivo (Ctrl+F) + contenedor de filtros propios a la izquierda,
       y botones de acción estandarizados (Actualizar icono, acción extra opcional y Crear primario) a la derecha.
    2. Barra contextual sobre la tabla: chip 'N seleccionados', botón 'Deseleccionar',
       acciones 'Editar' (1 sel.), 'Activar / Desactivar' dinámico, separador y 'Eliminar' (rojo suave).
    3. Modal propio de confirmación antes de eliminar.
    4. Treeview con selección múltiple (selectmode='extended'), casillas de selección,
       ordenación por columnas con flechas (▲▼), y badges '● Activo / ● Inactivo'.
    5. Estado vacío dual: distingue entre 'sin datos en el sistema' y 'sin resultados para la búsqueda'.
    6. Contador de pie 'N de M registros'.
    7. Atajos: doble clic o Enter = editar, Supr = eliminar, F5 = actualizar, Ctrl+N = crear, Ctrl+F = buscar.
    """

    ICON_UNCHECKED = "☐"
    ICON_CHECKED = "☑"
    _COL_CHK = "__chk__"

    def __init__(
        self,
        master,
        columns: List[Tuple[str, str, int, str]],
        on_editar: Optional[Callable[[str], None]] = None,
        on_toggle_estado: Optional[Callable[[List[str], bool], None]] = None,
        on_eliminar: Optional[Callable[[List[str]], None]] = None,
        on_crear: Optional[Callable[[], None]] = None,
        on_actualizar: Optional[Callable[[], None]] = None,
        entity_name: str = "registro",
        entity_name_plural: str = "registros",
        create_button_text: str = "Crear registro",
        search_placeholder: str = "Buscar...",
        extra_action_button: Optional[Dict[str, Any]] = None,
        empty_icon: str = "📦",
        empty_title: str = "No hay registros disponibles",
        empty_message: str = "Crea un nuevo registro para comenzar.",
        empty_action_text: Optional[str] = None,
        empty_action_command: Optional[Callable[[], None]] = None,
        **kwargs,
    ):
        base_kwargs = {
            'fg_color': 'transparent',
        }
        merged_kwargs = {**base_kwargs, **kwargs}
        super().__init__(master, **merged_kwargs)

        self._on_editar_cb = on_editar
        self._on_toggle_estado_cb = on_toggle_estado
        self._on_eliminar_cb = on_eliminar
        self._on_crear_cb = on_crear
        self._on_actualizar_cb = on_actualizar

        self.entity_name = entity_name
        self.entity_name_plural = entity_name_plural
        self.create_button_text = create_button_text
        self.search_placeholder = search_placeholder
        self.extra_action_button = extra_action_button

        self._empty_icon = empty_icon
        self._empty_title = empty_title
        self._empty_message = empty_message
        self._empty_action_text = empty_action_text
        self._empty_action_command = empty_action_command

        # Almacenamiento de columnas y ordenación
        self._columns_def = columns  # Lista de (col_id, base_heading, width, anchor)
        self._sort_col: Optional[str] = None
        self._sort_descending: bool = False

        # Datos en memoria
        # Cada elemento: {'id': str, 'values': tuple, 'values_dict': dict, 'is_active': bool, 'raw': Any}
        self._all_rows: List[Dict[str, Any]] = []
        self._filtered_rows: List[Dict[str, Any]] = []
        self._selected_ids: Set[str] = set()

        # Filtro personalizado externo (ej. por tipo o rango de años)
        self._custom_filter_fn: Optional[Callable[[Dict[str, Any]], bool]] = None

        # Seguimiento para efecto hover
        self._last_hovered_item: Optional[str] = None
        self._original_tags: Dict[str, Tuple[str, ...]] = {}

        # Configuración del grid vertical
        # Row 0: Toolbar
        # Row 1: Contextual Bar
        # Row 2: Table Card (expande)
        # Row 3: Footer
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ── 1. Barra de herramientas principal ─────────────────────────
        self._build_toolbar()

        # ── 2. Barra de acciones contextuales ──────────────────────────
        self._build_context_bar()

        # ── 3. Tarjeta contenedor con Treeview y Estado Vacío ──────────
        self._build_table_card()

        # ── 4. Pie de tabla con contador ───────────────────────────────
        self._build_footer()

        # ── 5. Atajos globales de la tabla ─────────────────────────────
        self._bind_events()

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║  CONSTRUCCIÓN DE SECCIONES DE LA INTERFAZ                       ║
    # ╚══════════════════════════════════════════════════════════════════╝

    def _build_toolbar(self):
        """Construye la barra superior con zona izquierda (buscador y filtros)
        y zona derecha (acciones globales ordenadas)."""
        self.toolbar = ctk.CTkFrame(self, fg_color='transparent')
        self.toolbar.grid(row=0, column=0, sticky='ew', pady=(0, SPACING['sm']))

        # Zona Izquierda: Buscador + contenedor de filtros propios de la pestaña
        self.left_tools = ctk.CTkFrame(self.toolbar, fg_color='transparent')
        self.left_tools.pack(side='left', fill='y')

        self.search_entry = entrada_busqueda(
            self.left_tools,
            placeholder=self.search_placeholder,
            width=240,
        )
        self.search_entry.pack(side='left', padx=(0, SPACING['sm']))
        self.search_entry.bind('<KeyRelease>', lambda e: self.apply_filter())

        # Contenedor para filtros adicionales inyectados por cada pestaña
        self.extra_filters_frame = ctk.CTkFrame(self.left_tools, fg_color='transparent')
        self.extra_filters_frame.pack(side='left')

        # Zona Derecha: Acciones globales con orden estricto y unificado
        # [Actualizar icono] -> [Acción extra si existe] -> [Crear primario]
        self.right_tools = ctk.CTkFrame(self.toolbar, fg_color='transparent')
        self.right_tools.pack(side='right', fill='y')

        # Botón primario de creación (al extremo derecho)
        self.btn_create = boton_primario(
            self.right_tools,
            text=self.create_button_text,
            command=self._handle_crear,
            height=CONTROL_HEIGHT,
        )
        self.btn_create.pack(side='right', padx=(SPACING['sm'], 0))

        # Botón de acción adicional (ej. "Descargar del SCIENTI" en Grupos)
        if self.extra_action_button:
            cmd = self.extra_action_button.get('command')
            txt = self.extra_action_button.get('text', 'Acción')
            var = self.extra_action_button.get('variant', 'secondary')
            if var == 'primary':
                self.btn_extra = boton_primario(self.right_tools, text=txt, command=cmd, height=CONTROL_HEIGHT)
            else:
                self.btn_extra = boton_secundario(self.right_tools, text=txt, command=cmd, height=CONTROL_HEIGHT)
            self.btn_extra.pack(side='right', padx=(SPACING['sm'], 0))
        else:
            self.btn_extra = None

        # Botón icono Actualizar (⟳)
        self.btn_refresh = boton_icono(
            self.right_tools,
            text="⟳",
            command=self._handle_actualizar,
        )
        self.btn_refresh.pack(side='right', padx=(0, 0))

    def _build_context_bar(self):
        """Construye la barra contextual interactiva sobre la tabla."""
        self.context_bar = ctk.CTkFrame(
            self,
            height=44,
            fg_color=COLORS['surface'],
            corner_radius=RADIUS['control'],
            border_width=1,
            border_color=COLORS['border'],
        )
        self.context_bar.grid(row=1, column=0, sticky='ew', pady=(0, SPACING['sm']))
        self.context_bar.pack_propagate(False)

        # Lado izquierdo: Chip indicador y botón para limpiar selección
        self.ctx_left = ctk.CTkFrame(self.context_bar, fg_color='transparent')
        self.ctx_left.pack(side='left', padx=SPACING['sm'], pady=4)

        self.chip_badge = ctk.CTkFrame(
            self.ctx_left,
            fg_color=COLORS['surface_subtle'],
            corner_radius=RADIUS['badge'],
        )
        self.chip_badge.pack(side='left', padx=(0, SPACING['xs']))

        self.chip_label = ctk.CTkLabel(
            self.chip_badge,
            text="0 seleccionados",
            font=font('badge'),
            text_color=COLORS['muted_light'],
        )
        self.chip_label.pack(padx=SPACING['sm'], pady=3)

        self.btn_clear_sel = button(
            self.ctx_left,
            text="Deseleccionar",
            variant='tertiary',
            command=self.clear_selection,
            height=28,
        )
        self.btn_clear_sel.pack(side='left')
        self.btn_clear_sel.configure(state='disabled')

        # Lado derecho: Acciones contextuales sobre la selección
        self.ctx_right = ctk.CTkFrame(self.context_bar, fg_color='transparent')
        self.ctx_right.pack(side='right', padx=SPACING['sm'], pady=4)

        # Botón Editar (activo solo con exactamente 1 seleccionado)
        self.btn_edit = boton_secundario(
            self.ctx_right,
            text="Editar",
            command=self._handle_editar,
            height=30,
        )
        self.btn_edit.pack(side='left', padx=(0, SPACING['xs']))
        self.btn_edit.configure(state='disabled')

        # Botón Activar / Desactivar (cambia texto dinámicamente)
        self.btn_toggle = boton_secundario(
            self.ctx_right,
            text="Desactivar",
            command=self._handle_toggle_estado,
            height=30,
        )
        self.btn_toggle.pack(side='left', padx=(0, SPACING['xs']))
        self.btn_toggle.configure(state='disabled')

        # Separador vertical fino
        self.ctx_sep = ctk.CTkFrame(
            self.ctx_right,
            width=1,
            height=20,
            fg_color=COLORS['border'],
            corner_radius=0,
        )
        self.ctx_sep.pack(side='left', padx=SPACING['xs'], pady=5)

        # Botón Eliminar en rojo suave
        self.btn_delete = boton_peligro(
            self.ctx_right,
            text="Eliminar",
            command=self._handle_eliminar_request,
            height=30,
        )
        self.btn_delete.pack(side='left')
        self.btn_delete.configure(state='disabled')

    def _build_table_card(self):
        """Construye la tarjeta contenedora del Treeview, scrollbar y estado vacío."""
        self.table_card = ctk.CTkFrame(
            self,
            corner_radius=RADIUS['card'],
            fg_color=COLORS['surface'],
            border_width=1,
            border_color=COLORS['border'],
        )
        self.table_card.grid(row=2, column=0, sticky='nsew', pady=(0, SPACING['xs']))
        self.table_card.grid_rowconfigure(0, weight=1)
        self.table_card.grid_columnconfigure(0, weight=1)

        # Estilo del Treeview
        configurar_treeview(self)

        # Treeview con selección extendida
        self.tree = ttk.Treeview(
            self.table_card,
            show='headings',
            style='Pea.Treeview',
            selectmode='extended',
        )
        apply_treeview_tags(self.tree)

        # Scrollbar vertical
        self.scrollbar = ttk.Scrollbar(
            self.table_card,
            orient='vertical',
            style='Pea.Vertical.TScrollbar',
            command=self.tree.yview,
        )
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.tree.grid(row=0, column=0, sticky='nsew', padx=(1, 0), pady=1)
        self.scrollbar.grid(row=0, column=1, sticky='ns', padx=(0, 1), pady=1)

        # Configuración de columnas
        self._setup_columns()

        # Contenedor flotante para Estado Vacío
        self.empty_container = ctk.CTkFrame(self.table_card, fg_color=COLORS['surface'])

        self.empty_icon_label = ctk.CTkLabel(
            self.empty_container,
            text=self._empty_icon,
            font=('Segoe UI', 32),
            text_color=COLORS['muted_light'],
        )
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

        self.empty_action_btn = boton_primario(
            self.empty_container,
            text=self._empty_action_text or "Crear registro",
            command=self._handle_empty_action,
        )
        if self._empty_action_text:
            self.empty_action_btn.pack()

    def _build_footer(self):
        """Construye el pie de tabla con el contador 'N de M registros'."""
        self.footer_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.footer_frame.grid(row=3, column=0, sticky='ew', pady=(SPACING['xs'], 0))

        self.count_label = ctk.CTkLabel(
            self.footer_frame,
            text="0 de 0 registros",
            font=font('small'),
            text_color=COLORS['muted'],
            anchor='w',
        )
        self.count_label.pack(side='left')

    def _setup_columns(self):
        """Configura las columnas del Treeview incluyendo la de casillas."""
        col_ids = [self._COL_CHK]
        for col in self._columns_def:
            col_ids.append(str(col[0]))

        self.tree['columns'] = col_ids

        # Columna de casillas con alternancia de selección total al hacer clic en el encabezado
        self.tree.heading(
            self._COL_CHK,
            text=self.ICON_UNCHECKED,
            anchor='center',
            command=self._toggle_select_all,
        )
        self.tree.column(self._COL_CHK, width=46, minwidth=46, stretch=False, anchor='center')

        # Columnas de datos con soporte de ordenación al hacer clic
        for col in self._columns_def:
            cid = str(col[0])
            heading_text = str(col[1]) if len(col) > 1 else cid.capitalize()
            width = int(col[2]) if len(col) > 2 else 120
            anchor = str(col[3]) if len(col) > 3 else 'w'

            self.tree.heading(
                cid,
                text=heading_text,
                anchor=anchor,
                command=lambda c=cid: self._on_heading_click(c),
            )
            self.tree.column(cid, width=width, anchor=anchor, stretch=True)

    def _bind_events(self):
        """Vincula los eventos de interacción y atajos de teclado."""
        # Hover interactivo
        self.tree.bind('<Motion>', self._on_motion)
        self.tree.bind('<Leave>', self._on_leave)

        # Clics y selección
        self.tree.bind('<Button-1>', self._on_tree_click, add='+')
        self.tree.bind('<Button-3>', self._on_right_click, add='+')
        self.tree.bind('<Double-1>', lambda e: self._on_double_click(e))
        self.tree.bind('<Return>', lambda e: self._on_enter_key())
        self.tree.bind('<Delete>', lambda e: self._on_delete_key())
        self.tree.bind('<space>', lambda e: self._on_space_key())
        self.tree.bind('<Control-a>', lambda e: (self.select_all(), "break")[1])
        self.tree.bind('<Control-A>', lambda e: (self.select_all(), "break")[1])

        # Atajos de ventana
        self.bind('<Control-f>', lambda e: self.focus_search())
        self.bind('<Control-F>', lambda e: self.focus_search())
        self.bind('<Control-n>', lambda e: (self._handle_crear(), "break")[1])
        self.bind('<Control-N>', lambda e: (self._handle_crear(), "break")[1])
        self.bind('<F5>', lambda e: (self._handle_actualizar(), "break")[1])

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║  CARGA Y GESTIÓN DE DATOS                                       ║
    # ╚══════════════════════════════════════════════════════════════════╝

    def set_rows(self, rows: List[Dict[str, Any]]):
        """Carga el conjunto completo de datos en memoria y actualiza la vista.

        Cada elemento de `rows` debe ser un diccionario con la estructura:
        {
            'id': str o int único,
            'values': tupla o lista de valores en el orden de las columnas de datos,
            'is_active': bool (opcional, default True),
            'raw': objeto entidad original (opcional),
        }
        """
        self._all_rows = []
        for r in rows:
            row_id = str(r.get('id', ''))
            is_active = bool(r.get('is_active', True))
            raw_vals = list(r.get('values', ()))

            # Formatear la columna de estado si corresponde
            col_ids = [str(c[0]) for c in self._columns_def]
            values_dict = {}
            formatted_vals = []

            for idx, val in enumerate(raw_vals):
                cid = col_ids[idx] if idx < len(col_ids) else f"col_{idx}"
                # Detección de columna de estado
                if cid.lower() in ('active', 'activo', 'estado', 'status'):
                    val_str = "● Activo" if is_active else "● Inactivo"
                else:
                    val_str = str(val) if val is not None else ""
                values_dict[cid] = val_str
                formatted_vals.append(val_str)

            self._all_rows.append({
                'id': row_id,
                'values': tuple(formatted_vals),
                'values_dict': values_dict,
                'is_active': is_active,
                'raw': r.get('raw', None),
            })

        self.apply_filter()

    def set_filter_predicate(self, predicate: Optional[Callable[[Dict[str, Any]], bool]]):
        """Configura una función predicado personalizada para filtros adicionales."""
        self._custom_filter_fn = predicate
        self.apply_filter()

    def apply_filter(self):
        """Aplica conjuntamente el buscador por texto y el predicado personalizado."""
        query = self.search_entry.get().strip().lower()

        filtered = []
        for row in self._all_rows:
            # 1. Filtro personalizado (ej. por tipo o año)
            if self._custom_filter_fn and not self._custom_filter_fn(row):
                continue

            # 2. Filtro de búsqueda textual en todos los campos visibles
            if query:
                match = False
                for val in row['values']:
                    if query in str(val).lower():
                        match = True
                        break
                if not match:
                    continue

            filtered.append(row)

        self._filtered_rows = filtered

        # Aplicar ordenación si hay columna activa
        if self._sort_col:
            self._sort_filtered_rows()

        self._render_treeview()
        self._update_footer_count()
        self._update_empty_state()
        self._refresh_selection_state()

    def _sort_filtered_rows(self):
        """Ordena las filas filtradas según la columna y dirección actual."""
        if not self._sort_col:
            return

        def _sort_key(item):
            val = item['values_dict'].get(self._sort_col, '')
            # Limpiar badge si es estado
            val_clean = str(val).replace('●', '').strip()
            try:
                return (0, float(val_clean))
            except (ValueError, TypeError):
                return (1, val_clean.lower())

        self._filtered_rows.sort(key=_sort_key, reverse=self._sort_descending)

    def _render_treeview(self):
        """Dibuja las filas filtradas en el Treeview con tags zebra y badges."""
        self._clear_hover()
        self._original_tags.clear()

        # Limpiar filas existentes en el árbol
        for child in self.tree.get_children():
            self.tree.delete(child)

        for idx, row in enumerate(self._filtered_rows):
            iid = row['id']
            zebra_tag = 'odd' if idx % 2 == 0 else 'even'
            badge_tag = 'active_badge' if row['is_active'] else 'inactive_badge'
            tags = (zebra_tag, badge_tag)

            chk_icon = self.ICON_CHECKED if iid in self._selected_ids else self.ICON_UNCHECKED
            display_values = (chk_icon,) + row['values']

            self.tree.insert('', 'end', iid=iid, values=display_values, tags=tags)

    def _update_footer_count(self):
        """Actualiza el texto del pie 'N de M registros'."""
        total = len(self._all_rows)
        visible = len(self._filtered_rows)
        singular = (total == 1)
        name = self.entity_name if singular else self.entity_name_plural
        self.count_label.configure(text=f"{visible} de {total} {name}")

    def _update_empty_state(self):
        """Muestra u oculta el contenedor centrado de estado vacío, distinguiendo
        entre 'sin datos en el sistema' y 'sin resultados para la búsqueda'."""
        total = len(self._all_rows)
        visible = len(self._filtered_rows)

        if visible > 0:
            self.empty_container.place_forget()
            return

        if total == 0:
            # Caso 1: Aún no hay datos registrados en el sistema
            self.empty_icon_label.configure(text=self._empty_icon or "📦")
            self.empty_title_label.configure(text=self._empty_title)
            self.empty_message_label.configure(text=self._empty_message)

            if self._empty_action_text and (self._empty_action_command or self._on_crear_cb):
                self.empty_action_btn.configure(text=self._empty_action_text)
                self.empty_action_btn.pack(pady=(0, 0))
            else:
                self.empty_action_btn.pack_forget()
        else:
            # Caso 2: Hay datos pero la búsqueda o filtros no arrojaron resultados
            self.empty_icon_label.configure(text="🔍")
            self.empty_title_label.configure(text="Sin resultados para la búsqueda")
            self.empty_message_label.configure(
                text="No se encontraron registros que coincidan con los criterios de búsqueda o filtros aplicados."
            )
            self.empty_action_btn.configure(text="Limpiar búsqueda y filtros")
            self.empty_action_btn.pack(pady=(0, 0))

        self.empty_container.place(relx=0.5, rely=0.5, anchor='center')

    def _handle_empty_action(self):
        """Ejecuta la acción del estado vacío según el contexto."""
        if len(self._all_rows) == 0:
            if self._empty_action_command:
                self._empty_action_command()
            elif self._on_crear_cb:
                self._on_crear_cb()
        else:
            self.clear_search_and_filters()

    def clear_search_and_filters(self):
        """Restablece el campo de búsqueda y vuelve a aplicar los filtros."""
        self.search_entry.delete(0, 'end')
        self.apply_filter()

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║  ORDENACIÓN POR COLUMNAS CON FLECHAS (▲▼)                       ║
    # ╚══════════════════════════════════════════════════════════════════╝

    def _on_heading_click(self, col_id: str):
        """Alterna la ordenación ascendente/descendente de la columna seleccionada."""
        if self._sort_col == col_id:
            self._sort_descending = not self._sort_descending
        else:
            self._sort_col = col_id
            self._sort_descending = False

        self._refresh_headings()
        self.apply_filter()

    def _refresh_headings(self):
        """Actualiza los textos de los encabezados agregando o quitando las flechas ▲▼."""
        for col in self._columns_def:
            cid = str(col[0])
            base_text = str(col[1]) if len(col) > 1 else cid.capitalize()

            if cid == self._sort_col:
                arrow = " ▼" if self._sort_descending else " ▲"
                heading_text = f"{base_text}{arrow}"
            else:
                heading_text = base_text

            self.tree.heading(cid, text=heading_text)

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║  GESTIÓN DE SELECCIÓN Y CASILLAS                               ║
    # ╚══════════════════════════════════════════════════════════════════╝

    def _toggle_select_all(self):
        """Alterna entre seleccionar todas las filas visibles o deseleccionarlas."""
        all_children = [r['id'] for r in self._filtered_rows if self.tree.exists(r['id'])]
        if not all_children:
            return

        if len(self._selected_ids) == len(all_children):
            self.clear_selection()
        else:
            self.select_all()

    def select_all(self):
        """Marca y selecciona todas las filas visibles."""
        all_children = [r['id'] for r in self._filtered_rows if self.tree.exists(r['id'])]
        self._selected_ids = set(all_children)
        self.tree.heading(self._COL_CHK, text=self.ICON_CHECKED)

        for iid in all_children:
            vals = list(self.tree.item(iid, 'values'))
            if vals:
                vals[0] = self.ICON_CHECKED
                self.tree.item(iid, values=vals)

        self.tree.selection_set(all_children)
        self._refresh_selection_state()

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
        self._refresh_selection_state()

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
        self._refresh_selection_state()

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
        self._refresh_selection_state()

    def _refresh_header_checkbox(self):
        """Actualiza la casilla del encabezado según la cantidad de filas seleccionadas."""
        visible = len(self._filtered_rows)
        if visible > 0 and len(self._selected_ids) == visible:
            self.tree.heading(self._COL_CHK, text=self.ICON_CHECKED)
        else:
            self.tree.heading(self._COL_CHK, text=self.ICON_UNCHECKED)

    def _refresh_selection_state(self):
        """Actualiza los botones de la barra contextual según la selección activa."""
        valid_selected = [sid for sid in self._selected_ids if self.tree.exists(sid)]
        self._selected_ids = set(valid_selected)
        count = len(valid_selected)

        if count == 0:
            self.chip_label.configure(text="0 seleccionados", text_color=COLORS['muted_light'])
            self.chip_badge.configure(fg_color=COLORS['surface_subtle'])
            self.btn_clear_sel.configure(state='disabled')
            self.btn_edit.configure(state='disabled')
            self.btn_toggle.configure(state='disabled', text="Desactivar")
            self.btn_delete.configure(state='disabled')
        else:
            suffix = "seleccionado" if count == 1 else "seleccionados"
            self.chip_label.configure(text=f"{count} {suffix}", text_color=COLORS['accent'])
            self.chip_badge.configure(fg_color=COLORS['accent_soft'])
            self.btn_clear_sel.configure(state='normal')

            # Editar solo activo con exactamente 1 registro
            self.btn_edit.configure(state='normal' if count == 1 else 'disabled')

            # Botón Activar / Desactivar con texto dinámico
            are_active = self.are_selected_active()
            toggle_text = "Desactivar" if are_active else "Activar"
            self.btn_toggle.configure(state='normal', text=toggle_text)

            # Botón Eliminar activo
            self.btn_delete.configure(state='normal')

    def are_selected_active(self) -> bool:
        """Determina si la mayoría de los registros seleccionados están en estado activo."""
        selected_rows = [r for r in self._all_rows if r['id'] in self._selected_ids]
        if not selected_rows:
            return True
        active_count = sum(1 for r in selected_rows if r['is_active'])
        return active_count >= (len(selected_rows) / 2)

    def get_selected_ids(self) -> List[str]:
        """Retorna la lista de identificadores seleccionados válidos."""
        return [sid for sid in self._selected_ids if self.tree.exists(sid)]

    def get_selected_id(self) -> Optional[str]:
        """Retorna el primer identificador seleccionado, o None."""
        selected = self.get_selected_ids()
        return selected[0] if selected else None

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║  MANEJADORES DE ACCIONES Y CALLBACKS                            ║
    # ╚══════════════════════════════════════════════════════════════════╝

    def _handle_crear(self):
        """Dispara el callback de creación."""
        if self._on_crear_cb:
            self._on_crear_cb()

    def _handle_actualizar(self):
        """Dispara el callback de actualización."""
        if self._on_actualizar_cb:
            self._on_actualizar_cb()

    def _handle_editar(self):
        """Dispara el callback de edición para el registro seleccionado."""
        sid = self.get_selected_id()
        if sid and self._on_editar_cb:
            self._on_editar_cb(sid)

    def _handle_toggle_estado(self):
        """Dispara el callback para alternar el estado (activar/desactivar)."""
        ids = self.get_selected_ids()
        if not ids or not self._on_toggle_estado_cb:
            return
        should_activate = not self.are_selected_active()
        self._on_toggle_estado_cb(ids, should_activate)

    def _handle_eliminar_request(self):
        """Abre el modal propio de confirmación de eliminación."""
        ids = self.get_selected_ids()
        if not ids or not self._on_eliminar_cb:
            return

        modal = ModalConfirmacionEliminar(
            parent=self.winfo_toplevel(),
            count=len(ids),
            entity_name=self.entity_name,
            entity_name_plural=self.entity_name_plural,
            on_confirm=lambda: self._on_eliminar_cb(ids),
        )

    def focus_search(self):
        """Enfoca el campo de búsqueda y selecciona su contenido."""
        self.search_entry.focus_set()
        self.search_entry.select_range(0, 'end')
        return "break"

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║  INTERACCIÓN CON TREEVIEW (MOUSE Y TECLADO)                     ║
    # ╚══════════════════════════════════════════════════════════════════╝

    def _clear_hover(self):
        """Restaura las etiquetas originales de la fila en hover."""
        if self._last_hovered_item:
            if self.tree.exists(self._last_hovered_item):
                orig_tags = self._original_tags.pop(self._last_hovered_item, ('odd',))
                self.tree.item(self._last_hovered_item, tags=orig_tags)
            else:
                self._original_tags.pop(self._last_hovered_item, None)
            self._last_hovered_item = None

    def _on_motion(self, event):
        """Aplica el efecto hover sobre las filas del Treeview."""
        item = self.tree.identify_row(event.y)
        if item == self._last_hovered_item:
            return

        self._clear_hover()

        if item and self.tree.exists(item):
            self._last_hovered_item = item
            current_tags = tuple(self.tree.item(item, 'tags'))
            self._original_tags[item] = current_tags

            cleaned = tuple(t for t in current_tags if t not in ('odd', 'even'))
            hover_tags = cleaned + ('hover',)
            self.tree.item(item, tags=hover_tags)

    def _on_leave(self, event=None):
        """Limpia el efecto hover cuando el puntero sale de la tabla."""
        self._clear_hover()

    def _on_tree_click(self, event):
        """Gestiona clics en encabezados, casillas o celdas de datos."""
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

            # Clic con Ctrl: alternar selección; clic simple: selección única
            if event.state & 0x0004:
                self.toggle_row_selection(row_id)
                return "break"
            else:
                self.select_single_row(row_id)

    def _on_right_click(self, event):
        """Despliega el menú contextual con clic derecho sobre una fila."""
        row_id = self.tree.identify_row(event.y)
        if row_id:
            if row_id not in self._selected_ids:
                self.select_single_row(row_id)

            selected_ids = self.get_selected_ids()
            if not selected_ids:
                return

            is_active = self.are_selected_active()
            toggle_text = "Desactivar" if is_active else "Activar"

            menu = tk.Menu(
                self,
                tearoff=0,
                bg=COLORS['surface'],
                fg=COLORS['ink'],
                activebackground=COLORS['surface_alt'],
                activeforeground=COLORS['accent'],
                font=font('body'),
            )
            if len(selected_ids) == 1:
                menu.add_command(label="Editar", command=self._handle_editar)
            menu.add_command(label=toggle_text, command=self._handle_toggle_estado)
            menu.add_separator()
            menu.add_command(label="Eliminar", command=self._handle_eliminar_request)

            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

    def _on_double_click(self, event):
        """Dispara edición al hacer doble clic sobre una fila."""
        item_id = self.tree.identify_row(event.y)
        if item_id and self.tree.exists(item_id):
            self.select_single_row(item_id)
            self._handle_editar()

    def _on_enter_key(self):
        """Dispara edición al presionar Enter sobre la selección."""
        if len(self.get_selected_ids()) == 1:
            self._handle_editar()

    def _on_delete_key(self):
        """Dispara eliminación al presionar Supr sobre la selección."""
        if len(self.get_selected_ids()) >= 1:
            self._handle_eliminar_request()

    def _on_space_key(self):
        """Alterna la casilla de la fila enfocada con la barra espaciadora."""
        focused = self.tree.focus()
        if focused and self.tree.exists(focused):
            self.toggle_row_selection(focused)
