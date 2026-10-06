# -*- coding: utf-8 -*-
import customtkinter as ctk
from tkinter import ttk
import datetime


class ProductosTab(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        filter_frame = ctk.CTkFrame(self, fg_color='transparent')
        filter_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)
        ctk.CTkLabel(filter_frame, text='Filtro por año:').pack(side='left', padx=2)
        self.filter_var = ctk.StringVar(value='Todos')
        self.filter_menu = ctk.CTkOptionMenu(filter_frame, values=['Todos', 'Últimos 2 años', 'Últimos 5 años', 'Personalizado'], variable=self.filter_var, command=self.on_filter_change)
        self.filter_menu.pack(side='left', padx=2)
        self.from_entry = ctk.CTkEntry(filter_frame, width=80, placeholder_text='Desde')
        self.to_entry = ctk.CTkEntry(filter_frame, width=80, placeholder_text='Hasta')
        self.from_entry.pack(side='left', padx=2)
        self.to_entry.pack(side='left', padx=2)
        self.from_entry.pack_forget()
        self.to_entry.pack_forget()

        toolbar = ctk.CTkFrame(self, fg_color='transparent')
        toolbar.grid(row=1, column=0, sticky='ew', padx=10, pady=5)
        ctk.CTkButton(toolbar, text='Crear', command=self.create).pack(side='left', padx=2)
        ctk.CTkButton(toolbar, text='Editar', command=self.edit).pack(side='left', padx=2)
        ctk.CTkButton(toolbar, text='Desactivar', command=self.deactivate).pack(side='left', padx=2)
        ctk.CTkButton(toolbar, text='Activar', command=self.activate).pack(side='left', padx=2)
        ctk.CTkButton(toolbar, text='Eliminar', command=self.delete).pack(side='left', padx=2)
        ctk.CTkButton(toolbar, text='Actualizar', command=self.refresh).pack(side='right', padx=2)

        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=2, column=0, sticky='nsew', padx=10, pady=5)
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        columns = ('id', 'title', 'type', 'year', 'group', 'active')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        for c in columns:
            self.tree.heading(c, text=c.title())
            self.tree.column(c, width=120)
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.refresh()

    def on_filter_change(self, *_):
        if self.filter_var.get() == 'Personalizado':
            self.from_entry.pack(side='left', padx=2)
            self.to_entry.pack(side='left', padx=2)
        else:
            self.from_entry.pack_forget()
            self.to_entry.pack_forget()

    def create(self): pass
    def edit(self): pass
    def deactivate(self): pass
    def activate(self): pass
    def delete(self): pass
    def refresh(self): pass
