# -*- coding: utf-8 -*-
"""Ventana principal con CustomTkinter."""
import sys
import traceback
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog

import customtkinter as ctk

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from persistencia.persistencia_postgres import PersistenciaPostgres
from persistencia.persistencia_json import PersistenciaJSON
from modelos.multilista import Multilist
from crud.crud_grupos import GrupoCRUD
from crud.crud_investigadores import InvestigadorCRUD
from crud.crud_productos import ProductoCRUD
from gui.tabs.grupos_tab import GruposTab
from gui.tabs.investigadores_tab import InvestigadoresTab
from gui.tabs.productos_tab import ProductosTab
from gui.tabs.estadisticas_tab import EstadisticasTab
from gui.styles import apply_theme
from scraping import scienti


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        apply_theme()
        self.title('PEA-i - Programa Estadístico de Análisis de Investigación')
        self.geometry('1200x700')
        self.minsize(1200, 700)

        self.persistencia = None
        self.multilista = Multilist()
        self.grupo_crud = GrupoCRUD(self.multilista)
        self.inv_crud = InvestigadorCRUD(self.multilista)
        self.prod_crud = ProductoCRUD(self.multilista)

        self.init_persistence()

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill='both', expand=True, padx=10, pady=(10, 5))

        self.grupos_tab = GruposTab(self.tabview.add('Grupos'))
        self.investigadores_tab = InvestigadoresTab(self.tabview.add('Investigadores'))
        self.productos_tab = ProductosTab(self.tabview.add('Productos'))
        self.estadisticas_tab = EstadisticasTab(self.tabview.add('Estadísticas'))

        self.status_label = ctk.CTkLabel(self, text='Persistencia: ...')
        self.status_label.pack(fill='x', padx=10, pady=(0, 10))
        self.update_status()

        self.create_menu()
        self.load_data()

    def init_persistence(self):
        try:
            p = PersistenciaPostgres()
            if p.connect():
                p.close()
                self.persistencia = p
                return
        except Exception as e:
            print('Error al intentar conectar:', e)
        self.persistencia = PersistenciaJSON()
        try:
            messagebox.showwarning('Persistencia', 'Usando persistencia JSON (PostgreSQL no disponible)')
        except Exception:
            pass

    def update_status(self):
        name = 'PostgreSQL' if isinstance(self.persistencia, PersistenciaPostgres) else 'JSON'
        try:
            self.status_label.configure(text='Persistencia: ' + name)
        except Exception:
            pass

    def create_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label='Cargar datos', command=self.load_data)
        file_menu.add_command(label='Guardar datos', command=self.save_data)
        file_menu.add_separator()
        file_menu.add_command(label='Salir', command=self.quit)
        menubar.add_cascade(label='Archivo', menu=file_menu)

        data_menu = tk.Menu(menubar, tearoff=0)
        data_menu.add_command(label='Descargar del SCIENTI', command=self.download_scienti)
        data_menu.add_command(label='Cargar desde CSV', command=self.load_csv)
        menubar.add_cascade(label='Datos', menu=data_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label='Acerca de', command=self.about)
        menubar.add_cascade(label='Ayuda', menu=help_menu)

        self.configure(menu=menubar)

    def load_data(self):
        try:
            datos = self.persistencia.load()
            self.multilista = Multilist()
            self.grupo_crud = GrupoCRUD(self.multilista)
            self.inv_crud = InvestigadorCRUD(self.multilista)
            self.prod_crud = ProductoCRUD(self.multilista)
            if datos:
                if 'grupos' in datos:
                    for g in datos['grupos']:
                        try:
                            self.grupo_crud.crear(g)
                        except Exception:
                            pass
                if 'investigadores' in datos:
                    for i in datos['investigadores']:
                        try:
                            self.inv_crud.crear(i)
                        except Exception:
                            pass
                if 'productos' in datos:
                    for p in datos['productos']:
                        try:
                            self.prod_crud.crear(p)
                        except Exception:
                            pass
        except Exception:
            pass

    def save_data(self):
        try:
            datos = {
                'grupos': [g.to_dict() if hasattr(g, 'to_dict') else g.__dict__ for g in self.grupo_crud.listar()],
                'investigadores': [i.to_dict() if hasattr(i, 'to_dict') else i.__dict__ for i in self.inv_crud.listar()],
                'productos': [p.to_dict() if hasattr(p, 'to_dict') else p.__dict__ for p in self.prod_crud.listar()],
            }
            self.persistencia.save(datos)
            messagebox.showinfo('Guardar', 'Datos guardados correctamente')
        except Exception:
            pass

    def download_scienti(self):
        try:
            url = simpledialog.askstring('SCIENTI', 'Ingrese la URL del grupo:', initialvalue='')
            if not url:
                return
            datos = scienti.download_group(url)
            if not datos:
                raise Exception('Sin datos')
            for g in datos.get('grupos', []):
                try:
                    self.grupo_crud.crear(g)
                except Exception:
                    pass
            for i in datos.get('investigadores', []):
                try:
                    self.inv_crud.crear(i)
                except Exception:
                    pass
            for p in datos.get('productos', []):
                try:
                    self.prod_crud.crear(p)
                except Exception:
                    pass
            self.save_data()
            messagebox.showinfo('Éxito', 'Datos descargados y guardados')
        except Exception as e:
            messagebox.showerror('Error', 'No se pudo descargar. ¿Desea cargar desde CSV?')
            self.load_csv()

    def load_csv(self):
        try:
            path = filedialog.askopenfilename(filetypes=[('CSV', '*.csv'), ('Todos', '*.*')])
            if not path:
                return
            datos = scienti.download_from_csv(path)
            if not datos:
                return
            for g in datos.get('grupos', []):
                try:
                    self.grupo_crud.crear(g)
                except Exception:
                    pass
            for i in datos.get('investigadores', []):
                try:
                    self.inv_crud.crear(i)
                except Exception:
                    pass
            for p in datos.get('productos', []):
                try:
                    self.prod_crud.crear(p)
                except Exception:
                    pass
            self.save_data()
            messagebox.showinfo('Éxito', 'Datos cargados desde CSV')
        except Exception:
            messagebox.showerror('Error', 'No se pudo cargar el archivo')

    def about(self):
        messagebox.showinfo('Acerca de', 'PEA-i - Programa Estadístico de Análisis de Investigación')

    def load_tabs_data(self):
        try:
            self.grupos_tab.refresh()
            self.investigadores_tab.refresh()
            self.productos_tab.refresh()
            self.estadisticas_tab.refresh()
        except Exception:
            pass


def main():
    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()