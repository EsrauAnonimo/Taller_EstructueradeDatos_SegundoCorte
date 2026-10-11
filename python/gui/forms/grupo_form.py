# -*- coding: utf-8 -*-
"""Formulario modal para creación y edición de Grupo de Investigación con sub-tablas y plan."""

from typing import Optional, Dict, Any, Callable, List
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk

from gui.forms.base_form import FormularioBase
from gui.styles import (
    COLORS,
    RADIUS,
    SPACING,
    font,
    boton_primario,
    boton_secundario,
    boton_peligro,
    combo,
    configurar_treeview,
    apply_treeview_tags,
)


class GrupoForm(FormularioBase):
    """Modal para captura y modificación de Grupo de Investigación con gestión de integrantes y productos."""

    def __init__(
        self,
        master,
        data: Optional[Dict[str, Any]] = None,
        grupo: Optional[Any] = None,
        on_save: Optional[Callable[[Dict[str, Any]], None]] = None,
        app: Optional[Any] = None,
        **kwargs,
    ):
        initial_data = {}
        if data:
            initial_data = dict(data)
        elif grupo is not None:
            if hasattr(grupo, 'to_dict'):
                initial_data = grupo.to_dict()
            elif hasattr(grupo, '__dict__'):
                initial_data = dict(grupo.__dict__)

        is_edit = bool(initial_data)
        title_text = "Editar grupo de investigación" if is_edit else "Crear grupo de investigación"
        sub_text = (
            "Modifica los datos del grupo académico, integrantes y productos asociados"
            if is_edit
            else "Registra un nuevo grupo académico en el sistema"
        )

        width = 660 if is_edit else 520
        height = 760 if is_edit else 640

        super().__init__(
            master=master,
            title=title_text,
            subtitle=sub_text,
            width=width,
            height=height,
            on_save=on_save,
            data=initial_data,
            app=app,
            **kwargs,
        )

        self.is_edit = is_edit
        self.grupo_id = initial_data.get('id') or initial_data.get('codigo_gruplac') or initial_data.get('code')
        self._build_fields()

    def _build_fields(self):
        """Construye las secciones y campos del formulario."""
        d = self._initial_data

        # --- Sección 1: Información del Grupo ---
        self.add_section("Información del grupo")

        code_val = d.get('code') or d.get('codigo_gruplac', '')
        self.add_text_field(
            key='code',
            label_text="Código Gruplac",
            placeholder="Ej. COL0008234",
            required=True,
            initial_value=str(code_val),
        )

        name_val = d.get('name') or d.get('nombre', '')
        self.add_text_field(
            key='name',
            label_text="Nombre del grupo",
            placeholder="Nombre de la línea o grupo de investigación",
            required=True,
            initial_value=str(name_val),
        )

        cat_val = d.get('category') or d.get('categoria', '')
        self.add_text_field(
            key='category',
            label_text="Categoría",
            placeholder="Ej. A1, A, B, C o Reconocido",
            required=False,
            initial_value=str(cat_val),
        )

        # --- Sección 2: Liderazgo, Plan y Estado ---
        self.add_section("Liderazgo, plan de trabajo y estado")

        leader_val = d.get('leader') or d.get('lider', '')
        self.add_text_field(
            key='leader',
            label_text="Líder del grupo",
            placeholder="Nombre completo del líder o director",
            required=True,
            initial_value=str(leader_val),
        )

        plan_val = d.get('plan', '')
        self.add_textarea_field(
            key='plan',
            label_text="Plan del grupo (multilínea)",
            placeholder="Objetivos, metas estratégicas y plan de desarrollo del grupo...",
            initial_value=str(plan_val),
            height=80,
            required=False,
        )

        active_val = d.get('active', d.get('activo', True))
        self.add_checkbox_field(
            key='active',
            label_text="Grupo activo en el sistema",
            initial_value=bool(active_val),
        )

        # --- Sub-tablas exclusivas de edición: Integrantes y Productos ---
        if self.is_edit and self.grupo_id:
            self._build_integrantes_section()
            self._build_productos_section()

    def _build_integrantes_section(self):
        """Construye la sub-tabla interactiva de integrantes del grupo (Multilista)."""
        self.add_section("Integrantes del grupo (Multilista)")

        container = ctk.CTkFrame(self.body, fg_color='transparent')
        container.pack(fill='x', padx=SPACING['sm'], pady=(0, SPACING['sm']))

        # Barra superior con combo para agregar integrante y botón '+ Agregar'
        action_bar = ctk.CTkFrame(container, fg_color='transparent')
        action_bar.pack(fill='x', pady=(0, SPACING['xs']))

        lbl_add = ctk.CTkLabel(
            action_bar,
            text="Vincular integrante:",
            font=font('small'),
            text_color=COLORS['ink'],
        )
        lbl_add.pack(side='left', padx=(0, SPACING['xs']))

        self._available_inv_map = {}
        options = self._get_available_researchers_options()

        self._selected_inv_var = ctk.StringVar(value=options[0] if options else "(Sin investigadores)")
        self._add_inv_combo = combo(
            action_bar,
            values=options if options else ["(Sin investigadores)"],
            variable=self._selected_inv_var,
            width=260,
        )
        self._add_inv_combo.pack(side='left', padx=(0, SPACING['xs']))

        btn_add = boton_primario(
            action_bar,
            text="+ Agregar",
            command=self._on_add_member,
            height=32,
            width=80,
        )
        btn_add.pack(side='left')

        # Tabla Treeview para integrantes
        table_frame = ctk.CTkFrame(
            container,
            fg_color=COLORS['surface'],
            corner_radius=RADIUS['control'],
            border_width=1,
            border_color=COLORS['border'],
        )
        table_frame.pack(fill='x', pady=(0, SPACING['xs']))

        configurar_treeview(self)
        self.tree_members = ttk.Treeview(
            table_frame,
            columns=('cedula', 'nombres', 'email'),
            show='headings',
            style='Pea.Treeview',
            height=5,
            selectmode='browse',
        )
        apply_treeview_tags(self.tree_members)

        self.tree_members.heading('cedula', text='Cédula')
        self.tree_members.heading('nombres', text='Nombres y Apellidos')
        self.tree_members.heading('email', text='Correo Electrónico')

        self.tree_members.column('cedula', width=120, anchor='center')
        self.tree_members.column('nombres', width=260, anchor='w')
        self.tree_members.column('email', width=200, anchor='w')

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient='vertical',
            style='Pea.Vertical.TScrollbar',
            command=self.tree_members.yview,
        )
        self.tree_members.configure(yscrollcommand=scrollbar.set)

        self.tree_members.pack(side='left', fill='x', expand=True, padx=(1, 0), pady=1)
        scrollbar.pack(side='right', fill='y', padx=(0, 1), pady=1)

        # Botón para quitar integrante seleccionado
        btn_remove = boton_peligro(
            container,
            text="- Quitar integrante seleccionado",
            command=self._on_remove_member,
            height=30,
        )
        btn_remove.pack(anchor='w', pady=(2, 0))

        # Cargar datos iniciales de integrantes
        self._refresh_members_table()

    def _get_available_researchers_options(self) -> List[str]:
        """Obtiene la lista de investigadores registrados para el combo."""
        app = self.resolve_app()
        options = []
        self._available_inv_map = {}
        if app and hasattr(app, 'inv_crud'):
            try:
                all_invs = app.inv_crud.list_all()
                for inv in all_invs:
                    ced = str(getattr(inv, 'cedula', None) or getattr(inv, 'id', None) or '')
                    nom = f"{getattr(inv, 'nombres', '')} {getattr(inv, 'apellidos', '')}".strip() or getattr(inv, 'name', '')
                    label = f"{ced} - {nom}" if ced else nom
                    options.append(label)
                    self._available_inv_map[label] = inv
            except Exception:
                pass
        return options or ["(Sin investigadores disponibles)"]

    def _refresh_members_table(self):
        """Recarga los integrantes del grupo desde la Multilista."""
        if not hasattr(self, 'tree_members'):
            return
        for item in self.tree_members.get_children():
            self.tree_members.delete(item)

        app = self.resolve_app()
        if not app or not hasattr(app, 'multilista'):
            return

        try:
            members = app.multilista.get_investigadores_by_grupo(self.grupo_id)
            for idx, inv in enumerate(members):
                ced = str(getattr(inv, 'cedula', None) or getattr(inv, 'id', None) or '')
                nom = f"{getattr(inv, 'nombres', '')} {getattr(inv, 'apellidos', '')}".strip() or getattr(inv, 'name', '')
                email = getattr(inv, 'email', '')
                tag = 'even' if idx % 2 == 0 else 'odd'
                self.tree_members.insert('', 'end', iid=ced, values=(ced, nom, email), tags=(tag,))
        except Exception as e:
            print("Error cargando integrantes del grupo:", e)

    def _on_add_member(self):
        """Agrega el integrante seleccionado del combo al grupo en la Multilista."""
        app = self.resolve_app()
        if not app:
            return

        selected_label = self._selected_inv_var.get()
        inv_obj = self._available_inv_map.get(selected_label)
        if not inv_obj:
            messagebox.showwarning("Selección requerida", "Selecciona un investigador del combo para agregarlo.")
            return

        ced = str(getattr(inv_obj, 'cedula', None) or getattr(inv_obj, 'id', None) or '')
        try:
            # Vincular en la Multilista
            app.multilista.add_investigador_to_group(self.grupo_id, inv_obj)
            app.save_data(silent=True)
            self._refresh_members_table()
            self._refresh_products_table()
            if hasattr(app, 'load_tabs_data'):
                app.load_tabs_data()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo vincular el investigador: {e}")

    def _on_remove_member(self):
        """Quita el integrante seleccionado de la tabla del grupo en la Multilista."""
        selected = self.tree_members.selection()
        if not selected:
            messagebox.showinfo("Información", "Selecciona un integrante de la tabla para desvincularlo del grupo.")
            return

        cedula_to_remove = selected[0]
        app = self.resolve_app()
        if not app:
            return

        try:
            # Desvincular de la Multilista
            app.multilista.remove_investigador_from_group(self.grupo_id, cedula_to_remove)
            app.save_data(silent=True)
            self._refresh_members_table()
            self._refresh_products_table()
            if hasattr(app, 'load_tabs_data'):
                app.load_tabs_data()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo desvincular el integrante: {e}")

    def _build_productos_section(self):
        """Construye la sub-tabla de productos del grupo (solo lectura, con categoría y año)."""
        self.add_section("Productos del grupo (solo lectura)")

        container = ctk.CTkFrame(self.body, fg_color='transparent')
        container.pack(fill='x', padx=SPACING['sm'], pady=(0, SPACING['sm']))

        lbl_info = ctk.CTkLabel(
            container,
            text="📌 Producción científica registrada por los integrantes del grupo (solo lectura):",
            font=font('small'),
            text_color=COLORS['muted'],
            anchor='w',
        )
        lbl_info.pack(fill='x', pady=(0, 4))

        table_frame = ctk.CTkFrame(
            container,
            fg_color=COLORS['surface'],
            corner_radius=RADIUS['control'],
            border_width=1,
            border_color=COLORS['border'],
        )
        table_frame.pack(fill='x')

        configurar_treeview(self)
        self.tree_prods = ttk.Treeview(
            table_frame,
            columns=('id', 'titulo', 'tipo', 'categoria', 'anio'),
            show='headings',
            style='Pea.Treeview',
            height=5,
            selectmode='browse',
        )
        apply_treeview_tags(self.tree_prods)

        self.tree_prods.heading('id', text='ID')
        self.tree_prods.heading('titulo', text='Título de la publicación o desarrollo')
        self.tree_prods.heading('tipo', text='Tipo')
        self.tree_prods.heading('categoria', text='Categoría')
        self.tree_prods.heading('anio', text='Año')

        self.tree_prods.column('id', width=65, anchor='center')
        self.tree_prods.column('titulo', width=240, anchor='w')
        self.tree_prods.column('tipo', width=110, anchor='w')
        self.tree_prods.column('categoria', width=130, anchor='w')
        self.tree_prods.column('anio', width=55, anchor='center')

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient='vertical',
            style='Pea.Vertical.TScrollbar',
            command=self.tree_prods.yview,
        )
        self.tree_prods.configure(yscrollcommand=scrollbar.set)

        self.tree_prods.pack(side='left', fill='x', expand=True, padx=(1, 0), pady=1)
        scrollbar.pack(side='right', fill='y', padx=(0, 1), pady=1)

        # Cargar productos iniciales del grupo
        self._refresh_products_table()

    def _refresh_products_table(self):
        """Recarga los productos del grupo desde la Multilista."""
        if not hasattr(self, 'tree_prods'):
            return
        for item in self.tree_prods.get_children():
            self.tree_prods.delete(item)

        app = self.resolve_app()
        if not app or not hasattr(app, 'multilista'):
            return

        try:
            prods = app.multilista.get_productos_by_grupo(self.grupo_id)
            for idx, p in enumerate(prods):
                pid = str(getattr(p, 'id', '') or '')
                tit = str(getattr(p, 'titulo', '') or getattr(p, 'title', '') or '')
                ptype = str(getattr(p, 'tipo', '') or getattr(p, 'type', '') or '')
                cat = str(getattr(p, 'categoria', getattr(p, 'categoria_producto', 'Nuevo conocimiento')) or 'Nuevo conocimiento')
                anio = str(getattr(p, 'anio', 0) or getattr(p, 'year', 0) or '')
                tag = 'even' if idx % 2 == 0 else 'odd'
                self.tree_prods.insert('', 'end', iid=f"grp_prod_{idx}_{pid}", values=(pid, tit, ptype, cat, anio), tags=(tag,))
        except Exception as e:
            print("Error cargando productos del grupo:", e)

    def get_data(self) -> Dict[str, Any]:
        """Extrae el diccionario normalizado con alias completos para la capa CRUD."""
        raw = super().get_data()
        code = raw.get('code', '').strip()
        name = raw.get('name', '').strip()
        cat = raw.get('category', '').strip()
        leader = raw.get('leader', '').strip()
        plan = raw.get('plan', '').strip()
        active = bool(raw.get('active', True))

        return {
            'code': code,
            'codigo_gruplac': code,
            'name': name,
            'nombre': name,
            'category': cat,
            'categoria': cat,
            'leader': leader,
            'lider': leader,
            'plan': plan,
            'active': active,
            'activo': active,
        }