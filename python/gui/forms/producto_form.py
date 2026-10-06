# -*- coding: utf-8 -*-
"""Formulario para Producto."""
import customtkinter as ctk
from tkinter import messagebox


class ProductoForm(ctk.CTkToplevel):
    def __init__(self, master, data=None):
        super().__init__(master)
        self.title('Formulario de Producto')
        self.geometry('500x380')
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.result = None

        ctk.CTkLabel(self, text='Producto').pack(padx=10, pady=(10, 5))

        ctk.CTkLabel(self, text='Título').pack(anchor='w', padx=20)
        self.title_entry = ctk.CTkEntry(self)
        self.title_entry.pack(fill='x', padx=20, pady=2)

        ctk.CTkLabel(self, text='Tipo').pack(anchor='w', padx=20)
        self.type_entry = ctk.CTkEntry(self)
        self.type_entry.pack(fill='x', padx=20, pady=2)

        ctk.CTkLabel(self, text='Año').pack(anchor='w', padx=20)
        self.year_entry = ctk.CTkEntry(self)
        self.year_entry.pack(fill='x', padx=20, pady=2)

        ctk.CTkLabel(self, text='Grupo').pack(anchor='w', padx=20)
        self.group_entry = ctk.CTkEntry(self)
        self.group_entry.pack(fill='x', padx=20, pady=2)

        ctk.CTkLabel(self, text='Activo').pack(anchor='w', padx=20)
        self.active_var = ctk.BooleanVar(value=True)
        self.active_check = ctk.CTkCheckBox(self, text='Activo', variable=self.active_var)
        self.active_check.pack(anchor='w', padx=20, pady=5)

        frame_btn = ctk.CTkFrame(self, fg_color='transparent')
        frame_btn.pack(fill='x', padx=20, pady=15)
        ctk.CTkButton(frame_btn, text='Guardar', command=self.save).pack(side='left', expand=True, padx=2)
        ctk.CTkButton(frame_btn, text='Cancelar', command=self.cancel).pack(side='right', expand=True, padx=2)

        if data:
            self.title_entry.insert(0, data.get('title', ''))
            self.type_entry.insert(0, data.get('type', ''))
            self.year_entry.insert(0, data.get('year', ''))
            self.group_entry.insert(0, data.get('group', ''))
            self.active_var.set(data.get('active', True))

    def get_data(self):
        return {
            'title': self.title_entry.get().strip(),
            'type': self.type_entry.get().strip(),
            'year': self.year_entry.get().strip(),
            'group': self.group_entry.get().strip(),
            'active': self.active_var.get(),
        }

    def save(self):
        data = self.get_data()
        if not data['title']:
            messagebox.showerror('Error', 'Título es obligatorio')
            return
        self.result = data
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()