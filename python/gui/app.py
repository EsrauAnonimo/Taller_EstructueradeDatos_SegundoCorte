# -*- coding: utf-8 -*-
"""Ventana principal de la aplicación PEA-i."""

import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog

import customtkinter as ctk

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# URL oficial de MinCiencias por defecto para descarga directa en un clic
DEFAULT_SCIENTI_URL = "https://scienti.minciencias.gov.co/gruplac/jsp/visualiza/visualizagr.jsp?nro=00000000002099"

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
from gui.dialogs.url_modal import UrlImportModal
from gui.widgets.menu_bar import MenuBarModerno
from gui.styles import (
    COLORS,
    RADIUS,
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

        # Configuración del sistema de diseño
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

        # Menú superior nativo del sistema (tkinter.Menu)
        self.create_menu()

        # Contenedor de pestañas
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(
            fill='both',
            expand=True,
            padx=SPACING['md'],
            pady=(SPACING['xs'], 0),
        )
        style_tabview(self.tabview)

        # Creación e inyección de dependencias en las pestañas
        self.grupos_tab = GruposTab(self.tabview.add("Grupos"), app=self)
        self.investigadores_tab = InvestigadoresTab(self.tabview.add("Investigadores"), app=self)
        self.productos_tab = ProductosTab(self.tabview.add("Productos"), app=self)
        self.estadisticas_tab = EstadisticasTab(self.tabview.add("Estadísticas"), app=self)

        # Barra de estado discreta inferior
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
            text="Usando persistencia: JSON",
            font=font('small'),
            text_color=COLORS['muted'],
            anchor='w',
        )
        self.status_label.pack(side='left', padx=SPACING['md'], pady=(2, 2))
        self.update_status()

        self.load_data()

    def init_persistence(self):
        """Inicializa la persistencia directa con archivo JSON."""
        datos_path = Path(__file__).resolve().parent.parent / 'datos' / 'datos.json'
        self.persistencia = PersistenciaJSON(filepath=str(datos_path))

    def update_status(self, text: str = "Usando persistencia: JSON"):
        """Actualiza el texto de la barra de estado inferior."""
        try:
            self.status_label.configure(text=text)
        except Exception:
            pass

    def create_menu(self):
        """Configura la barra de menú superior con opciones nativas y modernas."""
        # Menú nativo del sistema para compatibilidad estricta
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Cargar datos", command=self.load_data)
        file_menu.add_command(label="Guardar datos", command=self.save_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exportar a Excel", command=self.export_to_excel)
        file_menu.add_command(label="Exportar a CSV", command=self.export_to_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.quit)
        menubar.add_cascade(label="Archivo", menu=file_menu)

        data_menu = tk.Menu(menubar, tearoff=0)
        data_menu.add_command(
            label="Descargar del SCIENTI",
            command=lambda: self.download_from_url(DEFAULT_SCIENTI_URL),
        )
        data_menu.add_command(
            label="Descargar de otra URL...",
            command=self.download_from_custom_url,
        )
        data_menu.add_separator()
        data_menu.add_command(label="Actualizar todo", command=self.refresh_all)
        data_menu.add_separator()
        data_menu.add_command(label="Limpiar datos", command=self.clear_data)
        menubar.add_cascade(label="Datos", menu=data_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Guía rápida", command=self.show_quick_guide)
        help_menu.add_command(label="Acerca de", command=self.about)
        menubar.add_cascade(label="Ayuda", menu=help_menu)

        self.menubar = menubar
        self.file_menu = file_menu
        self.data_menu = data_menu
        self.help_menu = help_menu

        # Barra de menú moderna integrada (MenuBarModerno)
        self.menu_bar = MenuBarModerno(self, app=self)
        self.menu_bar.pack(side='top', fill='x')

        self.menu_bar.add_menu("Archivo", [
            {
                'label': "Cargar datos",
                'shortcut': "Ctrl+O",
                'command': self.load_data,
                'enabled': True,
            },
            {
                'label': "Guardar datos",
                'shortcut': "Ctrl+S",
                'command': self.save_data,
                'enabled': self.has_data,
            },
            {'separator': True},
            {
                'label': "Exportar a Excel",
                'shortcut': "Ctrl+E",
                'command': self.export_to_excel,
                'enabled': self.has_data,
            },
            {
                'label': "Exportar a CSV",
                'shortcut': "Ctrl+Shift+C",
                'command': self.export_to_csv,
                'enabled': self.has_data,
            },
            {'separator': True},
            {
                'label': "Salir",
                'shortcut': "Ctrl+Q",
                'command': self.quit,
                'enabled': True,
            },
        ])

        self.menu_bar.add_menu("Datos", [
            {
                'label': "Descargar del SCIENTI",
                'shortcut': "Ctrl+U",
                'command': lambda: self.download_from_url(DEFAULT_SCIENTI_URL),
                'enabled': True,
            },
            {
                'label': "Descargar de otra URL...",
                'shortcut': "Ctrl+Shift+U",
                'command': self.download_from_custom_url,
                'enabled': True,
            },
            {'separator': True},
            {
                'label': "Actualizar todo",
                'shortcut': "F5",
                'command': self.refresh_all,
                'enabled': True,
            },
            {'separator': True},
            {
                'label': "Limpiar datos",
                'shortcut': "Ctrl+Shift+Del",
                'command': self.clear_data,
                'enabled': self.has_data,
            },
        ])

        self.menu_bar.add_menu("Ayuda", [
            {
                'label': "Guía rápida",
                'shortcut': "F1",
                'command': self.show_quick_guide,
                'enabled': True,
            },
            {
                'label': "Acerca de",
                'shortcut': "Ctrl+H",
                'command': self.about,
                'enabled': True,
            },
        ])

    def download_from_custom_url(self):
        """Solicita una URL personalizada mediante simpledialog y ejecuta la descarga."""
        user_url = simpledialog.askstring(
            "Descargar de otra URL",
            "Ingrese la URL del grupo en SCIENTI / GrupLAC:",
            parent=self,
        )
        if user_url:
            self.download_from_url(user_url.strip())

    def download_scienti(self):
        """Descarga directa del SCIENTI con la URL por defecto."""
        self.download_from_url(DEFAULT_SCIENTI_URL)

    def download_from_url(self, url: str):
        """Descarga e integra la información de un grupo desde la URL especificada de forma directa."""
        if not url or not (url.startswith("http://") or url.startswith("https://")):
            messagebox.showerror("Error", "URL inválida")
            return

        if url == DEFAULT_SCIENTI_URL:
            self.update_status("Descargando desde SCIENTI...")
        else:
            self.update_status(f"Descargando desde {url}...")
        self.update()

        try:
            datos = scienti.download_group(url)
        except Exception as e:
            datos = {"error": f"Error de conexión: {e}"}

        if not datos or (isinstance(datos, dict) and "error" in datos):
            error_msg = datos.get("error", "Error al descargar.") if isinstance(datos, dict) else "Error al descargar."
            self.update_status("Error al descargar. Ofreciendo CSV...")
            messagebox.showerror("Error", error_msg)
            if messagebox.askyesno("Cargar CSV", "¿Desea cargar los datos desde un archivo CSV?"):
                path = filedialog.askopenfilename(
                    filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
                    title="Seleccionar archivo CSV",
                )
                if path:
                    self.load_from_csv(path)
            return

        self.process_downloaded_data(datos)

    def process_downloaded_data(self, datos: dict):
        """Procesa, normaliza e integra los datos descargados en la multilista y persiste."""
        try:
            # Inserción de entidades mediante la capa CRUD
            grupo_obj = None
            if isinstance(datos, dict) and "grupos" in datos:
                new_multilist = PersistenciaJSON.to_multilist(datos)
                if new_multilist and not new_multilist.is_empty():
                    self.multilista = new_multilist
                    self.grupo_crud = GrupoCRUD(self.multilista)
                    self.inv_crud = InvestigadorCRUD(self.multilista)
                    self.prod_crud = ProductoCRUD(self.multilista)
            elif isinstance(datos, dict):
                # 1. Insertar Grupo
                grupo_raw = datos.get("grupo")
                if isinstance(grupo_raw, dict):
                    gid = grupo_raw.get("id") or grupo_raw.get("codigo_gruplac") or f"GRP-{len(self.grupo_crud.list_all()) + 1}"
                    codigo_g = grupo_raw.get("codigo_gruplac") or str(gid)
                    existing = self.grupo_crud.get_by_id(gid)
                    if not existing and codigo_g:
                        existing = self.grupo_crud.get_by_code(codigo_g)
                    if not existing:
                        grupo_obj = Grupo(
                            id=gid,
                            codigo_gruplac=codigo_g,
                            nombre=grupo_raw.get("nombre") or grupo_raw.get("name") or "Grupo SCIENTI",
                            categoria=grupo_raw.get("categoria", ""),
                            lider=grupo_raw.get("lider", ""),
                            activo=True,
                            fecha_creacion=grupo_raw.get("fecha_creacion", ""),
                        )
                        self.grupo_crud.create(grupo_obj)
                    else:
                        grupo_obj = existing
                        gid = getattr(existing, 'id', gid)
                elif isinstance(grupo_raw, Grupo):
                    grupo_obj = grupo_raw
                    gid = grupo_obj.id
                    if not self.grupo_crud.get_by_id(gid):
                        self.grupo_crud.create(grupo_obj)
                else:
                    gid = 1

                # 2. Insertar Investigadores
                inv_list = datos.get("investigadores", [])
                primary_cedula = None
                for inv_raw in inv_list:
                    if isinstance(inv_raw, dict):
                        ced = str(inv_raw.get("cedula") or inv_raw.get("id") or "")
                        if not ced:
                            ced = f"INV-{len(self.inv_crud.list_all()) + 1}"
                        inv_obj = Investigador(
                            id=inv_raw.get("id"),
                            cedula=ced,
                            nombres=inv_raw.get("nombres") or inv_raw.get("nombre", ""),
                            apellidos=inv_raw.get("apellidos", ""),
                            email=inv_raw.get("email", ""),
                            activo=inv_raw.get("activo", True),
                            grupo_id=gid,
                        )
                    elif isinstance(inv_raw, Investigador):
                        inv_obj = inv_raw
                        if not inv_obj.grupo_id:
                            inv_obj.grupo_id = gid
                    else:
                        continue

                    if not primary_cedula:
                        primary_cedula = getattr(inv_obj, 'cedula', None)
                    if not self.inv_crud.get_by_cedula(inv_obj.cedula):
                        self.inv_crud.create(inv_obj)

                # Si no había investigadores pero hay productos, asegurar un investigador receptor
                prod_list = datos.get("productos", [])
                if not primary_cedula and prod_list:
                    existing_invs = self.inv_crud.list_by_group(gid)
                    if existing_invs:
                        primary_cedula = getattr(existing_invs[0], 'cedula', None)
                    else:
                        fallback_inv = Investigador(
                            cedula=f"INV-{gid}",
                            nombres=getattr(grupo_obj, 'lider', 'Investigador Principal') or 'Investigador Principal',
                            grupo_id=gid,
                            activo=True,
                        )
                        self.inv_crud.create(fallback_inv)
                        primary_cedula = fallback_inv.cedula

                # 3. Insertar Productos
                for p_raw in prod_list:
                    if isinstance(p_raw, dict):
                        p_ced = p_raw.get("investigador_cedula") or p_raw.get("investigador_id") or p_raw.get("cedula") or primary_cedula
                        p_obj = Producto(
                            id=p_raw.get("id"),
                            titulo=p_raw.get("titulo") or p_raw.get("title", ""),
                            tipo=p_raw.get("tipo") or p_raw.get("type", ""),
                            categoria=p_raw.get("categoria", ""),
                            validado=p_raw.get("validado", p_raw.get("active", True)),
                            anio=int(p_raw.get("anio") or p_raw.get("year") or 0),
                            investigador_id=p_ced,
                            grupo_id=gid,
                            raw=p_raw.get("raw"),
                        )
                    elif isinstance(p_raw, Producto):
                        p_obj = p_raw
                        if not getattr(p_obj, 'investigador_id', None):
                            p_obj.investigador_id = primary_cedula
                        if not getattr(p_obj, 'grupo_id', None):
                            p_obj.grupo_id = gid
                    else:
                        continue
                    self.prod_crud.create(p_obj)

            self.save_data(silent=True)
            self.load_tabs_data()

            # Obtención de nombres y conteos para la notificación
            nombre_grupo = ""
            if grupo_obj:
                nombre_grupo = getattr(grupo_obj, 'nombre', '')
            if not nombre_grupo:
                todos_grupos = self.grupo_crud.list_all()
                if todos_grupos:
                    g0 = todos_grupos[0]
                    nombre_grupo = getattr(g0, 'nombre', '') or getattr(g0, 'name', '') or str(getattr(g0, 'id', ''))
                elif isinstance(datos, dict) and "grupo" in datos and isinstance(datos["grupo"], dict):
                    nombre_grupo = datos["grupo"].get("nombre", datos["grupo"].get("name", ""))

            num_inv = len(self.inv_crud.list_all())
            num_prod = len(self.prod_crud.list_all())

            messagebox.showinfo(
                "Éxito",
                f"Grupo descargado: {nombre_grupo}. Investigadores: {num_inv}. Productos: {num_prod}.",
            )
            self.update_status("Descarga completada.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar los datos descargados: {e}")

    def load_from_csv(self, path: str = None):
        """Carga datos de grupos, investigadores y productos desde un archivo CSV."""
        try:
            if not path:
                path = filedialog.askopenfilename(
                    filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
                    title="Seleccionar archivo CSV",
                )
            if not path:
                return

            datos = scienti.download_from_csv(path)
            if not datos or (isinstance(datos, dict) and "error" in datos):
                messagebox.showerror("Error", "No se pudo procesar el archivo CSV")
                return

            new_multilist = PersistenciaJSON.to_multilist(datos)
            if new_multilist and not new_multilist.is_empty():
                self.multilista = new_multilist
                self.grupo_crud = GrupoCRUD(self.multilista)
                self.inv_crud = InvestigadorCRUD(self.multilista)
                self.prod_crud = ProductoCRUD(self.multilista)

            self.save_data(silent=True)
            self.load_tabs_data()
            messagebox.showinfo("Éxito", "Datos cargados correctamente desde CSV.")
            self.update_status("Descarga completada.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar el archivo CSV: {e}")

    def load_csv(self, path: str = None):
        """Alias para load_from_csv."""
        self.load_from_csv(path)

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
                if 'grupos' in datos and datos['grupos'] and isinstance(datos['grupos'][0], dict) and 'grupo' in datos['grupos'][0]:
                    self.multilista = PersistenciaJSON.to_multilist(datos)
                else:
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

    def save_data(self, silent: bool = False):
        """Guarda la estructura actual en la capa de persistencia activa."""
        try:
            self.persistencia.save(self.multilista)
            if not silent:
                messagebox.showinfo("Guardar", "Datos guardados correctamente")
        except Exception:
            try:
                datos = {
                    'grupos': [g.to_dict() if hasattr(g, 'to_dict') else g.__dict__ for g in self.grupo_crud.list_all()],
                    'investigadores': [i.to_dict() if hasattr(i, 'to_dict') else i.__dict__ for i in self.inv_crud.list_all()],
                    'productos': [p.to_dict() if hasattr(p, 'to_dict') else p.__dict__ for p in self.prod_crud.list_all()],
                }
                self.persistencia.save(datos)
                if not silent:
                    messagebox.showinfo("Guardar", "Datos guardados correctamente")
            except Exception as ex:
                if not silent:
                    messagebox.showerror("Error", f"No se pudo guardar la información: {ex}")

    def about(self):
        """Muestra ventana modal con información sobre la aplicación."""
        messagebox.showinfo(
            "Acerca de",
            "PEA-i (Programa Estadístico de Análisis de Investigación)\n\n"
            "Taller de Estructura de Datos - Segundo Corte\n"
            "Diseñado con CustomTkinter y arquitectura de Multilistas.",
        )

    def has_data(self) -> bool:
        """Indica si existen registros cargados en memoria."""
        try:
            return bool(
                (self.grupo_crud and self.grupo_crud.list_all()) or
                (self.inv_crud and self.inv_crud.list_all()) or
                (self.prod_crud and self.prod_crud.list_all())
            )
        except Exception:
            return False

    def export_to_excel(self):
        """Exporta los datos de grupos, investigadores y productos a un archivo Excel (.xlsx)."""
        if not self.has_data():
            messagebox.showwarning("Exportar a Excel", "No hay datos para exportar.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Libro de Excel", "*.xlsx"), ("Todos los archivos", "*.*")],
            title="Exportar datos a Excel",
            initialfile="datos_investigacion.xlsx",
        )
        if not filepath:
            return

        try:
            grupos_data = [g.to_dict() if hasattr(g, 'to_dict') else g.__dict__ for g in self.grupo_crud.list_all()]
            invs_data = [i.to_dict() if hasattr(i, 'to_dict') else i.__dict__ for i in self.inv_crud.list_all()]
            prods_data = [p.to_dict() if hasattr(p, 'to_dict') else p.__dict__ for p in self.prod_crud.list_all()]

            import pandas as pd
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                pd.DataFrame(grupos_data).to_excel(writer, sheet_name='Grupos', index=False)
                pd.DataFrame(invs_data).to_excel(writer, sheet_name='Investigadores', index=False)
                pd.DataFrame(prods_data).to_excel(writer, sheet_name='Productos', index=False)

            messagebox.showinfo("Exportación exitosa", f"Datos exportados correctamente en:\n{filepath}")
            self.update_status(f"Exportado a Excel: {Path(filepath).name}")
        except Exception as e:
            messagebox.showerror("Error de exportación", f"No se pudo exportar a Excel:\n{e}")

    def export_to_csv(self):
        """Exporta los datos de grupos, investigadores y productos a archivos CSV en una carpeta."""
        if not self.has_data():
            messagebox.showwarning("Exportar a CSV", "No hay datos para exportar.")
            return

        directory = filedialog.askdirectory(title="Seleccionar carpeta para guardar archivos CSV")
        if not directory:
            return

        try:
            import csv
            grupos_data = [g.to_dict() if hasattr(g, 'to_dict') else g.__dict__ for g in self.grupo_crud.list_all()]
            invs_data = [i.to_dict() if hasattr(i, 'to_dict') else i.__dict__ for i in self.inv_crud.list_all()]
            prods_data = [p.to_dict() if hasattr(p, 'to_dict') else p.__dict__ for p in self.prod_crud.list_all()]

            def _write(name, rows):
                if not rows:
                    return
                p = Path(directory) / f"{name}.csv"
                keys = list(rows[0].keys())
                with open(p, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=keys)
                    writer.writeheader()
                    writer.writerows(rows)

            _write("grupos", grupos_data)
            _write("investigadores", invs_data)
            _write("productos", prods_data)

            messagebox.showinfo(
                "Exportación exitosa",
                f"Archivos CSV exportados correctamente en:\n{directory}",
            )
            self.update_status("Exportación CSV completada.")
        except Exception as e:
            messagebox.showerror("Error de exportación", f"No se pudo exportar a CSV:\n{e}")

    def refresh_all(self):
        """Recarga los datos de persistencia y actualiza todas las pestañas de la interfaz."""
        self.load_data()
        self.update_status("Vistas actualizadas correctamente.")

    def clear_data(self):
        """Limpia todos los datos cargados en memoria y persiste el estado vacío."""
        if not self.has_data():
            messagebox.showinfo("Limpiar datos", "No hay datos para limpiar.")
            return

        confirm = messagebox.askyesno(
            "Confirmar limpieza",
            "¿Está seguro de que desea limpiar todos los datos del sistema?\nEsta acción no se puede deshacer.",
            icon='warning',
        )
        if not confirm:
            return

        self.multilista = Multilist()
        self.grupo_crud = GrupoCRUD(self.multilista)
        self.inv_crud = InvestigadorCRUD(self.multilista)
        self.prod_crud = ProductoCRUD(self.multilista)
        self.save_data(silent=True)
        self.load_tabs_data()
        self.update_status("Todos los datos han sido limpiados.")
        messagebox.showinfo("Limpieza completada", "Se han limpiado todos los registros del sistema.")

    def show_quick_guide(self):
        """Muestra una guía rápida de uso y atajos de teclado del sistema."""
        guia = (
            "PEA-i - Guía Rápida de Uso\n\n"
            "1. Menú Archivo:\n"
            "  - Cargar datos (Ctrl+O): Recarga la información desde el archivo JSON local.\n"
            "  - Guardar datos (Ctrl+S): Guarda el estado actual en disco.\n"
            "  - Exportar a Excel (Ctrl+E): Genera un libro .xlsx con Grupos, Investigadores y Productos.\n"
            "  - Exportar a CSV (Ctrl+Shift+C): Genera archivos .csv independientes.\n"
            "  - Salir (Ctrl+Q): Cierra la aplicación.\n\n"
            "2. Menú Datos:\n"
            "  - Descargar del SCIENTI (Ctrl+U): Descarga directa del grupo oficial de MinCiencias.\n"
            "  - Descargar de otra URL... (Ctrl+Shift+U): Solicita una URL para descargar e indexar.\n"
            "  - Actualizar todo (F5): Refresca las listas, tablas y estadísticas.\n"
            "  - Limpiar datos (Ctrl+Shift+Del): Restablece todas las estructuras en memoria.\n\n"
            "3. Menú Ayuda:\n"
            "  - Guía rápida (F1): Muestra esta guía informativa.\n"
            "  - Acerca de (Ctrl+H): Información de versión y créditos."
        )
        messagebox.showinfo("Guía Rápida - PEA-i", guia)


MainWindow = App


def main():
    """Punto de entrada de la interfaz gráfica."""
    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()