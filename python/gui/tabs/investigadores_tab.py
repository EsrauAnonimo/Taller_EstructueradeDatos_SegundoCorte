# -*- coding: utf-8 -*-
"""Pestaña de gestión de Investigadores refactorizada con TablaCRUD."""

from typing import Optional, List, Any
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from gui.styles import (
    COLORS,
    SPACING,
    font,
)
from gui.widgets.tabla_crud import TablaCRUD
from gui.forms.investigador_form import InvestigadorForm
from entidades.investigador import Investigador


class InvestigadoresTab(ctk.CTkFrame):
    """Pestaña para listar, buscar, crear, editar y eliminar investigadores
    utilizando el componente estandarizado TablaCRUD."""

    def __init__(self, master, app=None):
        super().__init__(master, fg_color='transparent')
        self._app_ref = app
        self.pack(fill='both', expand=True)

        self._all_investigadores: List = []

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

        # --- 2. Tabla CRUD Reutilizable ---
        columns = [
            ('cedula', 'Cédula / ID', 120, 'center'),
            ('nombres', 'Nombres y Apellidos', 250, 'w'),
            ('email', 'Correo electrónico', 220, 'w'),
            ('grupo_id', 'Grupo ID', 100, 'center'),
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
            entity_name="investigador",
            entity_name_plural="investigadores",
            create_button_text="Crear investigador",
            search_placeholder="Buscar por cédula, nombre o correo...",
            empty_icon="👥",
            empty_title="No hay investigadores registrados",
            empty_message="Registra investigadores manualmente o importa un grupo desde MinCiencias para indexarlos automáticamente.",
            empty_action_text="Crear investigador",
            empty_action_command=self.create,
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
            if hasattr(curr, 'inv_crud'):
                self._app_ref = curr
                return curr
            curr = getattr(curr, 'master', None)
        return None

    def _get_all_raw_investigadores(self) -> List:
        """Obtiene todos los investigadores de la estructura de multilista o CRUD."""
        app = self.get_app()
        if app is None or not hasattr(app, 'multilista'):
            return []
        invs = []
        try:
            curr_g = app.multilista.head_group
            while curr_g is not None:
                curr_i = curr_g.sublist
                while curr_i is not None:
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
        """Recarga los datos de los investigadores y los entrega al componente TablaCRUD."""
        self._all_investigadores = self._get_all_raw_investigadores()
        rows = []
        for inv in self._all_investigadores:
            ced = getattr(inv, 'cedula', None) or getattr(inv, 'id', '')
            nombres = getattr(inv, 'nombres', '') or getattr(inv, 'name', '')
            email = getattr(inv, 'email', '') or getattr(inv, 'correo', '')
            gid = getattr(inv, 'grupo_id', '') or getattr(inv, 'group', '')
            active = getattr(inv, 'activo', getattr(inv, 'active', True))

            rows.append({
                'id': str(ced),
                'values': (
                    str(ced),
                    str(nombres),
                    str(email),
                    str(gid),
                    "● Activo" if active else "● Inactivo",
                ),
                'is_active': bool(active),
                'raw': inv,
            })

        self.table.set_rows(rows)

    def create(self):
        """Abre el formulario modal para registrar un nuevo investigador."""
        app = self.get_app()
        form = InvestigadorForm(self, app=app, on_save=self._on_save_create)
        form.grab_set()

    def _on_save_create(self, data: dict):
        """Persiste el nuevo investigador mediante la capa CRUD."""
        app = self.get_app()
        if not app:
            return
        try:
            nuevo = Investigador(
                cedula=str(data.get('cedula', '')),
                nombres=data.get('nombres') or data.get('name', ''),
                email=data.get('email') or data.get('correo', ''),
                grupo_id=data.get('grupo_id') or data.get('group'),
                activo=data.get('activo', True),
                horas_dedicacion=int(data.get('horas_dedicacion', 0) or 0),
            )
            app.inv_crud.create(nuevo)
            app.save_data()
            self.load_data()
            if hasattr(app, 'load_tabs_data'):
                app.load_tabs_data()
            messagebox.showinfo("Éxito", "Investigador registrado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el investigador: {e}")

    def edit(self, item_id: Optional[str] = None):
        """Abre el formulario para editar el investigador seleccionado."""
        target_cedula = item_id or self.table.get_selected_id()
        if not target_cedula:
            return

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

    def toggle_active(self, selected_ids: Optional[List[str]] = None, should_activate: Optional[bool] = None):
        """Alterna el estado (Activar / Desactivar) de los investigadores seleccionados."""
        ids = selected_ids or self.table.get_selected_ids()
        if not ids:
            return
        app = self.get_app()
        if not app:
            return

        if should_activate is None:
            should_activate = not self.table.are_selected_active()

        try:
            for cid in ids:
                if should_activate:
                    app.inv_crud.activate(cid)
                else:
                    app.inv_crud.deactivate(cid)

            app.save_data()
            self.load_data()
            if hasattr(app, 'load_tabs_data'):
                app.load_tabs_data()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cambiar estado de investigadores: {e}")

    def delete(self, selected_ids: Optional[List[str]] = None):
        """Elimina los investigadores seleccionados tras la confirmación del modal."""
        ids = selected_ids or self.table.get_selected_ids()
        if not ids:
            return
        app = self.get_app()
        if not app:
            return

        try:
            deleted_count = 0
            for cid in ids:
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
