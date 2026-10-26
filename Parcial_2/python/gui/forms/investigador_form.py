# -*- coding: utf-8 -*-
"""Formulario modal para creación y edición de Investigador con sub-tablas de grupos y productos."""

from typing import Optional, Dict, Any, Callable, List
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

from gui.forms.base_form import FormularioBase
from gui.styles import (
    COLORS,
    RADIUS,
    SPACING,
    font,
    configurar_treeview,
    apply_treeview_tags,
)


class InvestigadorForm(FormularioBase):
    """Modal para captura y modificación de Investigador con sub-tablas de sus productos y grupos."""

    def __init__(
        self,
        master,
        data: Optional[Dict[str, Any]] = None,
        investigador: Optional[Any] = None,
        on_save: Optional[Callable[[Dict[str, Any]], None]] = None,
        app: Optional[Any] = None,
        **kwargs,
    ):
        initial_data = {}
        if data:
            initial_data = dict(data)
        elif investigador is not None:
            if hasattr(investigador, 'to_dict'):
                initial_data = investigador.to_dict()
            elif hasattr(investigador, '__dict__'):
                initial_data = dict(investigador.__dict__)

        is_edit = bool(initial_data)
        title_text = "Editar investigador" if is_edit else "Crear investigador"
        sub_text = (
            "Modifica los datos personales, vinculación académica, productos y grupos del investigador"
            if is_edit
            else "Registra un nuevo investigador adscrito a un grupo académico"
        )

        width = 660 if is_edit else 520
        height = 760 if is_edit else 660

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
        self.cedula = str(initial_data.get('cedula') or initial_data.get('id') or '')
        self._build_fields()

    def _build_fields(self):
        """Construye las secciones y campos del formulario."""
        d = self._initial_data

        # --- Sección 1: Datos Personales ---
        self.add_section("Datos personales")

        ced_val = d.get('cedula') or d.get('id', '')
        self.add_text_field(
            key='cedula',
            label_text="Cédula / Identificación",
            placeholder="Ej. 1098765432 (solo números)",
            required=True,
            validator=self.validator_cedula,
            initial_value=str(ced_val) if ced_val else "",
        )

        name_val = d.get('nombres') or d.get('name', '')
        self.add_text_field(
            key='nombres',
            label_text="Nombres y apellidos completos",
            placeholder="Ej. Dra. María González Pérez",
            required=True,
            initial_value=str(name_val),
        )

        email_val = d.get('email', '') or d.get('correo', '')
        self.add_text_field(
            key='email',
            label_text="Correo electrónico institucional",
            placeholder="usuario@institucion.edu.co",
            required=True,
            validator=self.validator_email,
            initial_value=str(email_val),
        )

        # --- Sección 2: Vinculación Académica ---
        self.add_section("Vinculación académica")

        # Combo de Grupo asociado ("código - nombre")
        options, mapping, reverse_mapping = self.get_grupos_combo_data()
        current_group_val = d.get('grupo_id') or d.get('group', None)
        initial_combo_val = None
        if current_group_val is not None:
            initial_combo_val = reverse_mapping.get(current_group_val) or reverse_mapping.get(str(current_group_val))

        self.add_combo_field(
            key='grupo_id',
            label_text="Grupo de investigación principal",
            options=options,
            required=True,
            initial_value=initial_combo_val,
            mapping=mapping,
            reverse_mapping=reverse_mapping,
        )

        horas_val = d.get('horas_dedicacion', 0)
        self.add_text_field(
            key='horas_dedicacion',
            label_text="Horas de dedicación semanal",
            placeholder="Ej. 20 o 40 (opcional)",
            required=False,
            validator=self.validator_numerico,
            initial_value=str(horas_val) if horas_val else "",
        )

        active_val = d.get('active', d.get('activo', True))
        self.add_checkbox_field(
            key='active',
            label_text="Investigador activo en el sistema",
            initial_value=bool(active_val),
        )

        # --- Sub-tablas exclusivas de edición: Grupos y Productos ---
        if self.is_edit and self.cedula:
            self._build_grupos_section()
            self._build_productos_section()

    def _build_grupos_section(self):
        """Construye la sub-tabla con los grupos a los que pertenece el investigador (Multilista)."""
        self.add_section("Grupos de investigación adscritos (Multilista)")

        container = ctk.CTkFrame(self.body, fg_color='transparent')
        container.pack(fill='x', padx=SPACING['sm'], pady=(0, SPACING['sm']))

        lbl_info = ctk.CTkLabel(
            container,
            text="📌 Grupos en los que participa el investigador dentro de la Multilista:",
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
        self.tree_groups = ttk.Treeview(
            table_frame,
            columns=('codigo', 'nombre', 'categoria', 'lider'),
            show='headings',
            style='Pea.Treeview',
            height=4,
            selectmode='browse',
        )
        apply_treeview_tags(self.tree_groups)

        self.tree_groups.heading('codigo', text='Código / ID')
        self.tree_groups.heading('nombre', text='Nombre del Grupo')
        self.tree_groups.heading('categoria', text='Categoría')
        self.tree_groups.heading('lider', text='Líder')

        self.tree_groups.column('codigo', width=110, anchor='center')
        self.tree_groups.column('nombre', width=250, anchor='w')
        self.tree_groups.column('categoria', width=80, anchor='center')
        self.tree_groups.column('lider', width=150, anchor='w')

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient='vertical',
            style='Pea.Vertical.TScrollbar',
            command=self.tree_groups.yview,
        )
        self.tree_groups.configure(yscrollcommand=scrollbar.set)

        self.tree_groups.pack(side='left', fill='x', expand=True, padx=(1, 0), pady=1)
        scrollbar.pack(side='right', fill='y', padx=(0, 1), pady=1)

        self._refresh_grupos_table()

    def _refresh_grupos_table(self):
        """Carga los grupos del investigador directamente desde la Multilista."""
        if not hasattr(self, 'tree_groups'):
            return
        for item in self.tree_groups.get_children():
            self.tree_groups.delete(item)

        app = self.resolve_app()
        if not app or not hasattr(app, 'multilista'):
            return

        try:
            grupos = app.multilista.get_grupos_by_investigador(self.cedula)
            for idx, g in enumerate(grupos):
                code = getattr(g, 'codigo_gruplac', '') or getattr(g, 'code', '') or getattr(g, 'id', '')
                nom = getattr(g, 'nombre', '') or getattr(g, 'name', '')
                cat = getattr(g, 'categoria', '') or getattr(g, 'category', '')
                lid = getattr(g, 'lider', '') or getattr(g, 'leader', '')
                tag = 'even' if idx % 2 == 0 else 'odd'
                self.tree_groups.insert('', 'end', iid=f"inv_grp_{idx}_{code}", values=(code, nom, cat, lid), tags=(tag,))
        except Exception as e:
            print("Error cargando grupos del investigador:", e)

    def _build_productos_section(self):
        """Construye la sub-tabla con los productos del investigador (Multilista)."""
        self.add_section("Productos del investigador (Multilista)")

        container = ctk.CTkFrame(self.body, fg_color='transparent')
        container.pack(fill='x', padx=SPACING['sm'], pady=(0, SPACING['sm']))

        lbl_info = ctk.CTkLabel(
            container,
            text="📌 Publicaciones y desarrollos científicos registrados en la Multilista:",
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
            columns=('id', 'titulo', 'tipo', 'categoria', 'anio', 'validacion'),
            show='headings',
            style='Pea.Treeview',
            height=5,
            selectmode='browse',
        )
        apply_treeview_tags(self.tree_prods)

        self.tree_prods.heading('id', text='ID')
        self.tree_prods.heading('titulo', text='Título del producto')
        self.tree_prods.heading('tipo', text='Tipo')
        self.tree_prods.heading('categoria', text='Categoría')
        self.tree_prods.heading('anio', text='Año')
        self.tree_prods.heading('validacion', text='Validación')

        self.tree_prods.column('id', width=65, anchor='center')
        self.tree_prods.column('titulo', width=220, anchor='w')
        self.tree_prods.column('tipo', width=100, anchor='w')
        self.tree_prods.column('categoria', width=120, anchor='w')
        self.tree_prods.column('anio', width=50, anchor='center')
        self.tree_prods.column('validacion', width=90, anchor='center')

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient='vertical',
            style='Pea.Vertical.TScrollbar',
            command=self.tree_prods.yview,
        )
        self.tree_prods.configure(yscrollcommand=scrollbar.set)

        self.tree_prods.pack(side='left', fill='x', expand=True, padx=(1, 0), pady=1)
        scrollbar.pack(side='right', fill='y', padx=(0, 1), pady=1)

        self._refresh_productos_table()

    def _refresh_productos_table(self):
        """Carga los productos del investigador directamente desde la Multilista."""
        if not hasattr(self, 'tree_prods'):
            return
        for item in self.tree_prods.get_children():
            self.tree_prods.delete(item)

        app = self.resolve_app()
        if not app or not hasattr(app, 'multilista'):
            return

        try:
            prods = app.multilista.get_productos_by_investigador(self.cedula)
            for idx, p in enumerate(prods):
                pid = str(getattr(p, 'id', '') or '')
                tit = str(getattr(p, 'titulo', '') or getattr(p, 'title', '') or '')
                ptype = str(getattr(p, 'tipo', '') or getattr(p, 'type', '') or '')
                cat = str(getattr(p, 'categoria', getattr(p, 'categoria_producto', 'Nuevo conocimiento')) or 'Nuevo conocimiento')
                anio = str(getattr(p, 'anio', 0) or getattr(p, 'year', 0) or '')
                val = str(getattr(p, 'validacion', 'No validado') or 'No validado')
                tag = 'even' if idx % 2 == 0 else 'odd'
                self.tree_prods.insert(
                    '', 'end',
                    iid=f"inv_prod_{idx}_{pid}",
                    values=(pid, tit, ptype, cat, anio, val),
                    tags=(tag,)
                )
        except Exception as e:
            print("Error cargando productos del investigador:", e)

    def get_data(self) -> Dict[str, Any]:
        """Extrae el diccionario normalizado con alias para el CRUD."""
        raw = super().get_data()
        cedula = raw.get('cedula', '').strip()
        nombres = raw.get('nombres', '').strip()
        email = raw.get('email', '').strip()
        grupo_id = raw.get('grupo_id')
        active = bool(raw.get('active', True))
        try:
            horas = int(raw.get('horas_dedicacion', 0) or 0)
        except (ValueError, TypeError):
            horas = 0

        return {
            'id': cedula,
            'cedula': cedula,
            'name': nombres,
            'nombres': nombres,
            'email': email,
            'group': grupo_id,
            'grupo_id': grupo_id,
            'horas_dedicacion': horas,
            'active': active,
            'activo': active,
        }