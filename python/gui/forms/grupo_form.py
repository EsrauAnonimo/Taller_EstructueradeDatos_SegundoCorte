# -*- coding: utf-8 -*-
"""Formulario modal para creación y edición de Grupo."""

from typing import Optional, Dict, Any
from tkinter import messagebox
import customtkinter as ctk

from gui.styles import (
    COLORS,
    RADIUS,
    SPACING,
    font,
    button,
    entry,
    card,
)


class GrupoForm(ctk.CTkToplevel):
    """Modal para captura y modificación de atributos de Grupo."""

    def __init__(self, master, data: Optional[Dict[str, Any]] = None):
        super().__init__(master)
        self.configure(fg_color=COLORS['bg'])

        is_edit = data is not None
        title_text = "Editar grupo" if is_edit else "Crear grupo"
        self.title(title_text)
        self.geometry('480x530')
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.result = None

        # Tarjeta contenedora blanca con 24 px de padding
        self.container = card(self)
        self.container.pack(fill='both', expand=True, padx=SPACING['lg'], pady=SPACING['lg'])

        # Encabezado con tipografía heading
        self.lbl_title = ctk.CTkLabel(
            self.container,
            text=title_text,
            font=font('heading'),
            text_color=COLORS['ink'],
            anchor='w',
        )
        self.lbl_title.pack(fill='x', padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['md']))

        # Campo: Código Gruplac
        self.lbl_code = ctk.CTkLabel(
            self.container,
            text="Código Gruplac",
            font=font('small'),
            text_color=COLORS['muted'],
            anchor='w',
        )
        self.lbl_code.pack(fill='x', padx=SPACING['lg'], pady=(0, 2))
        self.code_entry = entry(self.container, placeholder_text="Ej. COL0001")
        self.code_entry.pack(fill='x', padx=SPACING['lg'], pady=(0, SPACING['sm']))

        # Campo: Nombre
        self.lbl_name = ctk.CTkLabel(
            self.container,
            text="Nombre del grupo",
            font=font('small'),
            text_color=COLORS['muted'],
            anchor='w',
        )
        self.lbl_name.pack(fill='x', padx=SPACING['lg'], pady=(0, 2))
        self.name_entry = entry(self.container, placeholder_text="Nombre de la línea o grupo")
        self.name_entry.pack(fill='x', padx=SPACING['lg'], pady=(0, SPACING['sm']))

        # Campo: Categoría
        self.lbl_cat = ctk.CTkLabel(
            self.container,
            text="Categoría",
            font=font('small'),
            text_color=COLORS['muted'],
            anchor='w',
        )
        self.lbl_cat.pack(fill='x', padx=SPACING['lg'], pady=(0, 2))
        self.category_entry = entry(self.container, placeholder_text="Ej. A1, A, B, C o Reconocido")
        self.category_entry.pack(fill='x', padx=SPACING['lg'], pady=(0, SPACING['sm']))

        # Campo: Líder
        self.lbl_leader = ctk.CTkLabel(
            self.container,
            text="Líder del grupo",
            font=font('small'),
            text_color=COLORS['muted'],
            anchor='w',
        )
        self.lbl_leader.pack(fill='x', padx=SPACING['lg'], pady=(0, 2))
        self.leader_entry = entry(self.container, placeholder_text="Nombre completo del líder")
        self.leader_entry.pack(fill='x', padx=SPACING['lg'], pady=(0, SPACING['sm']))

        # Campo: Activo
        self.active_var = ctk.BooleanVar(value=True)
        self.active_check = ctk.CTkCheckBox(
            self.container,
            text="Grupo activo en el sistema",
            variable=self.active_var,
            font=font('body'),
            text_color=COLORS['ink'],
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_hover'],
            corner_radius=RADIUS['control'],
        )
        self.active_check.pack(anchor='w', padx=SPACING['lg'], pady=(SPACING['xs'], SPACING['md']))

        # Barra de botones inferior alineada a la derecha
        self.btn_frame = ctk.CTkFrame(self.container, fg_color='transparent')
        self.btn_frame.pack(fill='x', padx=SPACING['lg'], pady=(SPACING['sm'], SPACING['lg']))

        self.btn_save = button(
            self.btn_frame,
            text="Guardar",
            variant='primary',
            command=self.save,
            width=100,
        )
        self.btn_save.pack(side='right', padx=(SPACING['sm'], 0))

        self.btn_cancel = button(
            self.btn_frame,
            text="Cancelar",
            variant='secondary',
            command=self.cancel,
            width=100,
        )
        self.btn_cancel.pack(side='right')

        # Cargar datos preexistentes si es edición
        if data:
            code_val = data.get('code') or data.get('codigo_gruplac', '')
            name_val = data.get('name') or data.get('nombre', '')
            cat_val = data.get('category') or data.get('categoria', '')
            leader_val = data.get('leader') or data.get('lider', '')
            active_val = data.get('active', data.get('activo', True))

            self.code_entry.insert(0, str(code_val))
            self.name_entry.insert(0, str(name_val))
            self.category_entry.insert(0, str(cat_val))
            self.leader_entry.insert(0, str(leader_val))
            self.active_var.set(bool(active_val))

    def get_data(self) -> Dict[str, Any]:
        """Extrae el diccionario normalizado con alias para compatibilidad."""
        code = self.code_entry.get().strip()
        name = self.name_entry.get().strip()
        cat = self.category_entry.get().strip()
        leader = self.leader_entry.get().strip()
        active = self.active_var.get()
        return {
            'code': code,
            'codigo_gruplac': code,
            'name': name,
            'nombre': name,
            'category': cat,
            'categoria': cat,
            'leader': leader,
            'lider': leader,
            'active': active,
            'activo': active,
        }

    def save(self):
        """Valida los campos obligatorios y cierra el modal con el resultado."""
        data = self.get_data()
        if not data['code'] or not data['name']:
            messagebox.showerror("Error", "Código y Nombre son obligatorios")
            return
        self.result = data
        self.destroy()

    def cancel(self):
        """Cancela la operación y destruye la ventana."""
        self.result = None
        self.destroy()