# -*- coding: utf-8 -*-
"""Formulario para Investigador."""
import customtkinter as ctk
from tkinter import messagebox


class InvestigadorForm(ctk.CTkToplevel):
    def __init__(self, master, data=None):
        super().__init__(master)
        self.title('Formulario de Investigador')
        self.geometry('500x380')
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.result = None

        ctk.CTkLabel(self, text='Investigador').pack(padx=10, pady=(10, 5))

        ctk.CTkLabel(self, text='Identificación').pack(anchor='w', padx=20)
        self.id_entry = ctk.CTkEntry(self)
        self.id_entry.pack(fill='x', padx=20, pady=2)

        ctk.CTkLabel(self, text='Nombre').pack(anchor='w', padx=20)
        self.name_entry = ctk.CTkEntry(self)
        self.name_entry.pack(fill='x', padx=20, pady=2)

        ctk.CTkLabel(self, text='Correo').pack(anchor='w', padx=20)
        self.email_entry = ctk.CTkEntry(self)
        self.email_entry.pack(fill='x', padx=20, pady=2)

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
            self.id_entry.insert(0, data.get('id', ''))
            self.name_entry.insert(0, data.get('name', ''))
            self.email_entry.insert(0, data.get('email', ''))
            self.group_entry.insert(0, data.get('group', ''))
            self.active_var.set(data.get('active', True))

    def get_data(self):
        return {
            'id': self.id_entry.get().strip(),
            'name': self.name_entry.get().strip(),
            'email': self.email_entry.get().strip(),
            'group': self.group_entry.get().strip(),
            'active': self.active_var.get(),
        }

    def save(self):
        data = self.get_data()
        if not data['id'] or not data['name']:
            messagebox.showerror('Error', 'Identificación y Nombre son obligatorios')
            return
        self.result = data
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()