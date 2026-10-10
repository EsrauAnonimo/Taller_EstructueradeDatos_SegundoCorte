# -*- coding: utf-8 -*-
"""Pestaña de gestión de Productos de Investigación."""

import datetime
from typing import Optional, List
from tkinter import messagebox
import customtkinter as ctk

from gui.styles import (
    COLORS,
    RADIUS,
    SPACING,
    font,
    button,
    entry,
)
from gui.widgets.data_table import DataTable
from gui.forms.producto_form import ProductoForm
from entidades.producto import Producto


class ProductosTab(ctk.CTkFrame):
    """Pestaña para listar, buscar, filtrar por año, crear, editar y eliminar productos."""

    def __init__(self, master, app=None):
        super().__init__(master, fg_color='transparent')
        self._app_ref = app
        self.pack(fill='both', expand=True)

        self._all_productos: List = []
        self._selected_id: Optional[int] = None

        # Configuración del layout vertical
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- 1. Encabezado ---
        self.header_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.header_frame.grid(
            row=0,
            column=0,
            sticky='ew',
            padx=SPACING['lg'],
            pady=(SPACING['lg'], SPACING['md']),
        )

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Productos académicos",
            font=font('display'),
            text_color=COLORS['ink'],
            anchor='w',
        )
        self.title_label.pack(fill='x', anchor='w')

        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Catálogo y producción científica de los grupos de investigación",
            font=font('body'),
            text_color=COLORS['muted'],
            anchor='w',
        )
        self.subtitle_label.pack(fill='x', anchor='w', pady=(SPACING['xs'], 0))

        # --- 2. Barra de herramientas integrada ---
        self.toolbar = ctk.CTkFrame(self, fg_color='transparent')
        self.toolbar.grid(
            row=1,
            column=0,
            sticky='ew',
            padx=SPACING['lg'],
            pady=(0, SPACING['md']),
        )

        # Filtros y búsqueda agrupados a la izquierda
        self.left_tools = ctk.CTkFrame(self.toolbar, fg_color='transparent')
        self.left_tools.pack(side='left', fill='y')

        self.search_entry = entry(
            self.left_tools,
            placeholder_text="Buscar producto...",
            width=220,
        )
        self.search_entry.pack(side='left', padx=(0, SPACING['sm']))
        self.search_entry.bind('<KeyRelease>', lambda e: self._apply_filters())

        # Selector de filtro por año
        self.filter_var = ctk.StringVar(value="Todos")
        self.filter_menu = ctk.CTkOptionMenu(
            self.left_tools,
            values=["Todos", "Últimos 2 años", "Últimos 5 años", "Personalizado"],
            variable=self.filter_var,
            command=self._on_filter_option_changed,
            font=font('body'),
            dropdown_font=font('body'),
            corner_radius=RADIUS['control'],
            fg_color=COLORS['surface'],
            button_color=COLORS['border'],
            button_hover_color=COLORS['muted'],
            text_color=COLORS['ink'],
            dropdown_fg_color=COLORS['surface'],
            dropdown_text_color=COLORS['ink'],
            width=140,
            height=36,
        )
        self.filter_menu.pack(side='left', padx=(0, SPACING['sm']))

        # Entradas numéricas para rango personalizado
        self.from_entry = entry(self.left_tools, placeholder_text="Desde", width=65)
        self.to_entry = entry(self.left_tools, placeholder_text="Hasta", width=65)
        self.btn_apply_range = button(
            self.left_tools,
            text="Filtrar",
            variant='secondary',
            command=self._apply_filters,
        )

        # Acciones principales a la derecha
        self.btn_create = button(
            self.toolbar,
            text="Crear producto",
            variant='primary',
            command=self.create,
        )
        self.btn_create.pack(side='right', padx=(SPACING['sm'], 0))

        self.btn_refresh = button(
            self.toolbar,
            text="Actualizar",
            variant='ghost',
            command=self.refresh,
        )
        self.btn_refresh.pack(side='right', padx=(SPACING['sm'], 0))

        self.btn_delete = button(
            self.toolbar,
            text="Eliminar",
            variant='danger',
            command=self.delete,
            state='disabled',
        )
        self.btn_delete.pack(side='right', padx=(SPACING['sm'], 0))

        self.btn_activate = button(
            self.toolbar,
            text="Activar",
            variant='secondary',
            command=self.activate,
            state='disabled',
        )
        self.btn_activate.pack(side='right', padx=(SPACING['sm'], 0))

        self.btn_deactivate = button(
            self.toolbar,
            text="Desactivar",
            variant='secondary',
            command=self.deactivate,
            state='disabled',
        )
        self.btn_deactivate.pack(side='right', padx=(SPACING['sm'], 0))

        self.btn_edit = button(
            self.toolbar,
            text="Editar",
            variant='secondary',
            command=self.edit,
            state='disabled',
        )
        self.btn_edit.pack(side='right', padx=(SPACING['sm'], 0))

        # --- 3. Tabla dentro de tarjeta ---
        columns = [
            ('id', 'ID', 60, 'center'),
            ('title', 'Título de la producción', 320, 'w'),
            ('type', 'Tipo', 120, 'center'),
            ('year', 'Año', 80, 'center'),
            ('group', 'Grupo ID', 80, 'center'),
            ('active', 'Estado', 100, 'center'),
        ]
        self.table = DataTable(
            self,
            columns=columns,
            on_select=self._on_row_select,
            on_double_click=self._on_row_double_click,
            empty_text="No hay productos para mostrar",
        )
        self.table.grid(
            row=2,
            column=0,
            sticky='nsew',
            padx=SPACING['lg'],
            pady=(0, SPACING['sm']),
        )

        # --- 4. Pie con contador de registros ---
        self.footer_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.footer_frame.grid(
            row=3,
            column=0,
            sticky='ew',
            padx=SPACING['lg'],
            pady=(0, SPACING['md']),
        )

        self.count_label = ctk.CTkLabel(
            self.footer_frame,
            text="0 productos",
            font=font('small'),
            text_color=COLORS['muted'],
            anchor='w',
        )
        self.count_label.pack(side='left')

        self.load_data()

    def get_app(self):
        """Resuelve dinámicamente la instancia principal de App en la jerarquía."""
        if self._app_ref is not None:
            return self._app_ref
        curr = self
        while curr is not None:
            if hasattr(curr, 'prod_crud'):
                self._app_ref = curr
                return curr
            curr = getattr(curr, 'master', None)
        return None

    def _get_all_raw_productos(self) -> List:
        """Obtiene todos los productos (activos e inactivos) de la multilista."""
        app = self.get_app()
        if app is None or not hasattr(app, 'multilista'):
            return []
        products = []
        try:
            curr_group = app.multilista.head_group
            while curr_group is not None:
                curr_inv = curr_group.sublist
                while curr_inv is not None:
                    curr_prod = curr_inv.sublist
                    while curr_prod is not None:
                        products.append(curr_prod.data)
                        curr_prod = curr_prod.next
                    curr_inv = curr_inv.next
                curr_group = curr_group.next
        except Exception:
            try:
                products = list(app.prod_crud.list_all())
            except Exception:
                products = []
        return products

    def load_data(self):
        """Recarga los datos de los productos desde la capa de persistencia."""
        self._all_productos = self._get_all_raw_productos()
        self._apply_filters()
        self._update_selection_buttons(None)

    def _on_filter_option_changed(self, choice: str):
        """Gestiona la visibilidad de los campos de rango personalizado."""
        if choice == "Personalizado":
            self.from_entry.pack(side='left', padx=(0, SPACING['xs']))
            self.to_entry.pack(side='left', padx=(0, SPACING['xs']))
            self.btn_apply_range.pack(side='left', padx=(0, SPACING['sm']))
        else:
            self.from_entry.pack_forget()
            self.to_entry.pack_forget()
            self.btn_apply_range.pack_forget()
            self._apply_filters()

    def _apply_filters(self):
        """Aplica conjuntamente los filtros de año y texto de búsqueda."""
        query = self.search_entry.get().strip().lower()
        filter_type = self.filter_var.get()
        current_year = datetime.datetime.now().year

        filtered = []
        for p in self._all_productos:
            title = str(getattr(p, 'titulo', '') or getattr(p, 'title', '')).lower()
            ptype = str(getattr(p, 'tipo', '') or getattr(p, 'type', '')).lower()
            try:
                pyear = int(getattr(p, 'anio', 0) or getattr(p, 'year', 0))
            except Exception:
                pyear = 0

            # 1. Filtro por año
            year_match = True
            if filter_type == "Últimos 2 años":
                year_match = pyear >= (current_year - 2)
            elif filter_type == "Últimos 5 años":
                year_match = pyear >= (current_year - 5)
            elif filter_type == "Personalizado":
                try:
                    f_from = int(self.from_entry.get().strip()) if self.from_entry.get().strip() else None
                except ValueError:
                    f_from = None
                try:
                    f_to = int(self.to_entry.get().strip()) if self.to_entry.get().strip() else None
                except ValueError:
                    f_to = None

                if f_from is not None and pyear < f_from:
                    year_match = False
                if f_to is not None and pyear > f_to:
                    year_match = False

            if not year_match:
                continue

            # 2. Filtro por texto de búsqueda
            if query:
                if query not in title and query not in ptype and query not in str(pyear):
                    continue

            filtered.append(p)

        self._render_rows(filtered)

    def _render_rows(self, productos: List):
        """Inserta los registros filtrados en el DataTable."""
        self.table.clear()
        for p in productos:
            pid = getattr(p, 'id', None)
            title = getattr(p, 'titulo', '') or getattr(p, 'title', '')
            ptype = getattr(p, 'tipo', '') or getattr(p, 'type', '')
            year = getattr(p, 'anio', 0) or getattr(p, 'year', 0)
            group_id = getattr(p, 'grupo_id', getattr(p, 'group', ''))
            active = getattr(p, 'validado', getattr(p, 'active', True))
            status_text = "Activo" if active else "Inactivo"

            values = (
                str(pid) if pid is not None else '',
                str(title),
                str(ptype),
                str(year) if year else '',
                str(group_id) if group_id is not None else '',
                status_text,
            )
            self.table.insert_row(values, iid=str(pid), is_active=bool(active))

        total = len(productos)
        suffix = "producto" if total == 1 else "productos"
        self.count_label.configure(text=f"{total} {suffix}")

    def _on_row_select(self, item_id: Optional[str], values):
        """Callback al seleccionar o deseleccionar una fila."""
        if item_id:
            try:
                self._selected_id = int(item_id)
            except ValueError:
                self._selected_id = item_id
        else:
            self._selected_id = None
        self._update_selection_buttons(self._selected_id)

    def _on_row_double_click(self, item_id: str, values):
        """Abre la ventana de edición al hacer doble clic."""
        if item_id:
            try:
                self._selected_id = int(item_id)
            except ValueError:
                self._selected_id = item_id
            self.edit()

    def _update_selection_buttons(self, selected_id):
        """Habilita o deshabilita botones según la selección activa."""
        state = 'normal' if selected_id is not None else 'disabled'
        self.btn_edit.configure(state=state)
        self.btn_deactivate.configure(state=state)
        self.btn_activate.configure(state=state)
        self.btn_delete.configure(state=state)

    def create(self):
        """Abre el formulario modal para registrar un nuevo producto."""
        form = ProductoForm(self)
        self.wait_window(form)
        if form.result:
            app = self.get_app()
            if app:
                data = form.result
                all_raw = self._get_all_raw_productos()
                max_id = max([getattr(p, 'id', 0) for p in all_raw if isinstance(getattr(p, 'id', None), int)] + [0])
                new_id = max_id + 1

                try:
                    anio = int(data.get('year') or data.get('anio') or 0)
                except ValueError:
                    anio = 0

                grupo_val = data.get('group') or data.get('grupo_id')
                try:
                    grupo_id = int(grupo_val) if grupo_val is not None and str(grupo_val).strip() else None
                except ValueError:
                    grupo_id = None

                producto = Producto(
                    id=new_id,
                    titulo=data.get('title') or data.get('titulo', ''),
                    tipo=data.get('type') or data.get('tipo', ''),
                    categoria='',
                    validado=data.get('active', True),
                    anio=anio,
                    investigador_id=None,
                    grupo_id=grupo_id,
                )
                success = app.prod_crud.create(producto)
                if success:
                    app.save_data()
                    self.load_data()
                else:
                    messagebox.showerror("Error", "No se pudo registrar el producto.")

    def edit(self):
        """Abre el formulario modal para editar el producto seleccionado."""
        if self._selected_id is None:
            return
        app = self.get_app()
        if not app:
            return

        prod = app.prod_crud.get_by_id(self._selected_id)
        if not prod:
            for p in self._all_productos:
                if getattr(p, 'id', None) == self._selected_id:
                    prod = p
                    break
        if not prod:
            messagebox.showwarning("Aviso", "No se encontró el producto seleccionado.")
            return

        form_data = {
            'title': getattr(prod, 'titulo', '') or getattr(prod, 'title', ''),
            'type': getattr(prod, 'tipo', '') or getattr(prod, 'type', ''),
            'year': str(getattr(prod, 'anio', 0) or getattr(prod, 'year', '')),
            'group': str(getattr(prod, 'grupo_id', '') or getattr(prod, 'group', '')),
            'active': getattr(prod, 'validado', getattr(prod, 'active', True)),
        }
        form = ProductoForm(self, data=form_data)
        self.wait_window(form)
        if form.result:
            data = form.result
            try:
                anio = int(data.get('year') or data.get('anio') or 0)
            except ValueError:
                anio = 0

            grupo_val = data.get('group') or data.get('grupo_id')
            try:
                grupo_id = int(grupo_val) if grupo_val is not None and str(grupo_val).strip() else None
            except ValueError:
                grupo_id = None

            update_fields = {
                'titulo': data.get('title') or data.get('titulo', ''),
                'tipo': data.get('type') or data.get('tipo', ''),
                'anio': anio,
                'grupo_id': grupo_id,
                'validado': data.get('active', True),
            }
            app.prod_crud.update(self._selected_id, **update_fields)
            app.save_data()
            self.load_data()

    def deactivate(self):
        """Desactiva el producto seleccionado."""
        if self._selected_id is None:
            return
        app = self.get_app()
        if app:
            app.prod_crud.deactivate(self._selected_id)
            app.save_data()
            self.load_data()

    def activate(self):
        """Activa el producto seleccionado."""
        if self._selected_id is None:
            return
        app = self.get_app()
        if app:
            app.prod_crud.activate(self._selected_id)
            app.save_data()
            self.load_data()

    def delete(self):
        """Elimina físicamente el producto seleccionado tras confirmación."""
        if self._selected_id is None:
            return
        confirm = messagebox.askyesno(
            "Confirmar eliminación",
            "¿Está seguro de que desea eliminar permanentemente este producto?",
        )
        if confirm:
            app = self.get_app()
            if app:
                app.prod_crud.delete(self._selected_id)
                app.save_data()
                self.load_data()

    def refresh(self):
        """Actualiza los datos de la tabla."""
        self.load_data()
