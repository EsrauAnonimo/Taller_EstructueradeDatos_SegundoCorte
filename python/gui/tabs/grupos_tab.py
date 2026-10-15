# -*- coding: utf-8 -*-
"""Pestaña de gestión de Grupos de Investigación refactorizada con TablaCRUD."""

from typing import Optional, List, Any
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from gui.styles import (
    COLORS,
    RADIUS,
    SPACING,
    font,
    boton_primario,
    boton_secundario,
)
from gui.widgets.tabla_crud import TablaCRUD
from gui.forms.grupo_form import GrupoForm
from entidades.grupo import Grupo


class GrupoDetailModal(ctk.CTkToplevel):
    """Modal para visualizar la información detallada de un grupo y su plan de trabajo completo."""

    def __init__(self, parent, grupo: Any):
        super().__init__(parent)
        self.parent = parent
        self.grupo = grupo

        self.title("Detalle del grupo de investigación")
        self.geometry("560x520")
        self.minsize(500, 460)
        self.configure(fg_color=COLORS['bg'])

        self.transient(parent)
        self.grab_set()
        self.bind('<Escape>', lambda e: self.destroy())
        self.bind('<Return>', lambda e: self.destroy())

        self._center_window(560, 520)
        self._build_ui()

    def _center_window(self, width: int, height: int):
        """Centra la ventana modal sobre su ventana contenedora."""
        self.update_idletasks()
        try:
            pw = self.parent.winfo_width()
            ph = self.parent.winfo_height()
            px = self.parent.winfo_rootx()
            py = self.parent.winfo_rooty()
            x = px + max(0, (pw - width) // 2)
            y = py + max(0, (ph - height) // 2)
            self.geometry(f"{width}x{height}+{x}+{y}")
        except Exception:
            self.geometry(f"{width}x{height}")

    def _build_ui(self):
        """Construye los componentes visuales del diálogo."""
        card = ctk.CTkFrame(
            self,
            fg_color=COLORS['surface'],
            corner_radius=RADIUS['card'],
            border_width=1,
            border_color=COLORS['border'],
        )
        card.pack(fill='both', expand=True, padx=SPACING['md'], pady=SPACING['md'])

        # Encabezado
        header = ctk.CTkFrame(card, fg_color='transparent')
        header.pack(fill='x', padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']))

        lbl_title = ctk.CTkLabel(
            header,
            text="Detalle del grupo de investigación",
            font=font('title'),
            text_color=COLORS['ink'],
            anchor='w',
        )
        lbl_title.pack(fill='x', anchor='w')

        nombre = getattr(self.grupo, 'nombre', '') or getattr(self.grupo, 'name', '') or 'Sin nombre'
        lbl_sub = ctk.CTkLabel(
            header,
            text=str(nombre),
            font=font('body_bold'),
            text_color=COLORS['accent'],
            anchor='w',
            wraplength=480,
            justify='left',
        )
        lbl_sub.pack(fill='x', anchor='w', pady=(2, 0))

        # Divisor
        sep = ctk.CTkFrame(card, height=1, fg_color=COLORS['border'], corner_radius=0)
        sep.pack(fill='x', padx=SPACING['lg'], pady=SPACING['sm'])

        # Tarjeta de metadatos básicos
        info_frame = ctk.CTkFrame(card, fg_color=COLORS['surface_subtle'], corner_radius=RADIUS['control'])
        info_frame.pack(fill='x', padx=SPACING['lg'], pady=(0, SPACING['sm']))
        info_frame.grid_columnconfigure((1, 3), weight=1)

        code = getattr(self.grupo, 'codigo_gruplac', '') or getattr(self.grupo, 'code', '') or '-'
        cat = getattr(self.grupo, 'categoria', '') or getattr(self.grupo, 'category', '') or '-'
        lider = getattr(self.grupo, 'lider', '') or getattr(self.grupo, 'leader', '') or '-'
        active = getattr(self.grupo, 'activo', getattr(self.grupo, 'active', True))
        status_text = "● Activo" if active else "● Inactivo"
        status_color = COLORS['success'] if active else COLORS['muted']

        fields = [
            ("Código Gruplac:", str(code), 0, 0),
            ("Categoría:", str(cat), 0, 2),
            ("Líder:", str(lider), 1, 0),
            ("Estado:", status_text, 1, 2),
        ]

        for lbl, val, r, c in fields:
            ctk.CTkLabel(
                info_frame,
                text=lbl,
                font=font('small'),
                text_color=COLORS['muted'],
                anchor='w',
            ).grid(row=r, column=c, sticky='w', padx=(SPACING['md'], 4), pady=4)

            val_color = status_color if lbl == "Estado:" else COLORS['ink']
            ctk.CTkLabel(
                info_frame,
                text=val,
                font=font('body'),
                text_color=val_color,
                anchor='w',
            ).grid(row=r, column=c+1, sticky='w', padx=(0, SPACING['md']), pady=4)

        # Sección Plan
        sec_label = ctk.CTkLabel(
            card,
            text="PLAN DEL GRUPO (LÍNEAS DE INVESTIGACIÓN / OBJETIVOS)",
            font=font('badge'),
            text_color=COLORS['accent'],
            anchor='w',
        )
        sec_label.pack(fill='x', padx=SPACING['lg'], pady=(SPACING['sm'], 4))

        # Cuadro de texto multilínea con el plan completo
        plan_text = getattr(self.grupo, 'plan', '') or ""
        txt_box = ctk.CTkTextbox(
            card,
            font=font('body'),
            corner_radius=RADIUS['control'],
            border_width=1,
            border_color=COLORS['border'],
            fg_color=COLORS['surface'],
            text_color=COLORS['ink'],
            wrap='word',
        )
        txt_box.pack(fill='both', expand=True, padx=SPACING['lg'], pady=(0, SPACING['md']))

        display_plan = str(plan_text).strip() if str(plan_text).strip() else "(El grupo no tiene un plan de trabajo registrado actualmente.)"
        txt_box.insert("1.0", display_plan)
        txt_box.configure(state='disabled')

        # Pie con botón Cerrar
        footer = ctk.CTkFrame(card, fg_color='transparent')
        footer.pack(fill='x', padx=SPACING['lg'], pady=(0, SPACING['md']))

        btn_close = boton_primario(
            footer,
            text="Cerrar",
            command=self.destroy,
            width=100,
            height=32,
        )
        btn_close.pack(side='right')
        btn_close.focus_set()


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
            ('id', 'ID', 60, 'center'),
            ('code', 'Código Gruplac', 130, 'w'),
            ('name', 'Nombre del grupo', 230, 'w'),
            ('category', 'Categoría', 90, 'center'),
            ('leader', 'Líder', 160, 'w'),
            ('plan', 'Plan', 240, 'w'),
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

        # --- 3. Botón Deshacer (fuera de TablaCRUD, en fila debajo del encabezado) ---
        self._build_undo_button()

        # --- 4. Botón Ver detalle ---
        self._build_detail_button()

        # Vincular eventos de selección para actualizar el botón de detalle
        self.table.tree.bind('<<TreeviewSelect>>', lambda e: self._update_detail_button_state(), add='+')
        self.table.tree.bind('<ButtonRelease-1>', lambda e: self._update_detail_button_state(), add='+')
        self.table.tree.bind('<KeyRelease>', lambda e: self._update_detail_button_state(), add='+')

        self.load_data()

    def _build_undo_button(self):
        """Crea el botón '↶ Deshacer' en la zona derecha del toolbar de TablaCRUD."""
        from gui.styles import COLORS, RADIUS, font, SPACING
        # right_tools es el contenedor del toolbar donde viven 'Crear' y 'Actualizar'
        parent = getattr(self.table, 'right_tools', None) or self.header_frame

        self.btn_undo = ctk.CTkButton(
            parent,
            text="↶ Deshacer",
            width=110,
            height=32,
            corner_radius=RADIUS['control'],
            fg_color=COLORS.get('warning', '#F59E0B'),
            hover_color=COLORS.get('warning_hover', '#D97706'),
            text_color='#FFFFFF',
            font=font('body_bold'),
            state='disabled',
            command=self._on_undo,
        )
        self.btn_undo.pack(side='right', padx=(SPACING['sm'], 0))

    def _build_detail_button(self):
        """Crea el botón 'Ver detalle' en la barra contextual de TablaCRUD."""
        parent = getattr(self.table, 'ctx_right', None)
        if parent:
            self.btn_detail = boton_secundario(
                parent,
                text="Ver detalle",
                command=self.show_detail,
                height=30,
            )
            try:
                self.btn_detail.pack(side='left', padx=(0, SPACING['xs']), before=self.table.btn_edit)
            except Exception:
                self.btn_detail.pack(side='left', padx=(0, SPACING['xs']))
            self.btn_detail.configure(state='disabled')

    def _update_detail_button_state(self):
        """Actualiza el estado habilitado del botón Ver detalle según la fila seleccionada."""
        if hasattr(self, 'btn_detail'):
            has_selection = len(self.table.get_selected_ids()) == 1
            self.btn_detail.configure(state='normal' if has_selection else 'disabled')

    def show_detail(self, item_id: Optional[str] = None):
        """Abre un diálogo modal con la información completa y el plan del grupo."""
        target_id_str = item_id or self.table.get_selected_id()
        if not target_id_str:
            messagebox.showinfo("Información", "Selecciona un grupo para ver su detalle.")
            return

        target_id = int(target_id_str) if target_id_str.isdigit() else target_id_str

        app = self.get_app()
        grupo = None
        if app and hasattr(app, 'grupo_crud'):
            grupo = app.grupo_crud.get_by_id(target_id)
        if not grupo and hasattr(self, '_all_grupos'):
            for item in self._all_grupos:
                if str(getattr(item, 'id', '')) == str(target_id):
                    grupo = item
                    break

        if not grupo:
            messagebox.showerror("Error", "No se encontró el grupo seleccionado.")
            return

        GrupoDetailModal(self, grupo=grupo)

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
            name_raw = getattr(g, 'nombre', '') or getattr(g, 'name', '')
            clean_name = " ".join(str(name_raw).split())
            name = f"{clean_name[:40]}..." if len(clean_name) > 40 else clean_name
            cat = getattr(g, 'categoria', '') or getattr(g, 'category', '')
            leader = getattr(g, 'lider', '') or getattr(g, 'leader', '')
            plan_raw = getattr(g, 'plan', '') or ''
            clean_plan = " ".join(str(plan_raw).split())
            if len(clean_plan) > 40:
                truncated_plan = f"{clean_plan[:40]}..."
            else:
                truncated_plan = clean_plan
            active = getattr(g, 'activo', getattr(g, 'active', True))

            rows.append({
                'id': str(gid) if gid is not None else '',
                'values': (
                    str(gid) if gid is not None else '',
                    str(code),
                    str(name),
                    str(cat),
                    str(leader),
                    str(truncated_plan),
                    "● Activo" if active else "● Inactivo",
                ),
                'is_active': bool(active),
                'raw': g,
            })

        self.table.set_rows(rows)
        self._update_detail_button_state()

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
                plan=data.get('plan', ''),
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

        grupo = app.grupo_crud.get_by_id(target_id) if hasattr(app.grupo_crud, 'get_by_id') else getattr(app.grupo_crud, 'read', lambda _: None)(target_id)
        if not grupo and hasattr(self, '_all_grupos'):
            for item in self._all_grupos:
                if getattr(item, 'id', None) == target_id:
                    grupo = item
                    break
        if not grupo:
            messagebox.showerror("Error", "No se encontró el grupo seleccionado.")
            return

        form = GrupoForm(self, app=app, grupo=grupo, on_save=lambda data: self._on_save_edit(target_id, data))
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

    def _on_undo(self):
        """Delega la acción de deshacer a la instancia central de App."""
        app = self.get_app()
        if app and hasattr(app, 'undo_delete'):
            app.undo_delete()

    def delete(self, selected_ids: Optional[List[str]] = None):
        """Elimina los grupos seleccionados tras la confirmación realizada por el modal,
        apilando cada objeto en la pila de deshacer antes de borrarlo físicamente."""
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

                # ── Capturar snapshot ANTES de eliminar ────────────────────────────
                grupo_obj = app.grupo_crud.get_by_id(gid)
                if grupo_obj is None:
                    continue

                # Recopilar investigadores y sus productos (relaciones multilista)
                invs_snapshot = []
                try:
                    inv_list = app.inv_crud.list_by_group(gid)
                    for inv in inv_list:
                        ced = getattr(inv, 'cedula', None)
                        prods = []
                        if ced:
                            try:
                                prods = list(app.prod_crud.list_by_investigador(ced))
                            except Exception:
                                pass
                        invs_snapshot.append({'investigador': inv, 'productos': prods})
                except Exception:
                    pass

                posicion = {
                    'grupo_id': gid,
                    'investigadores': invs_snapshot,
                }

                # Apilar en la pila de deshacer
                app.push_undo('grupo', grupo_obj, posicion)

                # Eliminar físicamente
                if app.grupo_crud.delete(gid):
                    deleted_count += 1

            app.save_data()
            self.load_data()
            if hasattr(app, 'load_tabs_data'):
                app.load_tabs_data()

            messagebox.showinfo(
                "Eliminación completada",
                f"Se ha{'n' if deleted_count != 1 else ''} eliminado {deleted_count} "
                f"grupo{'s' if deleted_count != 1 else ''} correctamente.\n"
                f"Puede deshacer con Ctrl+Z o el botón Deshacer.",
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar grupos: {e}")

    def refresh(self):
        """Actualiza manualmente la información del listado."""
        self.load_data()
