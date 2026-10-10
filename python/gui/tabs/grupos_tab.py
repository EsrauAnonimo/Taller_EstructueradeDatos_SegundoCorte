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

        # --- 2. Barra de herramientas con jerarquía unificada ---
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

        # Acciones a la derecha ordenadas por jerarquía estricta
        # Primario
        self.btn_create = button(
            self.toolbar,
            text="Crear grupo",
            variant='primary',
            command=self.create,
        )
        self.btn_create.pack(side='right', padx=(SPACING['sm'], 0))

        # Terciario (Actualizar)
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
            ('id', 'ID', 70, 'center'),
            ('code', 'Código Gruplac', 150, 'w'),
            ('name', 'Nombre del grupo', 280, 'w'),
            ('category', 'Categoría', 100, 'center'),
            ('leader', 'Líder', 180, 'w'),
            ('active', 'Estado', 110, 'center'),
        ]
        self.table = DataTable(
            self,
            columns=columns,
            on_select=self._on_row_select,
            on_double_click=self._on_row_double_click,
            empty_icon="",
            empty_title="Aún no hay grupos registrados",
            empty_message="Importa un grupo desde MinCiencias (GrupLAC) o crea un nuevo grupo manualmente.",
            empty_action_text="Importar desde MinCiencias",
            empty_action_command=self._trigger_import,
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

    def _trigger_import(self):
        """Abre el diálogo de importación de MinCiencias desde el estado vacío."""
        app = self.get_app()
        if app and hasattr(app, 'download_scienti'):
            app.download_scienti()

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
        """Renderiza las filas de grupos en el DataTable con badges de color."""
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
        """Filtra la lista de grupos en tiempo real según el texto ingresado."""
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

    def _on_row_select(self, item_id: Optional[str], values: Optional[tuple]):
        """Actualiza el estado de los botones cuando se selecciona o deselecciona una fila."""
        self._update_selection_buttons(item_id)

    def _on_row_double_click(self, item_id: str, values: tuple):
        """Abre directamente la edición al hacer doble clic en una fila."""
        self._update_selection_buttons(item_id)
        self.edit()

    def _update_selection_buttons(self, item_id: Optional[str]):
        """Habilita o deshabilita los botones dependientes de una selección."""
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
        """Abre el formulario modal para registrar un nuevo grupo."""
        app = self.get_app()
        form = GrupoForm(self, on_save=self._on_save_create)
        form.grab_set()

    def _on_save_create(self, data: dict):
        """Persiste el nuevo grupo mediante el CRUD."""
        app = self.get_app()
        if not app:
            return
        try:
            nuevo = Grupo(
                codigo_gruplac=data.get('codigo_gruplac') or data.get('code', ''),
                nombre=data.get('nombre') or data.get('name', ''),
                categoria=data.get('categoria') or data.get('category', ''),
                lider=data.get('lider') or data.get('leader', ''),
                activo=data.get('activo', True),
                fecha_creacion=data.get('fecha_creacion', ''),
            )
            app.grupo_crud.create(nuevo)
            app.save_data()
            self.load_data()
            if hasattr(app, 'load_tabs_data'):
                app.load_tabs_data()
            messagebox.showinfo("Éxito", "Grupo creado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el grupo: {e}")

    def edit(self):
        """Abre el formulario para editar el grupo seleccionado."""
        if self._selected_id is None:
            return
        app = self.get_app()
        if not app:
            return
        grupo = app.grupo_crud.read(self._selected_id)
        if not grupo:
            messagebox.showerror("Error", "No se encontró el grupo seleccionado.")
            return

        form = GrupoForm(self, grupo=grupo, on_save=self._on_save_edit)
        form.grab_set()

    def _on_save_edit(self, data: dict):
        """Aplica y guarda los cambios del grupo en edición."""
        app = self.get_app()
        if not app or self._selected_id is None:
            return
        try:
            app.grupo_crud.update(self._selected_id, **data)
            app.save_data()
            self.load_data()
            if hasattr(app, 'load_tabs_data'):
                app.load_tabs_data()
            messagebox.showinfo("Éxito", "Grupo actualizado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el grupo: {e}")

    def delete(self):
        """Elimina físicamente el grupo seleccionado tras confirmación."""
        if self._selected_id is None:
            return
        app = self.get_app()
        if not app:
            return

        confirma = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro de eliminar el grupo con ID {self._selected_id}?\n\nEsta acción no se puede deshacer.",
        )
        if not confirma:
            return

        try:
            res = app.grupo_crud.delete(self._selected_id)
            if res:
                app.save_data()
                self.load_data()
                if hasattr(app, 'load_tabs_data'):
                    app.load_tabs_data()
                messagebox.showinfo("Éxito", "Grupo eliminado correctamente.")
            else:
                messagebox.showerror("Error", "No se pudo eliminar el grupo.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar: {e}")

    def activate(self):
        """Marca como activo el grupo seleccionado."""
        self._set_active_status(True)

    def deactivate(self):
        """Marca como inactivo el grupo seleccionado."""
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
                app.grupo_crud.activate(self._selected_id)
            else:
                app.grupo_crud.deactivate(self._selected_id)
            app.save_data()
            self.load_data()
            if hasattr(app, 'load_tabs_data'):
                app.load_tabs_data()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cambiar estado: {e}")

    def refresh(self):
        """Actualiza manualmente la información del listado."""
        self.load_data()
