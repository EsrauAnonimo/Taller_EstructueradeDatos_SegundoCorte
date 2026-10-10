# -*- coding: utf-8 -*-
"""Pestaña de gestión de Productos de Investigación."""

import datetime
from typing import Optional, List
from tkinter import messagebox
import customtkinter as ctk

from gui.styles import (
    COLORS,
    SPACING,
    font,
    button,
    entry,
    option_menu,
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
            placeholder_text="Buscar producto o tipo...",
            width=220,
        )
        self.search_entry.pack(side='left', padx=(0, SPACING['sm']))
        self.search_entry.bind('<KeyRelease>', lambda e: self._apply_filters())

        # Selector de filtro por año con chevron y dimensiones consistentes
        self.filter_var = ctk.StringVar(value="Todos")
        self.filter_menu = option_menu(
            self.left_tools,
            values=["Todos", "Últimos 2 años", "Últimos 5 años", "Personalizado"],
            variable=self.filter_var,
            command=self._on_filter_option_changed,
            width=150,
        )
        self.filter_menu.pack(side='left', padx=(0, SPACING['sm']))

        # Entradas numéricas para rango personalizado con ancho adecuado y placeholder claro
        self.from_entry = entry(self.left_tools, placeholder_text="Año desde", width=95)
        self.to_entry = entry(self.left_tools, placeholder_text="Año hasta", width=95)
        self.btn_apply_range = button(
            self.left_tools,
            text="Aplicar",
            variant='secondary',
            command=self._apply_filters,
        )

        # Acciones principales a la derecha ordenadas por jerarquía
        # Primario
        self.btn_create = button(
            self.toolbar,
            text="Crear producto",
            variant='primary',
            command=self.create,
        )
        self.btn_create.pack(side='right', padx=(SPACING['sm'], 0))

        # Terciario (Actualizar con texto limpio)
        self.btn_refresh = button(
            self.toolbar,
            text="Actualizar",
            variant='tertiary',
            command=self.refresh,
        )
        self.btn_refresh.pack(side='right', padx=(SPACING['sm'], 0))

        # Destructivo (Rojo suave)
        self.btn_delete = button(
            self.toolbar,
            text="Eliminar",
            variant='danger',
            command=self.delete,
            state='disabled',
        )
        self.btn_delete.pack(side='right', padx=(SPACING['sm'], 0))

        # Secundarios con borde
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

        # --- 3. Tabla dentro de tarjeta con estado vacío sugerido ---
        columns = [
            ('id', 'ID', 60, 'center'),
            ('title', 'Título de la producción', 320, 'w'),
            ('type', 'Tipo de producto', 130, 'center'),
            ('year', 'Año', 80, 'center'),
            ('group', 'Grupo ID', 80, 'center'),
            ('active', 'Estado', 110, 'center'),
        ]
        self.table = DataTable(
            self,
            columns=columns,
            on_select=self._on_row_select,
            on_double_click=self._on_row_double_click,
            empty_icon="",
            empty_title="No se encontraron productos académicos",
            empty_message="Aplica otros filtros de búsqueda o importa producción científica desde MinCiencias.",
            empty_action_text="Restablecer filtros",
            empty_action_command=self._reset_filters,
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

    def _reset_filters(self):
        """Restablece los filtros de búsqueda y selector de año a su valor por defecto."""
        self.search_entry.delete(0, 'end')
        self.filter_var.set("Todos")
        self._on_filter_option_changed("Todos")
        self._apply_filters()

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
        """Gestiona la visibilidad de los campos de rango personalizado de año."""
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
        """Inserta los registros filtrados en el DataTable con badges de color."""
        self.table.clear()
        for p in productos:
            pid = getattr(p, 'id', None)
            title = getattr(p, 'titulo', '') or getattr(p, 'title', '')
            ptype = getattr(p, 'tipo', '') or getattr(p, 'type', '')
            year = getattr(p, 'anio', '') or getattr(p, 'year', '')
            gid = getattr(p, 'grupo_id', getattr(p, 'group', ''))
            active = getattr(p, 'validado', getattr(p, 'active', True))
            status_text = "Activo" if active else "Inactivo"

            values = (
                str(pid) if pid is not None else '',
                str(title),
                str(ptype),
                str(year),
                str(gid) if gid is not None else '',
                status_text,
            )
            self.table.insert_row(values, iid=str(pid), is_active=bool(active))

        total = len(productos)
        suffix = "producto" if total == 1 else "productos"
        self.count_label.configure(text=f"{total} {suffix}")

    def _on_row_select(self, item_id: Optional[str], values: Optional[tuple]):
        """Actualiza el estado de los botones cuando se selecciona o deselecciona una fila."""
        self._update_selection_buttons(item_id)

    def _on_row_double_click(self, item_id: str, values: tuple):
        """Abre directamente la edición al hacer doble clic en una fila."""
        self._update_selection_buttons(item_id)
        self.edit()

    def _update_selection_buttons(self, item_id: Optional[str]):
        """Habilita o deshabilita los botones según la selección actual."""
        if item_id:
            try:
                self._selected_id = int(item_id)
            except ValueError:
                self._selected_id = None
            state = 'normal'
        else:
            self._selected_id = None
            state = 'disabled'

        self.btn_edit.configure(state=state)
        self.btn_delete.configure(state=state)
        self.btn_activate.configure(state=state)
        self.btn_deactivate.configure(state=state)

    def create(self):
        """Abre el formulario modal para registrar un nuevo producto."""
        app = self.get_app()
        form = ProductoForm(self, app=app, on_save=self._on_save_create)
        form.grab_set()

    def _on_save_create(self, data: dict):
        """Persiste el nuevo producto mediante el CRUD."""
        app = self.get_app()
        if not app:
            return
        try:
            nuevo = Producto(
                titulo=data.get('titulo') or data.get('title', ''),
                tipo=data.get('tipo') or data.get('type', ''),
                categoria=data.get('categoria', ''),
                validado=data.get('validado', data.get('active', True)),
                anio=int(data.get('anio') or data.get('year') or 0),
                investigador_id=data.get('investigador_id'),
                grupo_id=data.get('grupo_id') or data.get('group'),
            )
            app.prod_crud.create(nuevo)
            app.save_data()
            self.load_data()
            if hasattr(app, 'load_tabs_data'):
                app.load_tabs_data()
            messagebox.showinfo("Éxito", "Producto registrado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el producto: {e}")

    def edit(self):
        """Abre el formulario para editar el producto seleccionado."""
        if self._selected_id is None:
            return
        app = self.get_app()
        if not app:
            return

        prod = app.prod_crud.read(self._selected_id)
        if not prod:
            for item in self._all_productos:
                if getattr(item, 'id', None) == self._selected_id:
                    prod = item
                    break

        if not prod:
            messagebox.showerror("Error", "No se encontró el producto seleccionado.")
            return

        form = ProductoForm(self, app=app, producto=prod, on_save=self._on_save_edit)
        form.grab_set()

    def _on_save_edit(self, data: dict):
        """Aplica y guarda los cambios del producto en edición."""
        app = self.get_app()
        if not app or self._selected_id is None:
            return
        try:
            app.prod_crud.update(self._selected_id, **data)
            app.save_data()
            self.load_data()
            if hasattr(app, 'load_tabs_data'):
                app.load_tabs_data()
            messagebox.showinfo("Éxito", "Producto actualizado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el producto: {e}")

    def delete(self):
        """Elimina físicamente el producto seleccionado tras confirmación."""
        if self._selected_id is None:
            return
        app = self.get_app()
        if not app:
            return

        confirma = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro de eliminar el producto con ID {self._selected_id}?\n\nEsta acción no se puede deshacer.",
        )
        if not confirma:
            return

        try:
            res = app.prod_crud.delete(self._selected_id)
            if res:
                app.save_data()
                self.load_data()
                if hasattr(app, 'load_tabs_data'):
                    app.load_tabs_data()
                messagebox.showinfo("Éxito", "Producto eliminado correctamente.")
            else:
                messagebox.showerror("Error", "No se pudo eliminar el producto.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar: {e}")

    def activate(self):
        """Marca como activo/validado el producto seleccionado."""
        self._set_active_status(True)

    def deactivate(self):
        """Marca como inactivo el producto seleccionado."""
        self._set_active_status(False)

    def _set_active_status(self, is_active: bool):
        """Actualiza el estado de activación en la capa de datos."""
        if self._selected_id is None:
            return
        app = self.get_app()
        if not app:
            return
        try:
            if is_active:
                app.prod_crud.activate(self._selected_id)
            else:
                app.prod_crud.deactivate(self._selected_id)
            app.save_data()
            self.load_data()
            if hasattr(app, 'load_tabs_data'):
                app.load_tabs_data()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cambiar estado: {e}")

    def refresh(self):
        """Actualiza manualmente la información del listado."""
        self.load_data()
