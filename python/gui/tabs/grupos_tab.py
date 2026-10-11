# -*- coding: utf-8 -*-
"""Pestaña de gestión de Grupos de Investigación refactorizada con TablaCRUD."""

from typing import Optional, List
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from gui.styles import (
    COLORS,
    SPACING,
    font,
)
from gui.widgets.tabla_crud import TablaCRUD
from gui.forms.grupo_form import GrupoForm
from entidades.grupo import Grupo


class GruposTab(ctk.CTkFrame):
    """Pestaña para listar, buscar, crear, editar y eliminar grupos de investigación
    utilizando el componente estandarizado TablaCRUD."""

    def __init__(self, master, app=None):
        super().__init__(master, fg_color='transparent')
        self._app_ref = app
        self.pack(fill='both', expand=True)

        self._all_grupos: List = []

        # Configuración del layout vertical
        # Row 0: Encabezado (título + subtítulo)
        # Row 1: TablaCRUD (barra de herramientas + barra contextual + tabla + pie)
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

        # --- 2. Tabla CRUD Reutilizable ---
        columns = [
            ('id', 'ID', 70, 'center'),
            ('code', 'Código Gruplac', 150, 'w'),
            ('name', 'Nombre del grupo', 280, 'w'),
            ('category', 'Categoría', 100, 'center'),
            ('leader', 'Líder', 180, 'w'),
            ('active', 'Estado', 110, 'center'),
        ]

        self.table = TablaCRUD(
            self,
            columns=columns,
            on_editar=self.edit,
            on_toggle_estado=self.toggle_active,
            on_eliminar=self.delete,
            on_crear=self.create,
            on_actualizar=self.refresh,
            entity_name="grupo",
            entity_name_plural="grupos",
            create_button_text="Crear grupo",
            search_placeholder="Buscar por código, nombre o líder...",
            extra_action_button={
                'text': "Descargar del SCIENTI",
                'command': self._on_import_scienti,
                'variant': 'secondary',
            },
            empty_icon="👥",
            empty_title="Aún no hay grupos",
            empty_message="Descarga datos del SCIENTI o crea un nuevo grupo para comenzar.",
            empty_action_text="Descargar del SCIENTI",
            empty_action_command=self._on_import_scienti,
        )
        self.table.grid(
            row=1,
            column=0,
            sticky='nsew',
            padx=SPACING['lg'],
            pady=(0, SPACING['lg']),
        )

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
        """Obtiene todos los grupos de la estructura de multilista o CRUD."""
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
        """Recarga los datos de los grupos y los entrega al componente TablaCRUD."""
        self._all_grupos = self._get_all_raw_groups()
        rows = []
        for g in self._all_grupos:
            gid = getattr(g, 'id', None)
            code = getattr(g, 'codigo_gruplac', '') or getattr(g, 'code', '')
            name = getattr(g, 'nombre', '') or getattr(g, 'name', '')
            cat = getattr(g, 'categoria', '') or getattr(g, 'category', '')
            leader = getattr(g, 'lider', '') or getattr(g, 'leader', '')
            active = getattr(g, 'activo', getattr(g, 'active', True))

            rows.append({
                'id': str(gid) if gid is not None else '',
                'values': (
                    str(gid) if gid is not None else '',
                    str(code),
                    str(name),
                    str(cat),
                    str(leader),
                    "● Activo" if active else "● Inactivo",
                ),
                'is_active': bool(active),
                'raw': g,
            })

        self.table.set_rows(rows)

    def _on_import_scienti(self):
        """Abre la descarga directa o modal de importación desde SCIENTI."""
        app = self.get_app()
        if app and hasattr(app, 'download_scienti'):
            app.download_scienti()

    def create(self):
        """Abre el formulario modal para registrar un nuevo grupo."""
        form = GrupoForm(self, on_save=self._on_save_create)
        form.grab_set()

    def _on_save_create(self, data: dict):
        """Persiste el nuevo grupo mediante la capa CRUD."""
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

    def edit(self, item_id: Optional[str] = None):
        """Abre el formulario para editar el grupo seleccionado."""
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

        grupo = app.grupo_crud.read(target_id)
        if not grupo:
            messagebox.showerror("Error", "No se encontró el grupo seleccionado.")
            return

        form = GrupoForm(self, grupo=grupo, on_save=lambda data: self._on_save_edit(target_id, data))
        form.grab_set()

    def _on_save_edit(self, target_id: Any, data: dict):
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

    def toggle_active(self, selected_ids: Optional[List[str]] = None, should_activate: Optional[bool] = None):
        """Alterna el estado (Activar / Desactivar) de los grupos seleccionados."""
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
                gid = int(sid) if sid.isdigit() else sid
                if should_activate:
                    app.grupo_crud.activate(gid)
                else:
                    app.grupo_crud.deactivate(gid)

            app.save_data()
            self.load_data()
            if hasattr(app, 'load_tabs_data'):
                app.load_tabs_data()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cambiar estado de grupos: {e}")

    def delete(self, selected_ids: Optional[List[str]] = None):
        """Elimina los grupos seleccionados tras la confirmación realizada por el modal."""
        ids = selected_ids or self.table.get_selected_ids()
        if not ids:
            return
        app = self.get_app()
        if not app:
            return

        try:
            deleted_count = 0
            for sid in ids:
                gid = int(sid) if sid.isdigit() else sid
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
