# -*- coding: utf-8 -*-
"""Pestaña de gestión de Investigadores."""

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
from gui.forms.investigador_form import InvestigadorForm
from entidades.investigador import Investigador


class InvestigadoresTab(ctk.CTkFrame):
    """Pestaña para listar, buscar, crear, editar y eliminar investigadores."""

    def __init__(self, master, app=None):
        super().__init__(master, fg_color='transparent')
        self._app_ref = app
        self.pack(fill='both', expand=True)

        self._all_investigadores: List = []
        self._selected_cedula: Optional[str] = None

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
            text="Investigadores",
            font=font('display'),
            text_color=COLORS['ink'],
            anchor='w',
        )
        self.title_label.pack(fill='x', anchor='w')

        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Gestión de investigadores y docentes adscritos a grupos de investigación",
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
            placeholder_text="Buscar por cédula, nombre o correo...",
            width=280,
        )
        self.search_entry.pack(side='left', padx=(0, SPACING['md']))
        self.search_entry.bind('<KeyRelease>', lambda e: self._on_search_change())

        # Acciones a la derecha ordenadas por jerarquía estricta
        # Primario
        self.btn_create = button(
            self.toolbar,
            text="Crear investigador",
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
            ('id', 'ID', 60, 'center'),
            ('cedula', 'Cédula', 120, 'w'),
            ('name', 'Nombre completo', 260, 'w'),
            ('email', 'Correo electrónico', 220, 'w'),
            ('group', 'Grupo ID', 90, 'center'),
            ('active', 'Estado', 110, 'center'),
        ]
        self.table = DataTable(
            self,
            columns=columns,
            on_select=self._on_row_select,
            on_double_click=self._on_row_double_click,
            empty_icon="",
            empty_title="Aún no hay investigadores registrados",
            empty_message="Aún no hay investigadores. Importa un grupo desde MinCiencias o registra investigadores manualmente.",
            empty_action_text="Importar grupo desde MinCiencias",
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
            text="0 investigadores",
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
            if hasattr(curr, 'inv_crud'):
                self._app_ref = curr
                return curr
            curr = getattr(curr, 'master', None)
        return None

    def _get_all_raw_investigadores(self) -> List:
        """Obtiene todos los investigadores (activos e inactivos) de la multilista."""
        app = self.get_app()
        if app is None or not hasattr(app, 'multilista'):
            return []
        invs = []
        try:
            curr_group = app.multilista.head_group
            while curr_group is not None:
                curr_inv = curr_group.sublist
                while curr_inv is not None:
                    invs.append(curr_inv.data)
                    curr_inv = curr_inv.next
                curr_group = curr_group.next
        except Exception:
            try:
                invs = list(app.inv_crud.list_all())
            except Exception:
                invs = []
        return invs

    def load_data(self):
        """Recarga los datos de los investigadores desde la capa de persistencia."""
        self._all_investigadores = self._get_all_raw_investigadores()
        self._render_rows(self._all_investigadores)
        self._update_selection_buttons(None)

    def _render_rows(self, investigadores: List):
        """Renderiza las filas de investigadores en el DataTable con badges."""
        self.table.clear()
        for i in investigadores:
            iid = getattr(i, 'id', None)
            ced = getattr(i, 'cedula', '')
            nom = getattr(i, 'nombres', '') or getattr(i, 'name', '')
            ape = getattr(i, 'apellidos', '')
            full_name = f"{nom} {ape}".strip() if ape else nom
            mail = getattr(i, 'email', '')
            gid = getattr(i, 'grupo_id', getattr(i, 'group', ''))
            active = getattr(i, 'activo', getattr(i, 'active', True))
            status_text = "Activo" if active else "Inactivo"

            values = (
                str(iid) if iid is not None else '',
                str(ced),
                str(full_name),
                str(mail),
                str(gid) if gid is not None else '',
                status_text,
            )
            # Clave única por cédula o id
            row_key = str(ced) if ced else str(iid)
            self.table.insert_row(values, iid=row_key, is_active=bool(active))

        total = len(investigadores)
        suffix = "investigador" if total == 1 else "investigadores"
        self.count_label.configure(text=f"{total} {suffix}")

    def _on_search_change(self):
        """Filtra los investigadores en tiempo real según el texto ingresado."""
        query = self.search_entry.get().strip().lower()
        if not query:
            self._render_rows(self._all_investigadores)
            return

        filtered = []
        for i in self._all_investigadores:
            ced = str(getattr(i, 'cedula', '')).lower()
            nom = str(getattr(i, 'nombres', '') or getattr(i, 'name', '')).lower()
            ape = str(getattr(i, 'apellidos', '')).lower()
            mail = str(getattr(i, 'email', '')).lower()
            if query in ced or query in nom or query in ape or query in mail:
                filtered.append(i)

        self._render_rows(filtered)

    def _on_row_select(self, item_id: Optional[str], values: Optional[tuple]):
        """Actualiza el estado de los botones cuando se selecciona o deselecciona una fila."""
        self._update_selection_buttons(item_id)

    def _on_row_double_click(self, item_id: str, values: tuple):
        """Abre directamente la edición al hacer doble clic en una fila."""
        self._update_selection_buttons(item_id)
        self.edit()

    def _update_selection_buttons(self, item_id: Optional[str]):
        """Habilita o deshabilita los botones según haya una selección activa."""
        if item_id:
            self._selected_cedula = str(item_id)
            state = 'normal'
        else:
            self._selected_cedula = None
            state = 'disabled'

        self.btn_edit.configure(state=state)
        self.btn_delete.configure(state=state)
        self.btn_activate.configure(state=state)
        self.btn_deactivate.configure(state=state)

    def create(self):
        """Abre el formulario modal para registrar un nuevo investigador."""
        app = self.get_app()
        form = InvestigadorForm(self, app=app, on_save=self._on_save_create)
        form.grab_set()

    def _on_save_create(self, data: dict):
        """Persiste el nuevo investigador mediante el CRUD."""
        app = self.get_app()
        if not app:
            return
        try:
            nuevo = Investigador(
                cedula=str(data.get('cedula', '')),
                nombres=data.get('nombres') or data.get('name', ''),
                apellidos=data.get('apellidos', ''),
                email=data.get('email', ''),
                activo=data.get('activo', True),
                grupo_id=data.get('grupo_id') or data.get('group'),
            )
            app.inv_crud.create(nuevo)
            app.save_data()
            self.load_data()
            if hasattr(app, 'load_tabs_data'):
                app.load_tabs_data()
            messagebox.showinfo("Éxito", "Investigador registrado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar al investigador: {e}")

    def edit(self):
        """Abre el formulario para editar el investigador seleccionado."""
        if self._selected_cedula is None:
            return
        app = self.get_app()
        if not app:
            return

        inv = app.inv_crud.read(self._selected_cedula)
        if not inv:
            # Búsqueda por ID numérico en caso de que la clave sea el ID
            try:
                inv_id = int(self._selected_cedula)
                for item in self._all_investigadores:
                    if getattr(item, 'id', None) == inv_id:
                        inv = item
                        break
            except ValueError:
                pass

        if not inv:
            messagebox.showerror("Error", "No se encontró el investigador seleccionado.")
            return

        form = InvestigadorForm(self, app=app, investigador=inv, on_save=self._on_save_edit)
        form.grab_set()

    def _on_save_edit(self, data: dict):
        """Aplica y guarda los cambios del investigador en edición."""
        app = self.get_app()
        if not app or self._selected_cedula is None:
            return
        try:
            target_key = data.get('cedula', self._selected_cedula)
            app.inv_crud.update(self._selected_cedula, **data)
            app.save_data()
            self.load_data()
            if hasattr(app, 'load_tabs_data'):
                app.load_tabs_data()
            messagebox.showinfo("Éxito", "Investigador actualizado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el investigador: {e}")

    def delete(self):
        """Elimina físicamente el investigador seleccionado tras confirmación."""
        if self._selected_cedula is None:
            return
        app = self.get_app()
        if not app:
            return

        confirma = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro de eliminar el investigador con cédula {self._selected_cedula}?\n\nEsta acción no se puede deshacer.",
        )
        if not confirma:
            return

        try:
            res = app.inv_crud.delete(self._selected_cedula)
            if res:
                app.save_data()
                self.load_data()
                if hasattr(app, 'load_tabs_data'):
                    app.load_tabs_data()
                messagebox.showinfo("Éxito", "Investigador eliminado correctamente.")
            else:
                messagebox.showerror("Error", "No se pudo eliminar el investigador.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar: {e}")

    def activate(self):
        """Marca como activo el investigador seleccionado."""
        self._set_active_status(True)

    def deactivate(self):
        """Marca como inactivo el investigador seleccionado."""
        self._set_active_status(False)

    def _set_active_status(self, is_active: bool):
        """Actualiza el estado de activación en la capa de datos."""
        if self._selected_cedula is None:
            return
        app = self.get_app()
        if not app:
            return
        try:
            if is_active:
                app.inv_crud.activate(self._selected_cedula)
            else:
                app.inv_crud.deactivate(self._selected_cedula)
            app.save_data()
            self.load_data()
            if hasattr(app, 'load_tabs_data'):
                app.load_tabs_data()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cambiar estado: {e}")

    def refresh(self):
        """Actualiza manualmente la información del listado."""
        self.load_data()
