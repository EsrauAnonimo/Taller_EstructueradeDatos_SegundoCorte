# -*- coding: utf-8 -*-
"""Pestaña de gestión de Productos de Investigación refactorizada con TablaCRUD."""

from typing import Optional, List, Any
import datetime
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from gui.styles import (
    COLORS,
    RADIUS,
    SPACING,
    CONTROL_HEIGHT,
    font,
    entry,
    combo,
)
from gui.widgets.tabla_crud import TablaCRUD
from gui.forms.producto_form import ProductoForm
from entidades.producto import Producto


class ProductosTab(ctk.CTkFrame):
    """Pestaña para listar, buscar, filtrar por año/tipo, crear, editar y eliminar productos
    utilizando el componente estandarizado TablaCRUD."""

    def __init__(self, master, app=None):
        super().__init__(master, fg_color='transparent')
        self._app_ref = app
        self.pack(fill='both', expand=True)

        self._all_productos: List = []

        # Configuración del layout vertical
        # Row 0: Encabezado (título + subtítulo)
        # Row 1: TablaCRUD (barra de herramientas + filtros + barra contextual + tabla + pie)
        self.grid_rowconfigure(1, weight=1)
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
            text="Productos de investigación",
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

        # --- 2. Tabla CRUD Reutilizable ---
        columns = [
            ('id', 'ID', 70, 'center'),
            ('title', 'Título del producto', 320, 'w'),
            ('type', 'Tipo', 140, 'w'),
            ('year', 'Año', 90, 'center'),
            ('group', 'Grupo ID', 90, 'center'),
            ('active', 'Estado', 100, 'center'),
        ]

        self.table = TablaCRUD(
            self,
            columns=columns,
            on_editar=self.edit,
            on_toggle_estado=self.toggle_active,
            on_eliminar=self.delete,
            on_crear=self.create,
            on_actualizar=self.refresh,
            entity_name="producto",
            entity_name_plural="productos",
            create_button_text="Crear producto",
            search_placeholder="Buscar por título...",
            empty_icon="📄",
            empty_title="No hay productos registrados",
            empty_message="Registra productos manualmente o importa un grupo desde MinCiencias para extraer publicaciones.",
            empty_action_text="Crear producto",
            empty_action_command=self.create,
        )
        self.table.grid(
            row=1,
            column=0,
            sticky='nsew',
            padx=SPACING['lg'],
            pady=(0, SPACING['lg']),
        )

        # --- 3. Filtros específicos inyectados en la zona izquierda de TablaCRUD ---
        self._setup_custom_filters()

        self.load_data()

    def _setup_custom_filters(self):
        """Inyecta el selector de tipo y el filtro de año con CTkSegmentedButton
        en extra_filters_frame de TablaCRUD."""
        container = self.table.extra_filters_frame

        # Selector de tipo con estilo consistente
        self.type_var = ctk.StringVar(value="Todos los tipos")
        self.type_menu = combo(
            container,
            values=["Todos los tipos"],
            variable=self.type_var,
            command=lambda c: self.table.apply_filter(),
            width=160,
        )
        self.type_menu.pack(side='left', padx=(0, SPACING['sm']))

        # Filtro de año con CTkSegmentedButton
        self.year_segmented = ctk.CTkSegmentedButton(
            container,
            values=["Todos", "Últimos 2 años", "Últimos 5 años", "Personalizado"],
            command=self._on_year_segmented_changed,
            height=CONTROL_HEIGHT,
            corner_radius=RADIUS['control'],
            fg_color=COLORS['segment_bg'],
            selected_color=COLORS['accent'],
            selected_hover_color=COLORS['accent_hover'],
            unselected_color=COLORS['surface'],
            unselected_hover_color=COLORS['surface_alt'],
            text_color=COLORS['ink'],
            font=font('small'),
        )
        self.year_segmented.set("Todos")
        self.year_segmented.pack(side='left', padx=(0, SPACING['sm']))

        # Contenedor para rango personalizado Desde/Hasta (ancho amplio para no cortarse)
        self.custom_range_frame = ctk.CTkFrame(container, fg_color='transparent')

        self.from_entry = entry(
            self.custom_range_frame,
            placeholder_text="Desde",
            width=75,
        )
        self.from_entry.pack(side='left', padx=(0, SPACING['xs']))
        self.from_entry.bind('<KeyRelease>', lambda e: self.table.apply_filter())

        self.lbl_sep = ctk.CTkLabel(
            self.custom_range_frame,
            text="a",
            font=font('small'),
            text_color=COLORS['muted'],
        )
        self.lbl_sep.pack(side='left', padx=(0, SPACING['xs']))

        self.to_entry = entry(
            self.custom_range_frame,
            placeholder_text="Hasta",
            width=75,
        )
        self.to_entry.pack(side='left', padx=(0, SPACING['xs']))
        self.to_entry.bind('<KeyRelease>', lambda e: self.table.apply_filter())

        # Conectar el predicado de filtrado con TablaCRUD
        self.table.set_filter_predicate(self._custom_filter_predicate)

    def _on_year_segmented_changed(self, value: str):
        """Muestra u oculta los campos numéricos de rango según la opción elegida."""
        if value == "Personalizado":
            self.custom_range_frame.pack(side='left')
            self.from_entry.focus_set()
        else:
            self.custom_range_frame.pack_forget()

        self.table.apply_filter()

    def _custom_filter_predicate(self, row: dict) -> bool:
        """Predicado aplicado a cada fila para evaluar tipo de producto y rango de años."""
        raw_prod = row.get('raw')
        if raw_prod is None:
            return True

        # 1. Filtro por tipo de producto
        selected_type = self.type_var.get()
        if selected_type and selected_type != "Todos los tipos":
            ptype = str(getattr(raw_prod, 'tipo', '') or getattr(raw_prod, 'type', '')).lower()
            if selected_type.lower() != ptype:
                return False

        # 2. Filtro por año
        current_year = datetime.datetime.now().year
        try:
            pyear = int(getattr(raw_prod, 'anio', 0) or getattr(raw_prod, 'year', 0))
        except Exception:
            pyear = 0

        year_mode = self.year_segmented.get()
        if year_mode == "Últimos 2 años":
            if pyear < (current_year - 2):
                return False
        elif year_mode == "Últimos 5 años":
            if pyear < (current_year - 5):
                return False
        elif year_mode == "Personalizado":
            from_str = self.from_entry.get().strip()
            to_str = self.to_entry.get().strip()

            try:
                from_val = int(from_str) if from_str else None
            except ValueError:
                from_val = None

            try:
                to_val = int(to_str) if to_str else None
            except ValueError:
                to_val = None

            if from_val is not None and pyear < from_val:
                return False
            if to_val is not None and pyear > to_val:
                return False

        return True

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
        """Obtiene todos los productos de la estructura de multilista o CRUD."""
        app = self.get_app()
        if app is None or not hasattr(app, 'multilista'):
            return []
        prods = []
        try:
            curr_g = app.multilista.head_group
            while curr_g is not None:
                curr_i = curr_g.sublist
                while curr_i is not None:
                    curr_p = curr_i.sublist
                    while curr_p is not None:
                        prods.append(curr_p.data)
                        curr_p = curr_p.next
                    curr_i = curr_i.next
                curr_g = curr_g.next
        except Exception:
            try:
                prods = list(app.prod_crud.list_all())
            except Exception:
                prods = []
        return prods

    def load_data(self):
        """Recarga los datos de los productos y actualiza las opciones del menú de tipos."""
        self._all_productos = self._get_all_raw_productos()

        # Actualizar dinámicamente las opciones del menú de tipo
        types_set = set()
        for p in self._all_productos:
            t = getattr(p, 'tipo', '') or getattr(p, 'type', '')
            if t and t.strip():
                types_set.add(t.strip())

        unique_types = ["Todos los tipos"] + sorted(list(types_set))
        current_val = self.type_var.get()
        self.type_menu.configure(values=unique_types)
        if current_val in unique_types:
            self.type_var.set(current_val)
        else:
            self.type_var.set("Todos los tipos")

        # Preparar filas para TablaCRUD
        rows = []
        for p in self._all_productos:
            pid = getattr(p, 'id', None)
            title = getattr(p, 'titulo', '') or getattr(p, 'title', '')
            ptype = getattr(p, 'tipo', '') or getattr(p, 'type', '')
            year = getattr(p, 'anio', '') or getattr(p, 'year', '')
            gid = getattr(p, 'grupo_id', getattr(p, 'group', ''))
            active = getattr(p, 'validado', getattr(p, 'active', True))

            rows.append({
                'id': str(pid) if pid is not None else '',
                'values': (
                    str(pid) if pid is not None else '',
                    str(title),
                    str(ptype),
                    str(year),
                    str(gid) if gid is not None else '',
                    "● Activo" if active else "● Inactivo",
                ),
                'is_active': bool(active),
                'raw': p,
            })

        self.table.set_rows(rows)

    def create(self):
        """Abre el formulario modal para registrar un nuevo producto."""
        app = self.get_app()
        form = ProductoForm(self, app=app, on_save=self._on_save_create)
        form.grab_set()

    def _on_save_create(self, data: dict):
        """Persiste el nuevo producto mediante la capa CRUD."""
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

    def edit(self, item_id: Optional[str] = None):
        """Abre el formulario para editar el producto seleccionado."""
        target_id_str = item_id or self.table.get_selected_id()
        if not target_id_str:
            return

        try:
            target_id = int(target_id_str)
        except ValueError:
            target_id = target_id_str

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

    def _on_save_edit(self, target_id: Any, data: dict):
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

    def toggle_active(self, selected_ids: Optional[List[str]] = None, should_activate: Optional[bool] = None):
        """Alterna el estado (Activar / Desactivar) de los productos seleccionados."""
        ids = selected_ids or self.table.get_selected_ids()
        if not ids:
            return
        app = self.get_app()
        if not app:
            return

        if should_activate is None:
            should_activate = not self.table.are_selected_active()

        try:
            for sid in ids:
                pid = int(sid) if sid.isdigit() else sid
                if should_activate:
                    app.prod_crud.activate(pid)
                else:
                    app.prod_crud.deactivate(pid)

            app.save_data()
            self.load_data()
            if hasattr(app, 'load_tabs_data'):
                app.load_tabs_data()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cambiar estado de productos: {e}")

    def delete(self, selected_ids: Optional[List[str]] = None):
        """Elimina los productos seleccionados tras la confirmación del modal."""
        ids = selected_ids or self.table.get_selected_ids()
        if not ids:
            return
        app = self.get_app()
        if not app:
            return

        try:
            deleted_count = 0
            for sid in ids:
                pid = int(sid) if sid.isdigit() else sid
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
