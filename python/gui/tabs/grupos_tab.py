# -*- coding: utf-8 -*-
"""Pestaña de gestión de Grupos de Investigación."""

from typing import Optional, List
from tkinter import messagebox
import customtkinter as ctk

from gui.styles import (
    COLORS,
    SPACING,
    font,
    button,
    entry,
)
from gui.widgets.data_table import DataTable
from gui.forms.grupo_form import GrupoForm
from entidades.grupo import Grupo


class GruposTab(ctk.CTkFrame):
    """Pestaña para listar, buscar, crear, editar y eliminar grupos de investigación."""

    def __init__(self, master, app=None):
        super().__init__(master, fg_color='transparent')
        self._app_ref = app
        self.pack(fill='both', expand=True)

        self._all_grupos: List = []
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
            text="Grupos de investigación",
            font=font('display'),
            text_color=COLORS['ink'],
            anchor='w',
        )
        self.title_label.pack(fill='x', anchor='w')

        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Administración de grupos académicos registrados en el sistema",
            font=font('body'),
            text_color=COLORS['muted'],
            anchor='w',
        )
        self.subtitle_label.pack(fill='x', anchor='w', pady=(SPACING['xs'], 0))

        # --- 2. Barra de herramientas ---
        self.toolbar = ctk.CTkFrame(self, fg_color='transparent')
        self.toolbar.grid(
            row=1,
            column=0,
            sticky='ew',
            padx=SPACING['lg'],
            pady=(0, SPACING['md']),
        )

        # Campo de búsqueda a la izquierda
        self.search_entry = entry(
            self.toolbar,
            placeholder_text="Buscar por código, nombre o líder...",
            width=280,
        )
        self.search_entry.pack(side='left', padx=(0, SPACING['md']))
        self.search_entry.bind('<KeyRelease>', lambda e: self._on_search_change())

        # Acciones a la derecha ordenadas por jerarquía
        self.btn_create = button(
            self.toolbar,
            text="Crear grupo",
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
            ('id', 'ID', 70, 'center'),
            ('code', 'Código Gruplac', 150, 'w'),
            ('name', 'Nombre', 280, 'w'),
            ('category', 'Categoría', 100, 'center'),
            ('leader', 'Líder', 180, 'w'),
            ('active', 'Estado', 100, 'center'),
        ]
        self.table = DataTable(
            self,
            columns=columns,
            on_select=self._on_row_select,
            on_double_click=self._on_row_double_click,
            empty_text="No hay grupos para mostrar",
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
            text="0 grupos",
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
            if hasattr(curr, 'grupo_crud'):
                self._app_ref = curr
                return curr
            curr = getattr(curr, 'master', None)
        return None

    def _get_all_raw_groups(self) -> List:
        """Obtiene todos los grupos (activos e inactivos) de la estructura."""
        app = self.get_app()
        if app is None or not hasattr(app, 'multilista'):
            return []
        groups = []
        try:
            curr = app.multilista.head_group
            while curr is not None:
                groups.append(curr.data)
                curr = curr.next
        except Exception:
            try:
                groups = list(app.grupo_crud.list_all())
            except Exception:
                groups = []
        return groups

    def load_data(self):
        """Recarga los datos de los grupos desde la capa CRUD."""
        self._all_grupos = self._get_all_raw_groups()
        self._render_rows(self._all_grupos)
        self._update_selection_buttons(None)

    def _render_rows(self, grupos: List):
        """Renderiza las filas de grupos en el DataTable."""
        self.table.clear()
        for g in grupos:
            gid = getattr(g, 'id', None)
            code = getattr(g, 'codigo_gruplac', '') or getattr(g, 'code', '')
            name = getattr(g, 'nombre', '') or getattr(g, 'name', '')
            cat = getattr(g, 'categoria', '') or getattr(g, 'category', '')
            leader = getattr(g, 'lider', '') or getattr(g, 'leader', '')
            active = getattr(g, 'activo', getattr(g, 'active', True))
            status_text = "Activo" if active else "Inactivo"

            values = (
                str(gid) if gid is not None else '',
                str(code),
                str(name),
                str(cat),
                str(leader),
                status_text,
            )
            self.table.insert_row(values, iid=str(gid), is_active=bool(active))

        total = len(grupos)
        suffix = "grupo" if total == 1 else "grupos"
        self.count_label.configure(text=f"{total} {suffix}")

    def _on_search_change(self):
        """Filtra los grupos en base al texto ingresado en la búsqueda."""
        query = self.search_entry.get().strip().lower()
        if not query:
            self._render_rows(self._all_grupos)
            return

        filtered = []
        for g in self._all_grupos:
            code = str(getattr(g, 'codigo_gruplac', '') or getattr(g, 'code', '')).lower()
            name = str(getattr(g, 'nombre', '') or getattr(g, 'name', '')).lower()
            leader = str(getattr(g, 'lider', '') or getattr(g, 'leader', '')).lower()
            cat = str(getattr(g, 'categoria', '') or getattr(g, 'category', '')).lower()
            if query in code or query in name or query in leader or query in cat:
                filtered.append(g)

        self._render_rows(filtered)

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
        """Abre el formulario de edición al hacer doble clic."""
        if item_id:
            try:
                self._selected_id = int(item_id)
            except ValueError:
                self._selected_id = item_id
            self.edit()

    def _update_selection_buttons(self, selected_id):
        """Habilita o deshabilita botones dependientes de la selección."""
        state = 'normal' if selected_id is not None else 'disabled'
        self.btn_edit.configure(state=state)
        self.btn_deactivate.configure(state=state)
        self.btn_activate.configure(state=state)
        self.btn_delete.configure(state=state)

    def create(self):
        """Abre el formulario modal para crear un nuevo grupo."""
        form = GrupoForm(self)
        self.wait_window(form)
        if form.result:
            app = self.get_app()
            if app:
                data = form.result
                all_raw = self._get_all_raw_groups()
                max_id = max([getattr(g, 'id', 0) for g in all_raw if isinstance(getattr(g, 'id', None), int)] + [0])
                new_id = max_id + 1

                grupo = Grupo(
                    id=new_id,
                    codigo_gruplac=data.get('code') or data.get('codigo_gruplac', ''),
                    nombre=data.get('name') or data.get('nombre', ''),
                    categoria=data.get('category') or data.get('categoria', ''),
                    lider=data.get('leader') or data.get('lider', ''),
                    activo=data.get('active', True),
                )
                success = app.grupo_crud.create(grupo)
                if success:
                    app.save_data()
                    self.load_data()
                else:
                    messagebox.showerror("Error", "No se pudo crear el grupo (código duplicado).")

    def edit(self):
        """Abre el formulario modal para editar el grupo seleccionado."""
        if self._selected_id is None:
            return
        app = self.get_app()
        if not app:
            return
        grupo = app.grupo_crud.get_by_id(self._selected_id)
        if not grupo:
            # Buscar por si está inactivo
            for g in self._all_grupos:
                if getattr(g, 'id', None) == self._selected_id:
                    grupo = g
                    break
        if not grupo:
            messagebox.showwarning("Aviso", "No se encontró el grupo seleccionado.")
            return

        form = GrupoForm(self, data=grupo.to_dict() if hasattr(grupo, 'to_dict') else grupo.__dict__)
        self.wait_window(form)
        if form.result:
            data = form.result
            update_fields = {
                'codigo_gruplac': data.get('code') or data.get('codigo_gruplac', ''),
                'nombre': data.get('name') or data.get('nombre', ''),
                'categoria': data.get('category') or data.get('categoria', ''),
                'lider': data.get('leader') or data.get('lider', ''),
                'activo': data.get('active', True),
            }
            app.grupo_crud.update(self._selected_id, **update_fields)
            app.save_data()
            self.load_data()

    def deactivate(self):
        """Desactiva el grupo seleccionado."""
        if self._selected_id is None:
            return
        app = self.get_app()
        if app:
            app.grupo_crud.deactivate(self._selected_id)
            app.save_data()
            self.load_data()

    def activate(self):
        """Activa el grupo seleccionado."""
        if self._selected_id is None:
            return
        app = self.get_app()
        if app:
            app.grupo_crud.activate(self._selected_id)
            app.save_data()
            self.load_data()

    def delete(self):
        """Elimina físicamente el grupo seleccionado tras confirmación."""
        if self._selected_id is None:
            return
        confirm = messagebox.askyesno(
            "Confirmar eliminación",
            "¿Está seguro de que desea eliminar permanentemente este grupo?",
        )
        if confirm:
            app = self.get_app()
            if app:
                app.grupo_crud.delete(self._selected_id)
                app.save_data()
                self.load_data()

    def refresh(self):
        """Actualiza los datos de la tabla."""
        self.load_data()
