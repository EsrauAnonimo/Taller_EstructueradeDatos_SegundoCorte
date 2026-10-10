# -*- coding: utf-8 -*-
"""Pestaña de gestión de Productos Académicos."""

from typing import Optional, List
import datetime
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from gui.styles import (
    COLORS,
    SPACING,
    CONTROL_HEIGHT,
    font,
    button,
    entry,
    option_menu,
)
from gui.widgets.data_table import DataTable
from gui.widgets.selection_bar import SelectionActionBar
from gui.forms.producto_form import ProductoForm
from entidades.producto import Producto


class ProductosTab(ctk.CTkFrame):
    """Pestaña para listar, buscar, filtrar por tipo/año, crear, editar y eliminar productos académicos."""

    def __init__(self, master, app=None):
        super().__init__(master, fg_color='transparent')
        self._app_ref = app
        self.pack(fill='both', expand=True)

        self._all_productos: List = []
        self._selected_ids: List[int] = []

        # Configuración del layout vertical
        self.grid_rowconfigure(3, weight=1)
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
            text="Producción científica: artículos, ponencias, libros y software registrados",
            font=font('body'),
            text_color=COLORS['muted'],
            anchor='w',
        )
        self.subtitle_label.pack(fill='x', anchor='w', pady=(SPACING['xs'], 0))

        # --- 2. Barra de herramientas principal (Dos Zonas) ---
        self.toolbar = ctk.CTkFrame(self, fg_color='transparent')
        self.toolbar.grid(
            row=1,
            column=0,
            sticky='ew',
            padx=SPACING['lg'],
            pady=(0, SPACING['sm']),
        )

        # Zona Izquierda: Buscador + Selector de tipo + Selector de año
        self.left_tools = ctk.CTkFrame(self.toolbar, fg_color='transparent')
        self.left_tools.pack(side='left', fill='y')

        self.search_entry = entry(
            self.left_tools,
            placeholder_text="Buscar por título...",
            width=210,
        )
        self.search_entry.pack(side='left', padx=(0, SPACING['sm']))
        self.search_entry.bind('<KeyRelease>', lambda e: self._apply_filters())

        # Selector de Tipo con ancho suficiente y placeholder
        self.type_var = ctk.StringVar(value="Todos los tipos")
        self.type_menu = option_menu(
            self.left_tools,
            values=["Todos los tipos"],
            variable=self.type_var,
            command=lambda c: self._apply_filters(),
            width=160,
        )
        self.type_menu.pack(side='left', padx=(0, SPACING['sm']))

        # Selector de filtro por año con ancho suficiente
        self.year_var = ctk.StringVar(value="Todos los años")
        self.year_menu = option_menu(
            self.left_tools,
            values=["Todos los años", "Últimos 2 años", "Últimos 5 años", "Personalizado"],
            variable=self.year_var,
            command=self._on_filter_option_changed,
            width=150,
        )
        self.year_menu.pack(side='left', padx=(0, SPACING['sm']))

        # Entradas numéricas para rango personalizado
        self.from_entry = entry(self.left_tools, placeholder_text="Desde", width=80)
        self.to_entry = entry(self.left_tools, placeholder_text="Hasta", width=80)
        self.btn_apply_range = button(
            self.left_tools,
            text="Aplicar",
            variant='secondary',
            command=self._apply_filters,
            height=CONTROL_HEIGHT,
        )

        # Zona Derecha: Acciones globales con orden fijo
        # [Actualizar] -> [Crear producto (Primario al final)]
        self.right_tools = ctk.CTkFrame(self.toolbar, fg_color='transparent')
        self.right_tools.pack(side='right', fill='y')

        # Botón primario al final (Crear producto)
        self.btn_create = button(
            self.right_tools,
            text="Crear producto",
            variant='primary',
            command=self.create,
            height=CONTROL_HEIGHT,
        )
        self.btn_create.pack(side='right', padx=(SPACING['sm'], 0))

        # Botón terciario de actualización
        self.btn_refresh = button(
            self.right_tools,
            text="🔄 Actualizar",
            variant='tertiary',
            command=self.refresh,
            height=CONTROL_HEIGHT,
        )
        self.btn_refresh.pack(side='right', padx=(SPACING['sm'], 0))

        # Botón responsive 'Más acciones ▾'
        self.btn_more = button(
            self.right_tools,
            text="Más acciones ▾",
            variant='secondary',
            command=self._show_more_actions_menu,
            height=CONTROL_HEIGHT,
        )

        # --- 3. Barra contextual de selección (Oculta por defecto) ---
        self.context_bar = SelectionActionBar(
            self,
            on_edit=self.edit,
            on_toggle_active=self.toggle_active,
            on_delete=self.delete,
            on_clear=self._clear_selection,
        )
        self.context_bar.grid(
            row=2,
            column=0,
            sticky='ew',
            padx=SPACING['lg'],
            pady=(0, SPACING['sm']),
        )
        self.context_bar.grid_remove()

        # --- 4. Tabla dentro de tarjeta con casillas y selección múltiple ---
        columns = [
            ('id', 'ID', 70, 'center'),
            ('title', 'Título del producto', 320, 'w'),
            ('type', 'Tipo de producto', 160, 'w'),
            ('year', 'Año', 90, 'center'),
            ('group', 'Grupo ID', 100, 'center'),
            ('active', 'Estado', 100, 'center'),
        ]
        self.table = DataTable(
            self,
            columns=columns,
            on_selection_change=self._on_table_selection_change,
            on_double_click=self._on_row_double_click,
            on_delete_key=self.delete,
            on_context_menu=self._show_context_menu,
            empty_icon="",
            empty_title="No hay productos registrados",
            empty_message="No se encontraron productos académicos con los criterios actuales de búsqueda y filtro.",
            empty_action_text="Restablecer filtros",
            empty_action_command=self._reset_filters,
        )
        self.table.grid(
            row=3,
            column=0,
            sticky='nsew',
            padx=SPACING['lg'],
            pady=(0, SPACING['sm']),
        )

        # --- 5. Pie con contador de registros ---
        self.footer_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.footer_frame.grid(
            row=4,
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

        # Atajos de teclado y adaptabilidad responsive
        self._bind_shortcuts()
        self.bind('<Configure>', self._on_configure)

        self.load_data()

    def _bind_shortcuts(self):
        """Vincula atajos de teclado para la pestaña."""
        self.bind('<F5>', lambda e: self.refresh())
        self.bind('<Control-n>', lambda e: (self.create(), "break")[1])
        self.bind('<Control-N>', lambda e: (self.create(), "break")[1])
        self.bind('<Control-f>', lambda e: self._focus_search())
        self.bind('<Control-F>', lambda e: self._focus_search())

    def _focus_search(self):
        """Enfoca y selecciona el texto del buscador."""
        self.search_entry.focus_set()
        self.search_entry.select_range(0, 'end')
        return "break"

    def _on_configure(self, event):
        """Adapta la visibilidad de los botones en pantallas angostas."""
        width = self.winfo_width()
        if width < 860:
            if not self.btn_more.winfo_ismapped():
                self.btn_refresh.pack_forget()
                self.btn_more.pack(side='right', padx=(SPACING['sm'], 0))
        else:
            if self.btn_more.winfo_ismapped():
                self.btn_more.pack_forget()
                self.btn_refresh.pack(side='right', padx=(SPACING['sm'], 0))

    def _show_more_actions_menu(self):
        """Muestra menú desplegable cuando la barra está en modo compacto."""
        menu = tk.Menu(
            self,
            tearoff=0,
            bg=COLORS['surface'],
            fg=COLORS['ink'],
            activebackground=COLORS['surface_alt'],
            activeforeground=COLORS['accent'],
            font=font('body'),
        )
        menu.add_command(label="🔄 Actualizar lista", command=self.refresh)
        menu.add_command(label="🔄 Restablecer filtros", command=self._reset_filters)

        bx = self.btn_more.winfo_rootx()
        by = self.btn_more.winfo_rooty() + self.btn_more.winfo_height() + 2
        try:
            menu.tk_popup(bx, by)
        finally:
            menu.grab_release()

    def _reset_filters(self):
        """Restablece los filtros de búsqueda, tipo y año."""
        self.search_entry.delete(0, 'end')
        self.type_var.set("Todos los tipos")
        self.year_var.set("Todos los años")
        self._on_filter_option_changed("Todos los años")
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
                curr_inv = curr_group.down_investigador
                while curr_inv is not None:
                    curr_prod = curr_inv.down_producto
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

        # Actualiza dinámicamente los tipos disponibles en el selector
        available_types = sorted(list(set(
            str(getattr(p, 'tipo', '') or getattr(p, 'type', '')).strip()
            for p in self._all_productos
            if getattr(p, 'tipo', None) or getattr(p, 'type', None)
        )))
        type_options = ["Todos los tipos"] + [t for t in available_types if t]
        self.type_menu.configure(values=type_options)

        self._apply_filters()
        self._clear_selection()

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
        """Aplica conjuntamente los filtros de tipo, año y texto de búsqueda."""
        query = self.search_entry.get().strip().lower()
        selected_type = self.type_var.get()
        filter_year = self.year_var.get()
        current_year = datetime.datetime.now().year

        filtered = []
        for p in self._all_productos:
            title = str(getattr(p, 'titulo', '') or getattr(p, 'title', '')).lower()
            ptype_raw = str(getattr(p, 'tipo', '') or getattr(p, 'type', ''))
            ptype = ptype_raw.lower()
            try:
                pyear = int(getattr(p, 'anio', 0) or getattr(p, 'year', 0))
            except Exception:
                pyear = 0

            # 1. Filtro por tipo de producto
            if selected_type != "Todos los tipos":
                if selected_type.lower() != ptype:
                    continue

            # 2. Filtro por año
            year_match = True
            if filter_year == "Últimos 2 años":
                year_match = pyear >= (current_year - 2)
            elif filter_year == "Últimos 5 años":
                year_match = pyear >= (current_year - 5)
            elif filter_year == "Personalizado":
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

            # 3. Filtro por texto de búsqueda
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

    def _on_table_selection_change(self, selected_ids: List[str]):
        """Notificación de cambio en la selección múltiple."""
        self._selected_ids = []
        for sid in selected_ids:
            try:
                self._selected_ids.append(int(sid))
            except ValueError:
                pass

        count = len(self._selected_ids)
        if count == 0:
            self.context_bar.grid_remove()
        else:
            self.context_bar.grid()
            is_active = self.table.are_selected_active()
            self.context_bar.update_selection(count, is_active=is_active)

    def _clear_selection(self):
        """Limpia la selección tanto en la tabla como en la barra contextual."""
        self.table.clear_selection()
        self._selected_ids.clear()
        self.context_bar.grid_remove()

    def _on_row_double_click(self, item_id: str, values: tuple):
        """Abre la edición al hacer doble clic o Enter sobre una fila."""
        try:
            self._selected_ids = [int(item_id)]
        except ValueError:
            pass
        self.edit()

    def _show_context_menu(self, event, selected_ids: List[str]):
        """Despliega el menú contextual con clic derecho sobre una fila."""
        if not selected_ids:
            return

        is_active = self.table.are_selected_active()
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
            menu.add_command(label="✏️ Editar", command=self.edit)
        menu.add_command(label=f"🔄 {toggle_text}", command=self.toggle_active)
        menu.add_separator()
        menu.add_command(label="🗑️ Eliminar", command=self.delete)

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

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
        if not self._selected_ids:
            return
        target_id = self._selected_ids[0]
        app = self.get_app()
        if not app:
            return

        prod = app.prod_crud.read(target_id)
        if not prod:
            for item in self._all_productos:
                if getattr(item, 'id', None) == target_id:
                    prod = item
                    break

        if not prod:
            messagebox.showerror("Error", "No se encontró el producto seleccionado.")
            return

        form = ProductoForm(self, app=app, producto=prod, on_save=lambda data: self._on_save_edit(target_id, data))
        form.grab_set()

    def _on_save_edit(self, target_id: int, data: dict):
        """Aplica y guarda los cambios del producto en edición."""
        app = self.get_app()
        if not app:
            return
        try:
            app.prod_crud.update(target_id, **data)
            app.save_data()
            self.load_data()
            if hasattr(app, 'load_tabs_data'):
                app.load_tabs_data()
            messagebox.showinfo("Éxito", "Producto actualizado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el producto: {e}")

    def toggle_active(self):
        """Alterna el estado (Activar / Desactivar) de los productos seleccionados."""
        if not self._selected_ids:
            return
        app = self.get_app()
        if not app:
            return

        should_activate = not self.table.are_selected_active()
        try:
            for pid in self._selected_ids:
                if should_activate:
                    app.prod_crud.activate(pid)
                else:
                    app.prod_crud.deactivate(pid)

            app.save_data()
            self.load_data()
            if hasattr(app, 'load_tabs_data'):
                app.load_tabs_data()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cambiar estado: {e}")

    def activate(self):
        """Compatibilidad con métodos anteriores."""
        self._set_active_batch(True)

    def deactivate(self):
        """Compatibilidad con métodos anteriores."""
        self._set_active_batch(False)

    def _set_active_batch(self, is_active: bool):
        if not self._selected_ids:
            return
        app = self.get_app()
        if not app:
            return
        try:
            for pid in self._selected_ids:
                if is_active:
                    app.prod_crud.activate(pid)
                else:
                    app.prod_crud.deactivate(pid)
            app.save_data()
            self.load_data()
            if hasattr(app, 'load_tabs_data'):
                app.load_tabs_data()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cambiar estado: {e}")

    def delete(self):
        """Elimina físicamente los productos seleccionados tras confirmación modal."""
        if not self._selected_ids:
            return
        app = self.get_app()
        if not app:
            return

        count = len(self._selected_ids)
        plural = "s" if count != 1 else ""
        confirma = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro de eliminar {count} producto{plural} seleccionado{plural}?\n\nEsta acción no se puede deshacer.",
            icon='warning',
        )
        if not confirma:
            return

        try:
            deleted_count = 0
            for pid in list(self._selected_ids):
                if app.prod_crud.delete(pid):
                    deleted_count += 1

            app.save_data()
            self.load_data()
            if hasattr(app, 'load_tabs_data'):
                app.load_tabs_data()

            messagebox.showinfo(
                "Eliminación completada",
                f"Se ha{'n' if deleted_count != 1 else ''} eliminado {deleted_count} producto{'s' if deleted_count != 1 else ''} correctamente.",
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar productos: {e}")

    def refresh(self):
        """Actualiza manualmente la información del listado."""
        self.load_data()
