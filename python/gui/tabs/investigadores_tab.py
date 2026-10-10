# -*- coding: utf-8 -*-
"""Pestaña de gestión de Investigadores."""

from typing import Optional, List
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
)
from gui.widgets.data_table import DataTable
from gui.widgets.selection_bar import SelectionActionBar
from gui.forms.investigador_form import InvestigadorForm
from entidades.investigador import Investigador


class InvestigadoresTab(ctk.CTkFrame):
    """Pestaña para listar, buscar, crear, editar y eliminar investigadores académicos."""

    def __init__(self, master, app=None):
        super().__init__(master, fg_color='transparent')
        self._app_ref = app
        self.pack(fill='both', expand=True)

        self._all_investigadores: List = []
        self._selected_cedulas: List[str] = []

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
            text="Investigadores",
            font=font('display'),
            text_color=COLORS['ink'],
            anchor='w',
        )
        self.title_label.pack(fill='x', anchor='w')

        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Directorio y vinculación de investigadores adscritos a grupos de investigación",
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

        # Zona Izquierda: Buscador
        self.left_tools = ctk.CTkFrame(self.toolbar, fg_color='transparent')
        self.left_tools.pack(side='left', fill='y')

        self.search_entry = entry(
            self.left_tools,
            placeholder_text="Buscar por cédula, nombre o correo...",
            width=300,
        )
        self.search_entry.pack(side='left')
        self.search_entry.bind('<KeyRelease>', lambda e: self._on_search_change())

        # Zona Derecha: Acciones globales con orden fijo
        # [Actualizar] -> [Crear investigador (Primario al final)]
        self.right_tools = ctk.CTkFrame(self.toolbar, fg_color='transparent')
        self.right_tools.pack(side='right', fill='y')

        # Botón primario al final (Crear investigador)
        self.btn_create = button(
            self.right_tools,
            text="Crear investigador",
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
            ('cedula', 'Cédula / ID', 120, 'center'),
            ('nombres', 'Nombres y Apellidos', 250, 'w'),
            ('email', 'Correo electrónico', 220, 'w'),
            ('grupo_id', 'Grupo ID', 100, 'center'),
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
            empty_title="No hay investigadores registrados",
            empty_message="Registra investigadores manualmente o importa un grupo desde MinCiencias para indexarlos automáticamente.",
            empty_action_text="Crear investigador",
            empty_action_command=self.create,
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
            text="0 investigadores",
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
        if width < 760:
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

        bx = self.btn_more.winfo_rootx()
        by = self.btn_more.winfo_rooty() + self.btn_more.winfo_height() + 2
        try:
            menu.tk_popup(bx, by)
        finally:
            menu.grab_release()

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
            curr_g = app.multilista.head_group
            seen = set()
            while curr_g is not None:
                curr_i = curr_g.down_investigador
                while curr_i is not None:
                    cid = getattr(curr_i.data, 'cedula', None) or getattr(curr_i.data, 'id', None)
                    if cid not in seen:
                        seen.add(cid)
                        invs.append(curr_i.data)
                    curr_i = curr_i.next
                curr_g = curr_g.next
        except Exception:
            try:
                invs = list(app.inv_crud.list_all())
            except Exception:
                invs = []
        return invs

    def load_data(self):
        """Recarga los datos de los investigadores desde la capa CRUD."""
        self._all_investigadores = self._get_all_raw_investigadores()
        self._render_rows(self._all_investigadores)
        self._clear_selection()

    def _render_rows(self, investigadores: List):
        """Renderiza las filas de investigadores en el DataTable con badges de color."""
        self.table.clear()
        for i in investigadores:
            cedula_str = str(getattr(i, 'cedula', '') or getattr(i, 'id', ''))
            nombres = f"{getattr(i, 'nombres', '')} {getattr(i, 'apellidos', '')}".strip() or getattr(i, 'name', '')
            email = getattr(i, 'email', '')
            gid = getattr(i, 'grupo_id', '') or getattr(i, 'group', '')
            active = getattr(i, 'activo', getattr(i, 'active', True))
            status_text = "Activo" if active else "Inactivo"

            values = (
                cedula_str,
                nombres,
                email,
                str(gid),
                status_text,
            )
            self.table.insert_row(values, iid=cedula_str, is_active=bool(active))

        total = len(investigadores)
        suffix = "investigador" if total == 1 else "investigadores"
        self.count_label.configure(text=f"{total} {suffix}")

    def _on_search_change(self):
        """Filtra la lista de investigadores en tiempo real según el texto ingresado."""
        query = self.search_entry.get().strip().lower()
        if not query:
            self._render_rows(self._all_investigadores)
            return

        filtered = []
        for i in self._all_investigadores:
            cedula = str(getattr(i, 'cedula', '') or getattr(i, 'id', '')).lower()
            name = f"{getattr(i, 'nombres', '')} {getattr(i, 'apellidos', '')}".strip().lower() or str(getattr(i, 'name', '')).lower()
            email = str(getattr(i, 'email', '')).lower()
            gid = str(getattr(i, 'grupo_id', '') or getattr(i, 'group', '')).lower()

            if query in cedula or query in name or query in email or query in gid:
                filtered.append(i)

        self._render_rows(filtered)

    def _on_table_selection_change(self, selected_ids: List[str]):
        """Notificación de cambio en la selección múltiple."""
        self._selected_cedulas = [str(sid) for sid in selected_ids]
        count = len(self._selected_cedulas)

        if count == 0:
            self.context_bar.grid_remove()
        else:
            self.context_bar.grid()
            is_active = self.table.are_selected_active()
            self.context_bar.update_selection(count, is_active=is_active)

    def _clear_selection(self):
        """Limpia la selección tanto en la tabla como en la barra contextual."""
        self.table.clear_selection()
        self._selected_cedulas.clear()
        self.context_bar.grid_remove()

    def _on_row_double_click(self, item_id: str, values: tuple):
        """Abre la edición al hacer doble clic o Enter sobre una fila."""
        self._selected_cedulas = [str(item_id)]
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
                cedula=data.get('cedula', ''),
                nombres=data.get('nombres', ''),
                apellidos=data.get('apellidos', ''),
                email=data.get('email', ''),
                activo=data.get('activo', True),
                grupo_id=data.get('grupo_id'),
            )
            app.inv_crud.create(nuevo)
            app.save_data()
            self.load_data()
            if hasattr(app, 'load_tabs_data'):
                app.load_tabs_data()
            messagebox.showinfo("Éxito", "Investigador registrado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el investigador: {e}")

    def edit(self):
        """Abre el formulario para editar el investigador seleccionado."""
        if not self._selected_cedulas:
            return
        target_cedula = self._selected_cedulas[0]
        app = self.get_app()
        if not app:
            return

        inv = app.inv_crud.read(target_cedula)
        if not inv:
            for item in self._all_investigadores:
                if str(getattr(item, 'cedula', None) or getattr(item, 'id', None)) == target_cedula:
                    inv = item
                    break

        if not inv:
            messagebox.showerror("Error", "No se encontró el investigador seleccionado.")
            return

        form = InvestigadorForm(self, app=app, investigador=inv, on_save=lambda data: self._on_save_edit(target_cedula, data))
        form.grab_set()

    def _on_save_edit(self, target_cedula: str, data: dict):
        """Aplica y guarda los cambios del investigador en edición."""
        app = self.get_app()
        if not app:
            return
        try:
            app.inv_crud.update(target_cedula, **data)
            app.save_data()
            self.load_data()
            if hasattr(app, 'load_tabs_data'):
                app.load_tabs_data()
            messagebox.showinfo("Éxito", "Investigador actualizado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el investigador: {e}")

    def toggle_active(self):
        """Alterna el estado (Activar / Desactivar) de los investigadores seleccionados."""
        if not self._selected_cedulas:
            return
        app = self.get_app()
        if not app:
            return

        should_activate = not self.table.are_selected_active()
        try:
            for cid in self._selected_cedulas:
                if should_activate:
                    app.inv_crud.activate(cid)
                else:
                    app.inv_crud.deactivate(cid)

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
        if not self._selected_cedulas:
            return
        app = self.get_app()
        if not app:
            return
        try:
            for cid in self._selected_cedulas:
                if is_active:
                    app.inv_crud.activate(cid)
                else:
                    app.inv_crud.deactivate(cid)
            app.save_data()
            self.load_data()
            if hasattr(app, 'load_tabs_data'):
                app.load_tabs_data()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cambiar estado: {e}")

    def delete(self):
        """Elimina físicamente los investigadores seleccionados tras confirmación modal."""
        if not self._selected_cedulas:
            return
        app = self.get_app()
        if not app:
            return

        count = len(self._selected_cedulas)
        plural = "es" if count != 1 else ""
        confirma = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro de eliminar {count} investigador{plural} seleccionado{plural}?\n\nEsta acción no se puede deshacer.",
            icon='warning',
        )
        if not confirma:
            return

        try:
            deleted_count = 0
            for cid in list(self._selected_cedulas):
                if app.inv_crud.delete(cid):
                    deleted_count += 1

            app.save_data()
            self.load_data()
            if hasattr(app, 'load_tabs_data'):
                app.load_tabs_data()

            messagebox.showinfo(
                "Eliminación completada",
                f"Se ha{'n' if deleted_count != 1 else ''} eliminado {deleted_count} investigador{'es' if deleted_count != 1 else ''} correctamente.",
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar investigadores: {e}")

    def refresh(self):
        """Actualiza manualmente la información del listado."""
        self.load_data()
