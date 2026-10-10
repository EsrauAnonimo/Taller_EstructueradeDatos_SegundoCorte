# -*- coding: utf-8 -*-
"""Pestaña de gestión de Grupos de Investigación."""

from typing import Optional, List
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from gui.styles import (
    COLORS,
    RADIUS,
    SPACING,
    CONTROL_HEIGHT,
    font,
    button,
    entry,
)
from gui.widgets.data_table import DataTable
from gui.widgets.selection_bar import SelectionActionBar
from gui.forms.grupo_form import GrupoForm
from entidades.grupo import Grupo


class GruposTab(ctk.CTkFrame):
    """Pestaña para listar, buscar, crear, editar y eliminar grupos de investigación con acciones contextuales."""

    def __init__(self, master, app=None):
        super().__init__(master, fg_color='transparent')
        self._app_ref = app
        self.pack(fill='both', expand=True)

        self._all_grupos: List = []
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

        # --- 2. Barra de herramientas principal (Dos Zonas) ---
        self.toolbar = ctk.CTkFrame(self, fg_color='transparent')
        self.toolbar.grid(
            row=1,
            column=0,
            sticky='ew',
            padx=SPACING['lg'],
            pady=(0, SPACING['sm']),
        )

        # Zona Izquierda: Buscador y filtros
        self.left_tools = ctk.CTkFrame(self.toolbar, fg_color='transparent')
        self.left_tools.pack(side='left', fill='y')

        self.search_entry = entry(
            self.left_tools,
            placeholder_text="Buscar por código, nombre o líder...",
            width=300,
        )
        self.search_entry.pack(side='left')
        self.search_entry.bind('<KeyRelease>', lambda e: self._on_search_change())

        # Zona Derecha: Acciones globales con orden fijo
        # [Actualizar] -> [Crear grupo] -> [Importar desde URL (Primario al final)]
        self.right_tools = ctk.CTkFrame(self.toolbar, fg_color='transparent')
        self.right_tools.pack(side='right', fill='y')

        # Botón primario al final (Importar desde URL)
        self.btn_import = button(
            self.right_tools,
            text="Importar desde URL",
            variant='primary',
            command=self._on_import_scienti,
            height=CONTROL_HEIGHT,
        )
        self.btn_import.pack(side='right', padx=(SPACING['sm'], 0))

        # Botón secundario para registro manual
        self.btn_create = button(
            self.right_tools,
            text="Crear grupo",
            variant='secondary',
            command=self.create,
            height=CONTROL_HEIGHT,
        )
        self.btn_create.pack(side='right', padx=(SPACING['sm'], 0))

        # Botón terciario de actualización
        self.btn_refresh = button(
            self.right_tools,
            text="Actualizar",
            variant='tertiary',
            command=self.refresh,
            height=CONTROL_HEIGHT,
        )
        self.btn_refresh.pack(side='right', padx=(SPACING['sm'], 0))

        # Botón responsive 'Más acciones' para pantallas angostas
        self.btn_more = button(
            self.right_tools,
            text="Más acciones",
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
        # Se ubica en row=2 solo cuando hay elementos seleccionados
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
            ('code', 'Código Gruplac', 150, 'w'),
            ('name', 'Nombre del grupo', 280, 'w'),
            ('category', 'Categoría', 100, 'center'),
            ('leader', 'Líder', 180, 'w'),
            ('active', 'Estado', 110, 'center'),
        ]
        self.table = DataTable(
            self,
            columns=columns,
            on_selection_change=self._on_table_selection_change,
            on_double_click=self._on_row_double_click,
            on_delete_key=self.delete,
            on_context_menu=self._show_context_menu,
            empty_icon="",
            empty_title="Aún no hay grupos registrados",
            empty_message="Importa un grupo desde MinCiencias (GrupLAC) o crea un nuevo grupo manualmente.",
            empty_action_text="Importar desde MinCiencias",
            empty_action_command=self._on_import_scienti,
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
            text="0 grupos",
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
        self.bind('<Control-n>', lambda e: self._on_shortcut_create())
        self.bind('<Control-N>', lambda e: self._on_shortcut_create())
        self.bind('<Control-f>', lambda e: self._focus_search())
        self.bind('<Control-F>', lambda e: self._focus_search())

    def _focus_search(self):
        """Enfoca y selecciona el texto del buscador."""
        self.search_entry.focus_set()
        self.search_entry.select_range(0, 'end')
        return "break"

    def _on_shortcut_create(self):
        """Dispara la creación o importación desde atajo Ctrl+N."""
        self._on_import_scienti()
        return "break"

    def _on_configure(self, event):
        """Adapta la visibilidad de los botones en pantallas angostas."""
        width = self.winfo_width()
        if width < 760:
            if not self.btn_more.winfo_ismapped():
                self.btn_create.pack_forget()
                self.btn_more.pack(side='right', padx=(SPACING['sm'], 0))
        else:
            if self.btn_more.winfo_ismapped():
                self.btn_more.pack_forget()
                self.btn_create.pack(side='right', padx=(SPACING['sm'], 0))

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
        menu.add_command(label="Crear grupo manual", command=self.create)
        menu.add_command(label="Actualizar lista", command=self.refresh)

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
        self._clear_selection()

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
            menu.add_command(label="Editar", command=self.edit)
        menu.add_command(label=toggle_text, command=self.toggle_active)
        menu.add_separator()
        menu.add_command(label="Eliminar", command=self.delete)

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _on_import_scienti(self):
        """Abre el diálogo modal de importación desde SCIENTI / GrupLAC."""
        app = self.get_app()
        if app and hasattr(app, 'download_scienti'):
            app.download_scienti()

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
        if not self._selected_ids:
            return
        target_id = self._selected_ids[0]
        app = self.get_app()
        if not app:
            return

        grupo = app.grupo_crud.read(target_id)
        if not grupo:
            messagebox.showerror("Error", "No se encontró el grupo seleccionado.")
            return

        form = GrupoForm(self, grupo=grupo, on_save=lambda data: self._on_save_edit(target_id, data))
        form.grab_set()

    def _on_save_edit(self, target_id: int, data: dict):
        """Aplica y guarda los cambios del grupo en edición."""
        app = self.get_app()
        if not app:
            return
        try:
            app.grupo_crud.update(target_id, **data)
            app.save_data()
            self.load_data()
            if hasattr(app, 'load_tabs_data'):
                app.load_tabs_data()
            messagebox.showinfo("Éxito", "Grupo actualizado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el grupo: {e}")

    def toggle_active(self):
        """Alterna el estado (Activar / Desactivar) de los grupos seleccionados."""
        if not self._selected_ids:
            return
        app = self.get_app()
        if not app:
            return

        # Si están activos se desactivan, de lo contrario se activan
        should_activate = not self.table.are_selected_active()
        action_word = "activado" if should_activate else "desactivado"

        try:
            for gid in self._selected_ids:
                if should_activate:
                    app.grupo_crud.activate(gid)
                else:
                    app.grupo_crud.deactivate(gid)

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
            for gid in self._selected_ids:
                if is_active:
                    app.grupo_crud.activate(gid)
                else:
                    app.grupo_crud.deactivate(gid)
            app.save_data()
            self.load_data()
            if hasattr(app, 'load_tabs_data'):
                app.load_tabs_data()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cambiar estado: {e}")

    def delete(self):
        """Elimina físicamente los grupos seleccionados tras confirmación modal."""
        if not self._selected_ids:
            return
        app = self.get_app()
        if not app:
            return

        count = len(self._selected_ids)
        plural = "s" if count != 1 else ""
        confirma = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro de eliminar {count} grupo{plural} seleccionado{plural}?\n\nEsta acción no se puede deshacer.",
            icon='warning',
        )
        if not confirma:
            return

        try:
            deleted_count = 0
            for gid in list(self._selected_ids):
                if app.grupo_crud.delete(gid):
                    deleted_count += 1

            app.save_data()
            self.load_data()
            if hasattr(app, 'load_tabs_data'):
                app.load_tabs_data()

            messagebox.showinfo(
                "Eliminación completada",
                f"Se ha{'n' if deleted_count != 1 else ''} eliminado {deleted_count} grupo{'s' if deleted_count != 1 else ''} correctamente.",
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar grupos: {e}")

    def refresh(self):
        """Actualiza manualmente la información del listado."""
        self.load_data()
