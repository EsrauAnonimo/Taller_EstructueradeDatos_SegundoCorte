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
            placeholder_text="Buscar por cédula, nombre o correo...",
            width=280,
        )
        self.search_entry.pack(side='left', padx=(0, SPACING['md']))
        self.search_entry.bind('<KeyRelease>', lambda e: self._on_search_change())

        # Acciones a la derecha ordenadas por jerarquía
        self.btn_create = button(
            self.toolbar,
            text="Crear investigador",
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
            ('cedula', 'Cédula', 120, 'w'),
            ('name', 'Nombre completo', 260, 'w'),
            ('email', 'Correo electrónico', 220, 'w'),
            ('group', 'Grupo ID', 100, 'center'),
            ('active', 'Estado', 100, 'center'),
        ]
        self.table = DataTable(
            self,
            columns=columns,
            on_select=self._on_row_select,
            on_double_click=self._on_row_double_click,
            empty_text="No hay investigadores para mostrar",
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
        """Obtiene todos los investigadores (activos e inactivos) de la estructura."""
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
        """Recarga los datos de investigadores desde el CRUD."""
        self._all_investigadores = self._get_all_raw_investigadores()
        self._render_rows(self._all_investigadores)
        self._update_selection_buttons(None)

    def _render_rows(self, investigadores: List):
        """Renderiza las filas de investigadores en el DataTable."""
        self.table.clear()
        for inv in investigadores:
            iid = getattr(inv, 'id', None)
            cedula = str(getattr(inv, 'cedula', '') or getattr(inv, 'id', ''))
            nombres = getattr(inv, 'nombres', '')
            apellidos = getattr(inv, 'apellidos', '')
            full_name = f"{nombres} {apellidos}".strip() or getattr(inv, 'name', '')
            email = getattr(inv, 'email', '')
            grupo_id = getattr(inv, 'grupo_id', getattr(inv, 'group', ''))
            active = getattr(inv, 'activo', getattr(inv, 'active', True))
            status_text = "Activo" if active else "Inactivo"

            values = (
                str(iid) if iid is not None else '',
                cedula,
                full_name,
                email,
                str(grupo_id) if grupo_id is not None else '',
                status_text,
            )
            self.table.insert_row(values, iid=cedula, is_active=bool(active))

        total = len(investigadores)
        suffix = "investigador" if total == 1 else "investigadores"
        self.count_label.configure(text=f"{total} {suffix}")

    def _on_search_change(self):
        """Filtra investigadores en tiempo real al escribir en la barra de búsqueda."""
        query = self.search_entry.get().strip().lower()
        if not query:
            self._render_rows(self._all_investigadores)
            return

        filtered = []
        for inv in self._all_investigadores:
            cedula = str(getattr(inv, 'cedula', '') or getattr(inv, 'id', '')).lower()
            nombres = str(getattr(inv, 'nombres', '')).lower()
            apellidos = str(getattr(inv, 'apellidos', '')).lower()
            name = str(getattr(inv, 'name', '')).lower()
            email = str(getattr(inv, 'email', '')).lower()
            if query in cedula or query in nombres or query in apellidos or query in name or query in email:
                filtered.append(inv)

        self._render_rows(filtered)

    def _on_row_select(self, item_id: Optional[str], values):
        """Callback al seleccionar o deseleccionar una fila."""
        self._selected_cedula = item_id
        self._update_selection_buttons(self._selected_cedula)

    def _on_row_double_click(self, item_id: str, values):
        """Abre la ventana de edición al hacer doble clic."""
        if item_id:
            self._selected_cedula = item_id
            self.edit()

    def _update_selection_buttons(self, selected_id):
        """Habilita o deshabilita botones según la selección activa."""
        state = 'normal' if selected_id is not None else 'disabled'
        self.btn_edit.configure(state=state)
        self.btn_deactivate.configure(state=state)
        self.btn_activate.configure(state=state)
        self.btn_delete.configure(state=state)

    def create(self):
        """Abre el formulario modal para crear un investigador."""
        form = InvestigadorForm(self)
        self.wait_window(form)
        if form.result:
            app = self.get_app()
            if app:
                data = form.result
                all_raw = self._get_all_raw_investigadores()
                max_id = max([getattr(i, 'id', 0) for i in all_raw if isinstance(getattr(i, 'id', None), int)] + [0])
                new_id = max_id + 1

                cedula = data.get('id') or data.get('cedula', '')
                name_parts = (data.get('name') or '').strip().split(' ', 1)
                nombres = name_parts[0] if name_parts else ''
                apellidos = name_parts[1] if len(name_parts) > 1 else ''

                grupo_val = data.get('group') or data.get('grupo_id')
                try:
                    grupo_id = int(grupo_val) if grupo_val is not None and str(grupo_val).strip() else None
                except ValueError:
                    grupo_id = None

                inv = Investigador(
                    id=new_id,
                    cedula=cedula,
                    nombres=nombres,
                    apellidos=apellidos,
                    email=data.get('email', ''),
                    activo=data.get('active', True),
                    grupo_id=grupo_id,
                )
                success = app.inv_crud.create(inv)
                if success:
                    app.save_data()
                    self.load_data()
                else:
                    messagebox.showerror("Error", "No se pudo registrar el investigador (cédula duplicada o grupo inexistente).")

    def edit(self):
        """Abre el formulario modal para editar el investigador seleccionado."""
        if not self._selected_cedula:
            return
        app = self.get_app()
        if not app:
            return

        inv = app.inv_crud.get_by_cedula(self._selected_cedula)
        if not inv:
            for i in self._all_investigadores:
                if str(getattr(i, 'cedula', '')) == self._selected_cedula or str(getattr(i, 'id', '')) == self._selected_cedula:
                    inv = i
                    break
        if not inv:
            messagebox.showwarning("Aviso", "No se encontró el investigador seleccionado.")
            return

        form_data = {
            'id': getattr(inv, 'cedula', '') or getattr(inv, 'id', ''),
            'name': f"{getattr(inv, 'nombres', '')} {getattr(inv, 'apellidos', '')}".strip() or getattr(inv, 'name', ''),
            'email': getattr(inv, 'email', ''),
            'group': str(getattr(inv, 'grupo_id', '') or getattr(inv, 'group', '')),
            'active': getattr(inv, 'activo', getattr(inv, 'active', True)),
        }
        form = InvestigadorForm(self, data=form_data)
        self.wait_window(form)
        if form.result:
            data = form.result
            name_parts = (data.get('name') or '').strip().split(' ', 1)
            nombres = name_parts[0] if name_parts else ''
            apellidos = name_parts[1] if len(name_parts) > 1 else ''

            grupo_val = data.get('group') or data.get('grupo_id')
            try:
                grupo_id = int(grupo_val) if grupo_val is not None and str(grupo_val).strip() else None
            except ValueError:
                grupo_id = None

            update_fields = {
                'nombres': nombres,
                'apellidos': apellidos,
                'email': data.get('email', ''),
                'activo': data.get('active', True),
                'grupo_id': grupo_id,
            }
            app.inv_crud.update(self._selected_cedula, **update_fields)
            app.save_data()
            self.load_data()

    def deactivate(self):
        """Desactiva el investigador seleccionado."""
        if not self._selected_cedula:
            return
        app = self.get_app()
        if app:
            app.inv_crud.deactivate(self._selected_cedula)
            app.save_data()
            self.load_data()

    def activate(self):
        """Activa el investigador seleccionado."""
        if not self._selected_cedula:
            return
        app = self.get_app()
        if app:
            app.inv_crud.activate(self._selected_cedula)
            app.save_data()
            self.load_data()

    def delete(self):
        """Elimina físicamente el investigador seleccionado tras confirmación."""
        if not self._selected_cedula:
            return
        confirm = messagebox.askyesno(
            "Confirmar eliminación",
            "¿Está seguro de que desea eliminar permanentemente este investigador?",
        )
        if confirm:
            app = self.get_app()
            if app:
                app.inv_crud.delete(self._selected_cedula)
                app.save_data()
                self.load_data()

    def refresh(self):
        """Actualiza los datos de la tabla."""
        self.load_data()
