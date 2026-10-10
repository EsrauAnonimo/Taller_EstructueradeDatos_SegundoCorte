# -*- coding: utf-8 -*-
"""Formulario modal para creación y edición de Investigador."""

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


class InvestigadorForm(ctk.CTkToplevel):
    """Modal para captura y modificación de atributos de Investigador."""

    def __init__(self, master, data: Optional[Dict[str, Any]] = None):
        super().__init__(master)
        self.configure(fg_color=COLORS['bg'])

        is_edit = data is not None
        title_text = "Editar investigador" if is_edit else "Crear investigador"
        self.title(title_text)
        self.geometry('480x530')
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.result = None

        # Tarjeta contenedora blanca con 24 px de padding
        self.container = card(self)
        self.container.pack(fill='both', expand=True, padx=SPACING['lg'], pady=SPACING['lg'])

        # Encabezado
        self.lbl_title = ctk.CTkLabel(
            self.container,
            text=title_text,
            font=font('heading'),
            text_color=COLORS['ink'],
            anchor='w',
        )
        self.lbl_title.pack(fill='x', padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['md']))

        # Campo: Cédula / Identificación
        self.lbl_id = ctk.CTkLabel(
            self.container,
            text="Identificación / Cédula",
            font=font('small'),
            text_color=COLORS['muted'],
            anchor='w',
        )
        self.lbl_id.pack(fill='x', padx=SPACING['lg'], pady=(0, 2))
        self.id_entry = entry(self.container, placeholder_text="Ej. 12345678")
        self.id_entry.pack(fill='x', padx=SPACING['lg'], pady=(0, SPACING['sm']))

        # Campo: Nombre
        self.lbl_name = ctk.CTkLabel(
            self.container,
            text="Nombre completo",
            font=font('small'),
            text_color=COLORS['muted'],
            anchor='w',
        )
        self.lbl_name.pack(fill='x', padx=SPACING['lg'], pady=(0, 2))
        self.name_entry = entry(self.container, placeholder_text="Nombres y apellidos")
        self.name_entry.pack(fill='x', padx=SPACING['lg'], pady=(0, SPACING['sm']))

        # Campo: Correo
        self.lbl_email = ctk.CTkLabel(
            self.container,
            text="Correo electrónico",
            font=font('small'),
            text_color=COLORS['muted'],
            anchor='w',
        )
        self.lbl_email.pack(fill='x', padx=SPACING['lg'], pady=(0, 2))
        self.email_entry = entry(self.container, placeholder_text="nombre@institucion.edu.co")
        self.email_entry.pack(fill='x', padx=SPACING['lg'], pady=(0, SPACING['sm']))

        # Campo: Grupo ID
        self.lbl_group = ctk.CTkLabel(
            self.container,
            text="ID de grupo asociado",
            font=font('small'),
            text_color=COLORS['muted'],
            anchor='w',
        )
        self.lbl_group.pack(fill='x', padx=SPACING['lg'], pady=(0, 2))
        self.group_entry = entry(self.container, placeholder_text="Ej. 1")
        self.group_entry.pack(fill='x', padx=SPACING['lg'], pady=(0, SPACING['sm']))

        # Campo: Activo
        self.active_var = ctk.BooleanVar(value=True)
        self.active_check = ctk.CTkCheckBox(
            self.container,
            text="Investigador activo",
            variable=self.active_var,
            font=font('body'),
            text_color=COLORS['ink'],
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_hover'],
            corner_radius=RADIUS['control'],
        )
        self.active_check.pack(anchor='w', padx=SPACING['lg'], pady=(SPACING['xs'], SPACING['md']))

        # Barra de botones inferior
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

        if data:
            id_val = data.get('id') or data.get('cedula', '')
            name_val = data.get('name') or data.get('nombres', '')
            email_val = data.get('email', '')
            group_val = data.get('group', data.get('grupo_id', ''))
            active_val = data.get('active', data.get('activo', True))

            self.id_entry.insert(0, str(id_val))
            self.name_entry.insert(0, str(name_val))
            self.email_entry.insert(0, str(email_val))
            self.group_entry.insert(0, str(group_val) if group_val is not None else '')
            self.active_var.set(bool(active_val))

    def get_data(self) -> Dict[str, Any]:
        """Extrae el diccionario normalizado con alias para el CRUD."""
        id_val = self.id_entry.get().strip()
        name_val = self.name_entry.get().strip()
        email_val = self.email_entry.get().strip()
        group_val = self.group_entry.get().strip()
        active_val = self.active_var.get()
        return {
            'id': id_val,
            'cedula': id_val,
            'name': name_val,
            'nombres': name_val,
            'email': email_val,
            'group': group_val,
            'grupo_id': group_val,
            'active': active_val,
            'activo': active_val,
        }

    def save(self):
        """Valida que los campos obligatorios existan y guarda."""
        data = self.get_data()
        if not data['id'] or not data['name']:
            messagebox.showerror("Error", "Identificación y Nombre son obligatorios")
            return
        self.result = data
        self.destroy()

    def cancel(self):
        """Cancela la operación y destruye el modal."""
        self.result = None
        self.destroy()