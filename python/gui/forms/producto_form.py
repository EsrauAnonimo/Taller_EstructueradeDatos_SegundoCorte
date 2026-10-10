# -*- coding: utf-8 -*-
"""Formulario modal para creación y edición de Producto."""

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


class ProductoForm(ctk.CTkToplevel):
    """Modal para captura y modificación de atributos de Producto."""

    def __init__(self, master, data: Optional[Dict[str, Any]] = None):
        super().__init__(master)
        self.configure(fg_color=COLORS['bg'])

        is_edit = data is not None
        title_text = "Editar producto" if is_edit else "Crear producto"
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

        # Campo: Título
        self.lbl_product_title = ctk.CTkLabel(
            self.container,
            text="Título del producto",
            font=font('small'),
            text_color=COLORS['muted'],
            anchor='w',
        )
        self.lbl_product_title.pack(fill='x', padx=SPACING['lg'], pady=(0, 2))
        self.title_entry = entry(self.container, placeholder_text="Título de la publicación o desarrollo")
        self.title_entry.pack(fill='x', padx=SPACING['lg'], pady=(0, SPACING['sm']))

        # Campo: Tipo
        self.lbl_type = ctk.CTkLabel(
            self.container,
            text="Tipo de producto",
            font=font('small'),
            text_color=COLORS['muted'],
            anchor='w',
        )
        self.lbl_type.pack(fill='x', padx=SPACING['lg'], pady=(0, 2))
        self.type_entry = entry(self.container, placeholder_text="Ej. Artículo, Libro, Ponencia, Software")
        self.type_entry.pack(fill='x', padx=SPACING['lg'], pady=(0, SPACING['sm']))

        # Campo: Año
        self.lbl_year = ctk.CTkLabel(
            self.container,
            text="Año de publicación",
            font=font('small'),
            text_color=COLORS['muted'],
            anchor='w',
        )
        self.lbl_year.pack(fill='x', padx=SPACING['lg'], pady=(0, 2))
        self.year_entry = entry(self.container, placeholder_text="Ej. 2024")
        self.year_entry.pack(fill='x', padx=SPACING['lg'], pady=(0, SPACING['sm']))

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
            text="Producto validado y activo",
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
            title_val = data.get('title') or data.get('titulo', '')
            type_val = data.get('type') or data.get('tipo', '')
            year_val = data.get('year', data.get('anio', ''))
            group_val = data.get('group', data.get('grupo_id', ''))
            active_val = data.get('active', data.get('validado', True))

            self.title_entry.insert(0, str(title_val))
            self.type_entry.insert(0, str(type_val))
            self.year_entry.insert(0, str(year_val) if year_val else '')
            self.group_entry.insert(0, str(group_val) if group_val is not None else '')
            self.active_var.set(bool(active_val))

    def get_data(self) -> Dict[str, Any]:
        """Extrae el diccionario normalizado con alias para el CRUD."""
        title_val = self.title_entry.get().strip()
        type_val = self.type_entry.get().strip()
        year_val = self.year_entry.get().strip()
        group_val = self.group_entry.get().strip()
        active_val = self.active_var.get()
        return {
            'title': title_val,
            'titulo': title_val,
            'type': type_val,
            'tipo': type_val,
            'year': year_val,
            'anio': year_val,
            'group': group_val,
            'grupo_id': group_val,
            'active': active_val,
            'validado': active_val,
        }

    def save(self):
        """Valida que los campos obligatorios existan y guarda."""
        data = self.get_data()
        if not data['title']:
            messagebox.showerror("Error", "Título es obligatorio")
            return
        self.result = data
        self.destroy()

    def cancel(self):
        """Cancela la operación y destruye el modal."""
        self.result = None
        self.destroy()