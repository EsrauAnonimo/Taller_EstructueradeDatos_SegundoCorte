# -*- coding: utf-8 -*-
"""Formulario para Grupo."""
import customtkinter as ctk
from tkinter import messagebox


class GrupoForm(ctk.CTkToplevel):
    def __init__(self, master, data=None):
        super().__init__(master)
        self.title('Formulario de Grupo')
        self.geometry('500x380')
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.result = None

        ctk.CTkLabel(self, text='Grupo').pack(padx=10, pady=(10, 5))

        ctk.CTkLabel(self, text='Código').pack(anchor='w', padx=20)
        self.code_entry = ctk.CTkEntry(self)
        self.code_entry.pack(fill='x', padx=20, pady=2)

        ctk.CTkLabel(self, text='Nombre').pack(anchor='w', padx=20)
        self.name_entry = ctk.CTkEntry(self)
        self.name_entry.pack(fill='x', padx=20, pady=2)

        ctk.CTkLabel(self, text='Categoría').pack(anchor='w', padx=20)
        self.category_entry = ctk.CTkEntry(self)
        self.category_entry.pack(fill='x', padx=20, pady=2)

        ctk.CTkLabel(self, text='Líder').pack(anchor='w', padx=20)
        self.leader_entry = ctk.CTkEntry(self)
        self.leader_entry.pack(fill='x', padx=20, pady=2)

        ctk.CTkLabel(self, text='Activo').pack(anchor='w', padx=20)
        self.active_var = ctk.BooleanVar(value=True)
        self.active_check = ctk.CTkCheckBox(self, text='Activo', variable=self.active_var)
        self.active_check.pack(anchor='w', padx=20, pady=5)

        frame_btn = ctk.CTkFrame(self, fg_color='transparent')
        frame_btn.pack(fill='x', padx=20, pady=15)
        ctk.CTkButton(frame_btn, text='Guardar', command=self.save).pack(side='left', expand=True, padx=2)
        ctk.CTkButton(frame_btn, text='Cancelar', command=self.cancel).pack(side='right', expand=True, padx=2)

        if data:
            self.code_entry.insert(0, data.get('code', ''))
            self.name_entry.insert(0, data.get('name', ''))
            self.category_entry.insert(0, data.get('category', ''))
            self.leader_entry.insert(0, data.get('leader', ''))
            self.active_var.set(data.get('active', True))

    def get_data(self):
        return {
            'code': self.code_entry.get().strip(),
            'name': self.name_entry.get().strip(),
            'category': self.category_entry.get().strip(),
            'leader': self.leader_entry.get().strip(),
            'active': self.active_var.get(),
        }

    def save(self):
        data = self.get_data()
        if not data['code'] or not data['name']:
            messagebox.showerror('Error', 'Código y Nombre son obligatorios')
            return
        self.result = data
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()