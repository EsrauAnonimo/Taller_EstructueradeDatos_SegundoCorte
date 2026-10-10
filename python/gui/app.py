# -*- coding: utf-8 -*-
"""Ventana principal con CustomTkinter."""

import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog

import customtkinter as ctk

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from persistencia.persistencia_json import PersistenciaJSON
from modelos.multilista import Multilist
from crud.crud_grupos import GrupoCRUD
from crud.crud_investigadores import InvestigadorCRUD
from crud.crud_productos import ProductoCRUD
from entidades.grupo import Grupo
from entidades.investigador import Investigador
from entidades.producto import Producto
from gui.tabs.grupos_tab import GruposTab
from gui.tabs.investigadores_tab import InvestigadoresTab
from gui.tabs.productos_tab import ProductosTab
from gui.tabs.estadisticas_tab import EstadisticasTab
from gui.styles import (
    COLORS,
    SPACING,
    font,
    setup_app,
    style_tabview,
)
from scraping import scienti


class App(ctk.CTk):
    """Aplicación principal de escritorio PEA-i."""

    def __init__(self):
        super().__init__()

        # Configuración del sistema de diseño (modo claro, estilos ttk, matplotlib)
        setup_app(self)

        self.title("PEA-i - Programa Estadístico de Análisis de Investigación")
        self.geometry("1240x740")
        self.minsize(1200, 700)

        # Inicialización de modelos de datos y CRUDs
        self.persistencia = None
        self.multilista = Multilist()
        self.grupo_crud = GrupoCRUD(self.multilista)
        self.inv_crud = InvestigadorCRUD(self.multilista)
        self.prod_crud = ProductoCRUD(self.multilista)

        self.init_persistence()

        # Contenedor de pestañas con estilo pill moderno
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(
            fill='both',
            expand=True,
            padx=SPACING['md'],
            pady=(SPACING['sm'], 0),
        )
        style_tabview(self.tabview)

        # Creación e inyección de dependencias en las pestañas
        self.grupos_tab = GruposTab(self.tabview.add("Grupos"), app=self)
        self.investigadores_tab = InvestigadoresTab(self.tabview.add("Investigadores"), app=self)
        self.productos_tab = ProductosTab(self.tabview.add("Productos"), app=self)
        self.estadisticas_tab = EstadisticasTab(self.tabview.add("Estadísticas"), app=self)

        # Barra de estado discreta (borde superior de 1 px y texto small/muted)
        self.status_border = ctk.CTkFrame(
            self,
            height=1,
            fg_color=COLORS['border'],
            corner_radius=0,
        )
        self.status_border.pack(fill='x', side='bottom')

        self.status_bar = ctk.CTkFrame(
            self,
            height=28,
            fg_color=COLORS['surface_alt'],
            corner_radius=0,
        )
        self.status_bar.pack(fill='x', side='bottom')

        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="Persistencia: JSON",
            font=font('small'),
            text_color=COLORS['muted'],
            anchor='w',
        )
        self.status_label.pack(side='left', padx=SPACING['md'], pady=(2, 2))
        self.update_status()

        self.create_menu()
        self.load_data()

    def init_persistence(self):
        """Inicializa la persistencia directa con archivo JSON."""
        datos_path = Path(__file__).resolve().parent.parent / 'datos' / 'datos.json'
        self.persistencia = PersistenciaJSON(filepath=str(datos_path))

    def update_status(self):
        """Actualiza el texto descriptivo de la barra de estado inferior."""
        text = "Persistencia: JSON"
        try:
            self.status_label.configure(text=text)
        except Exception:
            pass

    def create_menu(self):
        """Menú nativo superior del sistema."""
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Cargar datos", command=self.load_data)
        file_menu.add_command(label="Guardar datos", command=self.save_data)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.quit)
        menubar.add_cascade(label="Archivo", menu=file_menu)

        data_menu = tk.Menu(menubar, tearoff=0)
        data_menu.add_command(label="Descargar del SCIENTI", command=self.download_scienti)
        data_menu.add_command(label="Cargar desde CSV", command=self.load_csv)
        menubar.add_cascade(label="Datos", menu=data_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Acerca de", command=self.about)
        menubar.add_cascade(label="Ayuda", menu=help_menu)

        self.configure(menu=menubar)

    def load_tabs_data(self):
        """Refresca la información visible en cada una de las pestañas."""
        try:
            self.grupos_tab.load_data()
        except Exception:
            pass
        try:
            self.investigadores_tab.load_data()
        except Exception:
            pass
        try:
            self.productos_tab.load_data()
        except Exception:
            pass
        try:
            self.estadisticas_tab.refresh()
        except Exception:
            pass

    def load_data(self):
        """Carga y sincroniza los datos persistidos en memoria y pestañas."""
        try:
            datos = self.persistencia.load()
            if isinstance(datos, dict):
                # Caso 1: Formato estructurado nativo de PersistenciaJSON / Multilist
                if 'grupos' in datos and datos['grupos'] and isinstance(datos['grupos'][0], dict) and 'grupo' in datos['grupos'][0]:
                    self.multilista = PersistenciaJSON.to_multilist(datos)
                else:
                    # Caso 2: Formato de carga plana
                    self.multilista = Multilist()
                    self.grupo_crud = GrupoCRUD(self.multilista)
                    self.inv_crud = InvestigadorCRUD(self.multilista)
                    self.prod_crud = ProductoCRUD(self.multilista)

                    for g in datos.get('grupos', []):
                        if isinstance(g, dict):
                            grupo_obj = Grupo(
                                id=g.get('id'),
                                codigo_gruplac=g.get('code') or g.get('codigo_gruplac', ''),
                                nombre=g.get('name') or g.get('nombre', ''),
                                categoria=g.get('category') or g.get('categoria', ''),
                                lider=g.get('leader') or g.get('lider', ''),
                                activo=g.get('active', g.get('activo', True)),
                                fecha_creacion=g.get('fecha_creacion', ''),
                            )
                        else:
                            grupo_obj = g
                        try:
                            self.grupo_crud.create(grupo_obj)
                        except Exception:
                            pass

                    inv_id_to_cedula = {}
                    for i in datos.get('investigadores', []):
                        if isinstance(i, dict):
                            cedula_str = str(i.get('cedula') or i.get('id', ''))
                            inv_obj = Investigador(
                                id=i.get('id'),
                                cedula=cedula_str,
                                nombres=i.get('name') or i.get('nombres', ''),
                                apellidos=i.get('apellidos', ''),
                                email=i.get('email', ''),
                                activo=i.get('active', i.get('activo', True)),
                                grupo_id=i.get('grupo_id') or i.get('group'),
                            )
                            if i.get('id') is not None:
                                inv_id_to_cedula[i.get('id')] = cedula_str
                        else:
                            inv_obj = i
                            if getattr(inv_obj, 'id', None) is not None:
                                inv_id_to_cedula[inv_obj.id] = getattr(inv_obj, 'cedula', str(inv_obj.id))
                        try:
                            self.inv_crud.create(inv_obj)
                        except Exception:
                            pass

                    for p in datos.get('productos', []):
                        if isinstance(p, dict):
                            try:
                                anio_val = int(p.get('year') or p.get('anio') or 0)
                            except ValueError:
                                anio_val = 0
                            inv_id_val = p.get('investigador_id')
                            cedula_val = p.get('investigador_cedula') or inv_id_to_cedula.get(inv_id_val) or str(inv_id_val)
                            prod_obj = Producto(
                                id=p.get('id'),
                                titulo=p.get('title') or p.get('titulo', ''),
                                tipo=p.get('type') or p.get('tipo', ''),
                                categoria=p.get('categoria', ''),
                                validado=p.get('active', p.get('validado', True)),
                                anio=anio_val,
                                investigador_id=inv_id_val,
                                grupo_id=p.get('grupo_id') or p.get('group'),
                            )
                            prod_obj.investigador_cedula = cedula_val
                        else:
                            prod_obj = p
                        try:
                            self.prod_crud.create(prod_obj)
                        except Exception:
                            pass

            self.grupo_crud = GrupoCRUD(self.multilista)
            self.inv_crud = InvestigadorCRUD(self.multilista)
            self.prod_crud = ProductoCRUD(self.multilista)
        except Exception as e:
            print("Aviso al cargar datos:", e)

        self.load_tabs_data()

    def save_data(self):
        """Guarda la estructura actual en la capa de persistencia activa."""
        try:
            self.persistencia.save(self.multilista)
            messagebox.showinfo("Guardar", "Datos guardados correctamente")
        except Exception:
            # Fallback en caso de que persistencia espere un diccionario plano
            try:
                datos = {
                    'grupos': [g.to_dict() if hasattr(g, 'to_dict') else g.__dict__ for g in self.grupo_crud.list_all()],
                    'investigadores': [i.to_dict() if hasattr(i, 'to_dict') else i.__dict__ for i in self.inv_crud.list_all()],
                    'productos': [p.to_dict() if hasattr(p, 'to_dict') else p.__dict__ for p in self.prod_crud.list_all()],
                }
                self.persistencia.save(datos)
                messagebox.showinfo("Guardar", "Datos guardados correctamente")
            except Exception as ex:
                messagebox.showerror("Error", f"No se pudo guardar la información: {ex}")

    def download_scienti(self):
        """Descarga información de un grupo desde la plataforma SCIENTI."""
        try:
            url = simpledialog.askstring("SCIENTI", "Ingrese la URL del grupo:", initialvalue="")
            if not url:
                return
            datos = scienti.download_group(url)
            if not datos or "error" in datos:
                raise Exception("Sin datos o error de conexión")

            new_multilist = PersistenciaJSON.to_multilist(datos)
            if new_multilist and not new_multilist.is_empty():
                self.multilista = new_multilist
                self.grupo_crud = GrupoCRUD(self.multilista)
                self.inv_crud = InvestigadorCRUD(self.multilista)
                self.prod_crud = ProductoCRUD(self.multilista)

            self.save_data()
            self.load_tabs_data()
            messagebox.showinfo("Éxito", "Datos descargados y guardados")
        except Exception:
            if messagebox.askyesno("Error", "No se pudo descargar de SCIENTI. ¿Desea cargar desde archivo CSV?"):
                self.load_csv()

    def load_csv(self):
        """Carga datos de grupos, investigadores y productos desde un archivo CSV."""
        try:
            path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv"), ("Todos", "*.*")])
            if not path:
                return
            datos = scienti.download_from_csv(path)
            if not datos or "error" in datos:
                messagebox.showerror("Error", "No se pudo procesar el archivo CSV")
                return

            new_multilist = PersistenciaJSON.to_multilist(datos)
            if new_multilist and not new_multilist.is_empty():
                self.multilista = new_multilist
                self.grupo_crud = GrupoCRUD(self.multilista)
                self.inv_crud = InvestigadorCRUD(self.multilista)
                self.prod_crud = ProductoCRUD(self.multilista)

            self.save_data()
            self.load_tabs_data()
            messagebox.showinfo("Éxito", "Datos cargados correctamente desde CSV")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar el archivo CSV: {e}")

    def about(self):
        """Muestra ventana modal con información sobre la aplicación."""
        messagebox.showinfo(
            "Acerca de",
            "PEA-i (Programa Estadístico de Análisis de Investigación)\n\n"
            "Taller de Estructura de Datos - Segundo Corte\n"
            "Diseñado con CustomTkinter y arquitectura de Multilistas.",
        )


def main():
    """Punto de entrada de la interfaz gráfica."""
    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()