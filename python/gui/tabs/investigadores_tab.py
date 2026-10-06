# -*- coding: utf-8 -*-
import customtkinter as ctk
from tkinter import ttk


class InvestigadoresTab(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        toolbar = ctk.CTkFrame(self, fg_color='transparent')
        toolbar.grid(row=0, column=0, sticky='ew', padx=10, pady=5)
        ctk.CTkButton(toolbar, text='Crear', command=self.create).pack(side='left', padx=2)
        ctk.CTkButton(toolbar, text='Editar', command=self.edit).pack(side='left', padx=2)
        ctk.CTkButton(toolbar, text='Desactivar', command=self.deactivate).pack(side='left', padx=2)
        ctk.CTkButton(toolbar, text='Activar', command=self.activate).pack(side='left', padx=2)
        ctk.CTkButton(toolbar, text='Eliminar', command=self.delete).pack(side='left', padx=2)
        ctk.CTkButton(toolbar, text='Actualizar', command=self.refresh).pack(side='right', padx=2)

        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        columns = ('id', 'name', 'email', 'group', 'active')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        for c in columns:
            self.tree.heading(c, text=c.title())
            self.tree.column(c, width=120)
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.refresh()

    def create(self): pass
    def edit(self): pass
    def deactivate(self): pass
    def activate(self): pass
    def delete(self): pass
    def refresh(self): pass
