# -*- coding: utf-8 -*-
"""Ventana principal de la aplicación PEA-i (Sistema de Gestión de Investigación - Unicesar)."""

import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
import tkinter as tk
from tkinter import messagebox, filedialog

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
from gui.styles import (
    COLORS,
    RADIUS,
    SPACING,
    ICONS,
    FONT_FAMILY,
    font,
    setup_app,
    tarjeta,
)
from scraping import scienti

_TAB_NAMES = ["Grupos", "Investigadores", "Productos", "Estadísticas"]


class App(ctk.CTk):
    """Aplicación principal de escritorio PEA-i con navegación lateral única y diseño Unicesar."""

    SECTION_METADATA = {
        "Grupos": {
            "icon": ICONS["grupos"],
            "title": "Grupos de investigación",
            "subtitle": "Gestión, clasificación y seguimiento de grupos registrados en MinCiencias",
        },
        "Investigadores": {
            "icon": ICONS["investigadores"],
            "title": "Investigadores",
            "subtitle": "Directorio de integrantes, líderes y vinculación académica",
        },
        "Productos": {
            "icon": ICONS["productos"],
            "title": "Productos de investigación",
            "subtitle": "Artículos, libros, capítulos, software y producciones científicas",
        },
        "Estadísticas": {
            "icon": ICONS["estadisticas"],
            "title": "Panel de estadísticas",
            "subtitle": "Indicadores clave, distribución temporal y métricas de producción",
        },
    }

    def __init__(self):
        super().__init__()

        # Configuración del sistema de diseño institucional
        setup_app(self)

        self.title("PEA-i · Sistema de Gestión de Investigación - Unicesar")
        self.geometry("1280x760")
        self.minsize(1200, 700)

        # Inicialización de modelos de datos y CRUDs
        self.persistencia = None
        self.multilista = Multilist()
        self.grupo_crud = GrupoCRUD(self.multilista)
        self.inv_crud = InvestigadorCRUD(self.multilista)
        self.prod_crud = ProductoCRUD(self.multilista)

        self._last_saved: str = ""
        self._status_toast_timer = None

        # Variables para el panel flotante "Más opciones"
        self._options_panel: Optional[ctk.CTkFrame] = None
        self._options_bind_id: Optional[str] = None

        self.init_persistence()

        # ── Estructura General ──────────────────────────────────────────
        # 1. Barra lateral izquierda (ancho ~259 px, fondo #0F1B3D)
        self._build_sidebar()

        # 2. Contenedor principal derecho (header azul + tarjeta blanca)
        self._build_main_container()

        # 3. Montar vistas dentro de la tarjeta blanca
        self._build_views()

        # Atajos de teclado y listeners globales
        self._bind_global_events()

        # Iniciar en la primera sección y cargar datos
        self.navigate_to(_TAB_NAMES[0])
        self.load_data()

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║  1. BARRA LATERAL IZQUIERDA (Sidebar, 259 px)                   ║
    # ╚══════════════════════════════════════════════════════════════════╝

    def _build_sidebar(self):
        """Construye la barra lateral izquierda como la ÚNICA navegación de la aplicación."""
        self.sidebar = ctk.CTkFrame(
            self,
            width=259,
            fg_color=COLORS["sidebar"],
            corner_radius=0,
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo y texto institucional en la parte superior
        self.brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.brand_frame.pack(fill="x", padx=20, pady=(24, 16))

        self.logo_title = ctk.CTkLabel(
            self.brand_frame,
            text="UNICESAR",
            font=(FONT_FAMILY, 20, "bold"),
            text_color="#FFFFFF",
            anchor="w",
        )
        self.logo_title.pack(fill="x")

        self.logo_sub = ctk.CTkLabel(
            self.brand_frame,
            text="Universidad Popular del Cesar",
            font=(FONT_FAMILY, 11),
            text_color="#94A3B8",
            anchor="w",
        )
        self.logo_sub.pack(fill="x", pady=(2, 0))

        # Divisor sutil
        self.sidebar_sep = ctk.CTkFrame(self.sidebar, height=1, fg_color=COLORS["sidebar_border"])
        self.sidebar_sep.pack(fill="x", padx=16, pady=(0, 16))

        # Ítems de navegación (Grupos, Investigadores, Productos, Estadísticas)
        self.nav_buttons: Dict[str, ctk.CTkButton] = {}
        for name in _TAB_NAMES:
            meta = self.SECTION_METADATA[name]
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {meta['icon']}   {name}",
                height=44,
                corner_radius=8,
                anchor="w",
                font=font("body"),
                fg_color="transparent",
                hover_color=COLORS["sidebar_hover"],
                text_color=COLORS["sidebar_text"],
                command=lambda n=name: self.navigate_to(n),
            )
            btn.pack(fill="x", padx=16, pady=4)
            self.nav_buttons[name] = btn

        # Bloque inferior de usuario institucional y botón "Más opciones"
        self._build_user_block()

    def _build_user_block(self):
        """Construye el bloque de usuario en la base de la barra lateral con botón de más opciones."""
        self.user_block_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.user_block_frame.pack(side="bottom", fill="x", padx=16, pady=16)

        # Línea divisoria superior del bloque de usuario
        self.user_sep = ctk.CTkFrame(self.sidebar, height=1, fg_color=COLORS["sidebar_border"])
        self.user_sep.pack(side="bottom", fill="x", padx=16, pady=(0, 8))

        self.user_row = ctk.CTkFrame(self.user_block_frame, fg_color="transparent")
        self.user_row.pack(fill="x")

        # Círculo de avatar con ícono
        self.avatar_circle = ctk.CTkLabel(
            self.user_row,
            text=ICONS["usuario"],
            width=36,
            height=36,
            corner_radius=18,
            fg_color="#1E293B",
            text_color="#FFFFFF",
            font=(FONT_FAMILY, 15),
        )
        self.avatar_circle.pack(side="left", padx=(0, 10))

        # Textos de usuario
        self.user_info_frame = ctk.CTkFrame(self.user_row, fg_color="transparent")
        self.user_info_frame.pack(side="left", fill="both", expand=True)

        self.user_system_lbl = ctk.CTkLabel(
            self.user_info_frame,
            text="Sistema de Investigación",
            font=(FONT_FAMILY, 11, "bold"),
            text_color="#FFFFFF",
            anchor="w",
        )
        self.user_system_lbl.pack(fill="x")

        self.user_sub_lbl = ctk.CTkLabel(
            self.user_info_frame,
            text="Unicesar",
            font=(FONT_FAMILY, 10),
            text_color="#94A3B8",
            anchor="w",
        )
        self.user_sub_lbl.pack(fill="x")

        # Botón "Más opciones" (reemplaza el menú superior flotante por panel integrado)
        self.btn_more_options = ctk.CTkButton(
            self.user_row,
            text=ICONS["acciones"],
            width=32,
            height=32,
            corner_radius=6,
            fg_color="transparent",
            hover_color=COLORS["sidebar_hover"],
            text_color="#CBD5E1",
            font=(FONT_FAMILY, 14, "bold"),
            command=self._toggle_more_options_panel,
        )
        self.btn_more_options.pack(side="right")

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║  2. CONTENEDOR PRINCIPAL DERECHO (Header + Tarjeta)              ║
    # ╚══════════════════════════════════════════════════════════════════╝

    def _build_main_container(self):
        """Construye el área derecha: encabezado azul dinámico y área central."""
        self.right_container = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=0)
        self.right_container.pack(side="right", fill="both", expand=True)

        # Encabezado azul (#1E3A8A, alto ~105 px)
        self.header_frame = ctk.CTkFrame(
            self.right_container,
            height=105,
            fg_color=COLORS["header"],
            corner_radius=0,
        )
        self.header_frame.pack(side="top", fill="x")
        self.header_frame.pack_propagate(False)

        # Contenido izquierdo del encabezado: ícono grande, título y subtítulo dinámicos
        self.header_left = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.header_left.pack(side="left", fill="y", padx=24, pady=16)

        self.header_icon_lbl = ctk.CTkLabel(
            self.header_left,
            text=ICONS["grupos"],
            font=(FONT_FAMILY, 28),
            text_color=COLORS["header_text"],
        )
        self.header_icon_lbl.pack(side="left", padx=(0, 16))

        self.header_text_frame = ctk.CTkFrame(self.header_left, fg_color="transparent")
        self.header_text_frame.pack(side="left", fill="y")

        self.header_title_lbl = ctk.CTkLabel(
            self.header_text_frame,
            text="Grupos de investigación",
            font=(FONT_FAMILY, 22, "bold"),
            text_color=COLORS["header_text"],
            anchor="w",
        )
        self.header_title_lbl.pack(anchor="w")

        self.header_sub_lbl = ctk.CTkLabel(
            self.header_text_frame,
            text="Gestión, clasificación y seguimiento de grupos registrados en MinCiencias",
            font=(FONT_FAMILY, 12),
            text_color=COLORS["header_sub"],
            anchor="w",
        )
        self.header_sub_lbl.pack(anchor="w", pady=(3, 0))

        # Contenido derecho del encabezado: toast y badge de estado
        self.header_right = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.header_right.pack(side="right", fill="y", padx=24, pady=16)

        self.toast_lbl = ctk.CTkLabel(
            self.header_right,
            text="",
            font=font("body_bold"),
            text_color="#86EFAC",
            anchor="e",
        )
        self.toast_lbl.pack(side="top", anchor="e", pady=(2, 0))

        self.status_count_lbl = ctk.CTkLabel(
            self.header_right,
            text="0 grupos · 0 inv. · 0 prod.",
            font=font("small"),
            text_color=COLORS["header_sub"],
            anchor="e",
        )
        self.status_count_lbl.pack(side="top", anchor="e", pady=(4, 0))

        # Área de contenido con margen de 24 px
        self.content_area = ctk.CTkFrame(self.right_container, fg_color="transparent")
        self.content_area.pack(fill="both", expand=True, padx=24, pady=24)

        # Tarjeta blanca principal (radio 12, borde #E5E7EB)
        self.card_container = tarjeta(self.content_area, corner_radius=RADIUS["card"])
        self.card_container.pack(fill="both", expand=True)

    def _build_views(self):
        """Monta los frames contenedores para cada pantalla dentro de la tarjeta blanca."""
        self._tab_frames = {}
        for name in _TAB_NAMES:
            frame = ctk.CTkFrame(self.card_container, fg_color="transparent")
            self._tab_frames[name] = frame

        # Inyección de dependencias en las pestañas
        self.grupos_tab = GruposTab(self._tab_frames["Grupos"], app=self)
        self.investigadores_tab = InvestigadoresTab(self._tab_frames["Investigadores"], app=self)
        self.productos_tab = ProductosTab(self._tab_frames["Productos"], app=self)
        self.estadisticas_tab = EstadisticasTab(self._tab_frames["Estadísticas"], app=self)

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║  3. NAVEGACIÓN Y ENCABEZADO DINÁMICO                           ║
    # ╚══════════════════════════════════════════════════════════════════╝

    def navigate_to(self, section_name: str):
        """Navega a la sección indicada, actualizando la barra lateral y el encabezado."""
        if section_name not in self._tab_frames:
            return

        self._close_more_options_panel()
        self._current_tab = section_name

        # 1. Actualizar apariencia de botones en la barra lateral
        for name, btn in self.nav_buttons.items():
            if name == section_name:
                btn.configure(
                    fg_color=COLORS["sidebar_active"],
                    hover_color=COLORS["sidebar_active"],
                    text_color=COLORS["sidebar_text_active"],
                    font=font("body_bold"),
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    hover_color=COLORS["sidebar_hover"],
                    text_color=COLORS["sidebar_text"],
                    font=font("body"),
                )

        # 2. Actualizar encabezado azul dinámicamente
        meta = self.SECTION_METADATA.get(section_name, {
            "icon": ICONS.get(section_name.lower(), "📁"),
            "title": section_name,
            "subtitle": "",
        })
        self.header_icon_lbl.configure(text=meta["icon"])
        self.header_title_lbl.configure(text=meta["title"])
        self.header_sub_lbl.configure(text=meta["subtitle"])

        # 3. Mostrar la vista seleccionada dentro de la tarjeta blanca
        for name, frame in self._tab_frames.items():
            if name == section_name:
                frame.pack(fill="both", expand=True)
            else:
                frame.pack_forget()

        # Si se navega a Estadísticas, refrescar los gráficos
        if section_name == "Estadísticas" and hasattr(self, "estadisticas_tab"):
            try:
                self.estadisticas_tab.refresh()
            except Exception:
                pass

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║  4. PANEL FLOTANTE "MÁS OPCIONES" (place + lift)               ║
    # ╚══════════════════════════════════════════════════════════════════╝

    def _toggle_more_options_panel(self):
        """Abre o cierra el panel emergente de opciones sobre el bloque de usuario."""
        if self._options_panel is not None:
            self._close_more_options_panel()
            return

        try:
            # Crear panel como CTkFrame hijo directo de la ventana raíz
            panel = ctk.CTkFrame(
                self,
                fg_color=COLORS["surface"],
                border_width=1,
                border_color=COLORS["border"],
                corner_radius=RADIUS["card"],
            )
            self._options_panel = panel

            content = ctk.CTkFrame(panel, fg_color="transparent")
            content.pack(fill="both", expand=True, padx=6, pady=6)

            opciones = [
                ("Cargar datos", "📂", self.load_data, True),
                ("Guardar datos", "💾", self.save_data, self.has_data),
                ("Exportar a CSV", "📊", self.export_to_csv, self.has_data),
                ("Cargar CSV/PDF", "📄", self.load_from_csv, True),
                ("Descargar de otra URL", "🔗", self.download_from_custom_url, True),
                ("Limpiar datos", "🗑️", self.clear_data, self.has_data),
                (None, None, None, None),  # Separador
                ("Guía rápida", "📖", self.show_quick_guide, True),
                ("Acerca de PEA-i", "ℹ️", self.about, True),
            ]

            for label, icon, cmd, enabled_val in opciones:
                if label is None:
                    sep = ctk.CTkFrame(content, height=1, fg_color=COLORS["border"], corner_radius=0)
                    sep.pack(fill="x", padx=4, pady=4)
                    continue

                is_enabled = enabled_val() if callable(enabled_val) else bool(enabled_val)
                row = ctk.CTkFrame(content, height=32, corner_radius=6, fg_color="transparent")
                row.pack(fill="x", pady=1)

                icon_lbl = ctk.CTkLabel(
                    row,
                    text=icon,
                    width=26,
                    font=("Segoe UI Emoji", 12),
                    text_color=COLORS["ink"] if is_enabled else COLORS["muted_light"],
                    anchor="center",
                )
                icon_lbl.pack(side="left", padx=(6, 4))

                text_lbl = ctk.CTkLabel(
                    row,
                    text=label,
                    font=font("body"),
                    text_color=COLORS["ink"] if is_enabled else COLORS["muted_light"],
                    anchor="w",
                )
                text_lbl.pack(side="left", padx=(4, 16), fill="x", expand=True)

                if is_enabled:
                    for w in (row, icon_lbl, text_lbl):
                        w.bind("<Enter>", lambda e, r=row: r.configure(fg_color=COLORS["surface_alt"]))
                        w.bind("<Leave>", lambda e, r=row: r.configure(fg_color="transparent"))
                        w.bind("<Button-1>", lambda e, c=cmd: self._exec_option_and_close(c))

            panel.update_idletasks()
            panel_w = max(230, panel.winfo_reqwidth())
            panel_h = panel.winfo_reqheight()

            # Posicionar sobre el bloque de usuario hacia arriba dentro de la barra lateral
            px = 16
            btn_root_y = self.btn_more_options.winfo_rooty() - self.winfo_rooty()
            py = max(16, btn_root_y - panel_h - 8)

            panel.place(x=px, y=py)
            panel.lift()

            # Diferir el listener de clic fuera para no capturar el clic actual
            self.after(50, self._enable_options_click_outside)
        except Exception:
            pass

    def _exec_option_and_close(self, command: Optional[Callable]):
        """Ejecuta una acción del panel de opciones y lo cierra."""
        self._close_more_options_panel()
        if command:
            self.after(10, command)

    def _close_more_options_panel(self):
        """Cierra el panel emergente de opciones si está abierto."""
        if self._options_bind_id:
            try:
                self.unbind("<Button-1>", self._options_bind_id)
            except Exception:
                pass
            self._options_bind_id = None

        if self._options_panel is not None:
            try:
                self._options_panel.place_forget()
                self._options_panel.destroy()
            except Exception:
                pass
            self._options_panel = None

    def _enable_options_click_outside(self):
        """Activa la detección de clic fuera cuando el panel está visible."""
        if self._options_panel is not None and self._options_bind_id is None:
            self._options_bind_id = self.bind("<Button-1>", self._on_options_click_outside, add="+")

    def _on_options_click_outside(self, event):
        """Cierra el panel de opciones si se hace clic fuera de él."""
        if not self._options_panel:
            return

        # 1. Comprobar si el clic cayó dentro del panel
        try:
            px = self._options_panel.winfo_rootx()
            py = self._options_panel.winfo_rooty()
            pw = self._options_panel.winfo_width()
            ph = self._options_panel.winfo_height()
            if px <= event.x_root <= px + pw and py <= event.y_root <= py + ph:
                return
        except Exception:
            pass

        # 2. Comprobar si cayó en el botón activador
        try:
            bx = self.btn_more_options.winfo_rootx()
            by = self.btn_more_options.winfo_rooty()
            bw = self.btn_more_options.winfo_width()
            bh = self.btn_more_options.winfo_height()
            if bx <= event.x_root <= bx + bw and by <= event.y_root <= by + bh:
                return
        except Exception:
            pass

        self._close_more_options_panel()

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║  5. PERSISTENCIA Y OPERACIONES CRUD                            ║
    # ╚══════════════════════════════════════════════════════════════════╝

    def init_persistence(self):
        """Inicializa la persistencia directa con archivo JSON."""
        datos_path = Path(__file__).resolve().parent.parent / "datos" / "datos.json"
        self.persistencia = PersistenciaJSON(filepath=str(datos_path))

    def has_data(self) -> bool:
        """Indica si existen grupos cargados en la multilista."""
        return len(self.grupo_crud.list_all()) > 0

    def load_data(self):
        """Carga y sincroniza los datos persistidos en memoria y actualiza pestañas."""
        try:
            datos = self.persistencia.load()
            if isinstance(datos, dict):
                if "grupos" in datos and datos["grupos"] and isinstance(datos["grupos"][0], dict) and "grupo" in datos["grupos"][0]:
                    self.multilista = PersistenciaJSON.to_multilist(datos)
                else:
                    self.multilista = Multilist()
                    self.grupo_crud = GrupoCRUD(self.multilista)
                    self.inv_crud = InvestigadorCRUD(self.multilista)
                    self.prod_crud = ProductoCRUD(self.multilista)

                    for g in datos.get("grupos", []):
                        if isinstance(g, dict):
                            grupo_obj = Grupo(
                                id=g.get("id"),
                                codigo_gruplac=g.get("code") or g.get("codigo_gruplac", ""),
                                nombre=g.get("name") or g.get("nombre", ""),
                                categoria=g.get("category") or g.get("categoria", ""),
                                lider=g.get("leader") or g.get("lider", ""),
                                activo=g.get("active", g.get("activo", True)),
                                fecha_creacion=g.get("fecha_creacion", ""),
                            )
                        else:
                            grupo_obj = g
                        try:
                            self.grupo_crud.create(grupo_obj)
                        except Exception:
                            pass

                    inv_id_to_cedula = {}
                    for i in datos.get("investigadores", []):
                        if isinstance(i, dict):
                            inv_obj = Investigador(
                                id=i.get("id"),
                                cedula=str(i.get("cedula") or i.get("id") or ""),
                                nombres=i.get("name") or i.get("nombres", ""),
                                apellidos=i.get("apellidos", ""),
                                email=i.get("email", ""),
                                activo=i.get("active", i.get("activo", True)),
                                grupo_id=i.get("grupo_id") or i.get("group"),
                            )
                        else:
                            inv_obj = i
                        if hasattr(inv_obj, "id"):
                            inv_id_to_cedula[inv_obj.id] = getattr(inv_obj, "cedula", str(inv_obj.id))
                        try:
                            self.inv_crud.create(inv_obj)
                        except Exception:
                            pass

                    for p in datos.get("productos", []):
                        if isinstance(p, dict):
                            try:
                                anio_val = int(p.get("year") or p.get("anio") or 0)
                            except ValueError:
                                anio_val = 0
                            inv_id_val = p.get("investigador_id")
                            cedula_val = p.get("investigador_cedula") or inv_id_to_cedula.get(inv_id_val) or str(inv_id_val)
                            prod_obj = Producto(
                                id=p.get("id"),
                                titulo=p.get("title") or p.get("titulo", ""),
                                tipo=p.get("type") or p.get("tipo", ""),
                                categoria=p.get("categoria", ""),
                                validado=p.get("active", p.get("validado", True)),
                                anio=anio_val,
                                investigador_id=inv_id_val,
                                grupo_id=p.get("grupo_id") or p.get("group"),
                                gran_categoria=p.get("gran_categoria", "Sin clasificar"),
                                codigo_minciencias=p.get("codigo_minciencias", ""),
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
            self._last_saved = datetime.now().strftime("%H:%M:%S")
            self._refresh_status_bar()
            if not silent:
                self.show_toast("Datos guardados correctamente")
        except Exception:
            try:
                datos = {
                    "grupos": [g.to_dict() if hasattr(g, "to_dict") else g.__dict__ for g in self.grupo_crud.list_all()],
                    "investigadores": [i.to_dict() if hasattr(i, "to_dict") else i.__dict__ for i in self.inv_crud.list_all()],
                    "productos": [p.to_dict() if hasattr(p, "to_dict") else p.__dict__ for p in self.prod_crud.list_all()],
                }
                self.persistencia.save(datos)
                self._last_saved = datetime.now().strftime("%H:%M:%S")
                self._refresh_status_bar()
                if not silent:
                    self.show_toast("Datos guardados correctamente")
            except Exception as ex:
                if not silent:
                    messagebox.showerror("Error", f"No se pudo guardar la información: {ex}")

    def load_tabs_data(self):
        """Refresca la información visible en cada una de las pantallas."""
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
        self._refresh_status_bar()

    def _refresh_status_bar(self):
        """Actualiza los indicadores numéricos en el encabezado."""
        try:
            ng = len(self.grupo_crud.list_all())
            ni = len(self.inv_crud.list_all())
            np_ = len(self.prod_crud.list_all())
            self.status_count_lbl.configure(
                text=f"{ng} grupo{'s' if ng != 1 else ''} · {ni} inv. · {np_} prod."
            )
        except Exception:
            pass

    def show_toast(self, message: str, duration_ms: int = 4000, color: str = ""):
        """Muestra un mensaje temporal en el encabezado azul."""
        if self._status_toast_timer:
            try:
                self.after_cancel(self._status_toast_timer)
            except Exception:
                pass

        toast_color = color or "#86EFAC"
        self.toast_lbl.configure(text=f"✓ {message}", text_color=toast_color)
        self._status_toast_timer = self.after(duration_ms, self._clear_toast)

    def _clear_toast(self):
        """Limpia el mensaje temporal del encabezado."""
        try:
            self.toast_lbl.configure(text="")
        except Exception:
            pass
        self._status_toast_timer = None

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║  6. DESCARGA Y WEB SCRAPING SCIENTI                            ║
    # ╚══════════════════════════════════════════════════════════════════╝

    def download_scienti(self):
        """Descarga directa del SCIENTI con la URL oficial por defecto."""
        self.download_from_url(DEFAULT_SCIENTI_URL)

    def download_from_url(self, url: str):
        """Descarga e integra la información de un grupo desde la URL en hilo secundario."""
        if not url or not (url.startswith("http://") or url.startswith("https://")):
            messagebox.showerror("Error", "URL inválida.")
            return

        self.show_toast("Descargando desde SCIENTI...", duration_ms=30000, color="#FDE047")
        self.update()

        def _worker():
            try:
                datos = scienti.download_group(url)
            except Exception as e:
                datos = {"error": f"Error de conexión: {e}"}
            self.after(0, lambda: self._on_download_complete(datos, url))

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()

    def _on_download_complete(self, datos, url: str):
        """Callback al terminar la descarga."""
        if not datos or (isinstance(datos, dict) and "error" in datos):
            error_msg = datos.get("error", "Error al descargar.") if isinstance(datos, dict) else "Error al descargar."
            self.show_toast("Error al descargar", color="#FCA5A5")
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
                        gid = getattr(existing, "id", gid)
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
                            id=inv_raw.get("id") or ced,
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
                        primary_cedula = getattr(inv_obj, "cedula", None)
                    if not self.inv_crud.get_by_cedula(inv_obj.cedula):
                        self.inv_crud.create(inv_obj)

                # Si no había investigadores pero hay productos, asegurar investigador receptor
                prod_list = datos.get("productos", [])
                if not primary_cedula and prod_list:
                    existing_invs = self.inv_crud.list_by_group(gid)
                    if existing_invs:
                        primary_cedula = getattr(existing_invs[0], "cedula", None)
                    else:
                        fallback_inv = Investigador(
                            cedula=f"INV-{gid}",
                            nombres=getattr(grupo_obj, "lider", "Investigador Principal") or "Investigador Principal",
                            grupo_id=gid,
                            activo=True,
                        )
                        self.inv_crud.create(fallback_inv)
                        primary_cedula = fallback_inv.cedula

                # 3. Insertar Productos
                for p_raw in prod_list:
                    if isinstance(p_raw, dict):
                        p_ced = p_raw.get("investigador_cedula") or p_raw.get("investigador_id") or p_raw.get("cedula")
                        if not p_ced or not self.inv_crud.get_by_cedula(p_ced):
                            p_ced = primary_cedula

                        pid = p_raw.get("id") or f"PRD-{len(self.prod_crud.list_all()) + 1}"
                        p_obj = Producto(
                            id=pid,
                            titulo=p_raw.get("titulo") or p_raw.get("title", ""),
                            tipo=p_raw.get("tipo") or p_raw.get("type", ""),
                            categoria=p_raw.get("categoria", ""),
                            validado=p_raw.get("validado", p_raw.get("active", True)),
                            anio=int(p_raw.get("anio") or p_raw.get("year") or 0),
                            investigador_id=p_ced,
                            grupo_id=gid,
                            raw=p_raw.get("raw"),
                            gran_categoria=p_raw.get("gran_categoria", "Sin clasificar"),
                            codigo_minciencias=p_raw.get("codigo_minciencias", ""),
                        )
                        p_obj.investigador_cedula = p_ced
                    elif isinstance(p_raw, Producto):
                        p_obj = p_raw
                        if not getattr(p_obj, "investigador_id", None) or not self.inv_crud.get_by_cedula(p_obj.investigador_id):
                            p_obj.investigador_id = primary_cedula
                        if not getattr(p_obj, "grupo_id", None):
                            p_obj.grupo_id = gid
                        if not getattr(p_obj, "id", None):
                            p_obj.id = f"PRD-{len(self.prod_crud.list_all()) + 1}"
                    else:
                        continue
                    self.prod_crud.create(p_obj)

            self.save_data(silent=True)
            self.load_tabs_data()

            nombre_grupo = ""
            if grupo_obj:
                nombre_grupo = getattr(grupo_obj, "nombre", "")
            if not nombre_grupo:
                todos_grupos = self.grupo_crud.list_all()
                if todos_grupos:
                    g0 = todos_grupos[0]
                    nombre_grupo = getattr(g0, "nombre", "") or str(getattr(g0, "id", ""))
                elif isinstance(datos, dict) and "grupo" in datos and isinstance(datos["grupo"], dict):
                    nombre_grupo = datos["grupo"].get("nombre", "")

            num_inv = len(self.inv_crud.list_all())
            num_prod = len(self.prod_crud.list_all())

            resumen_info = datos.get("resumen", "")
            secciones_vacias = datos.get("secciones_vacias", [])
            msg_vacias = f"\n\nSecciones vacías: {', '.join(secciones_vacias[:5])}" if secciones_vacias else ""

            messagebox.showinfo(
                "Éxito",
                f"Grupo descargado: {nombre_grupo}.\nInvestigadores en sistema: {num_inv}.\nProductos en sistema: {num_prod}.{msg_vacias}",
            )
            self.show_toast(f"Descarga completada ({num_inv} inv. · {num_prod} prod.)")
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar los datos descargados: {e}")

    def download_from_custom_url(self):
        """Abre el modal para ingresar una URL personalizada."""
        self._close_more_options_panel()
        UrlImportModal(
            parent=self,
            on_success=self._on_url_modal_success,
            initial_url="",
        )

    def _on_url_modal_success(self, datos: dict):
        """Callback al descargar exitosamente desde UrlImportModal."""
        self.process_downloaded_data(datos)

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║  7. EXPORTACIÓN Y ARCHIVOS (CSV, PDF)                          ║
    # ╚══════════════════════════════════════════════════════════════════╝

    def load_from_csv(self, path: str = None):
        """Carga datos de grupos, investigadores y productos desde un archivo CSV o PDF."""
        self._close_more_options_panel()
        try:
            if not path:
                path = filedialog.askopenfilename(
                    filetypes=[
                        ("Archivos compatibles", "*.csv;*.pdf"),
                        ("Archivos CSV", "*.csv"),
                        ("Archivos PDF", "*.pdf"),
                        ("Todos los archivos", "*.*"),
                    ],
                    title="Seleccionar archivo CSV o PDF",
                )
            if not path:
                return

            ext = Path(path).suffix.lower()
            if ext == ".csv":
                datos = scienti.load_from_csv(path)
            elif ext == ".pdf":
                datos = scienti.load_from_pdf(path)
            else:
                messagebox.showerror("Error", "Formato de archivo no soportado.")
                return

            if "error" in datos:
                messagebox.showerror("Error", datos["error"])
                return

            if "grupos" in datos and datos["grupos"]:
                new_multilist = PersistenciaJSON.to_multilist(datos)
                if new_multilist and not new_multilist.is_empty():
                    self.multilista = new_multilist
                    self.grupo_crud = GrupoCRUD(self.multilista)
                    self.inv_crud = InvestigadorCRUD(self.multilista)
                    self.prod_crud = ProductoCRUD(self.multilista)

            self.save_data(silent=True)
            self.load_tabs_data()
            self.show_toast("Datos cargados correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar el archivo: {e}")

    def export_to_csv(self):
        """Exporta los datos actuales a un archivo CSV."""
        self._close_more_options_panel()
        try:
            path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
                title="Exportar datos a CSV",
            )
            if not path:
                return

            import csv
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "grupo_codigo", "grupo_nombre", "grupo_categoria", "grupo_lider", "grupo_fecha_creacion",
                    "investigador_cedula", "investigador_nombres", "investigador_apellidos", "investigador_email",
                    "producto_titulo", "producto_tipo", "producto_categoria", "producto_anio", "producto_validado"
                ])

                grupos = self.grupo_crud.list_all()
                for g in grupos:
                    invs = self.inv_crud.list_by_group(g.id)
                    if not invs:
                        writer.writerow([g.codigo_gruplac, g.nombre, g.categoria, g.lider, g.fecha_creacion, "", "", "", "", "", "", "", "", ""])
                        continue
                    for inv in invs:
                        prods = self.prod_crud.list_by_investigador(inv.cedula)
                        if not prods:
                            writer.writerow([g.codigo_gruplac, g.nombre, g.categoria, g.lider, g.fecha_creacion, inv.cedula, inv.nombres, inv.apellidos, inv.email, "", "", "", "", ""])
                            continue
                        for p in prods:
                            writer.writerow([
                                g.codigo_gruplac, g.nombre, g.categoria, g.lider, g.fecha_creacion,
                                inv.cedula, inv.nombres, inv.apellidos, inv.email,
                                p.titulo, p.tipo, p.categoria, p.anio, "1" if p.validado else "0"
                            ])

            self.show_toast("Datos exportados exitosamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar datos: {e}")

    def clear_data(self):
        """Limpia todos los datos cargados en memoria y persistencia."""
        self._close_more_options_panel()
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar todos los datos de investigación cargados?"):
            self.multilista = Multilist()
            self.grupo_crud = GrupoCRUD(self.multilista)
            self.inv_crud = InvestigadorCRUD(self.multilista)
            self.prod_crud = ProductoCRUD(self.multilista)
            self.save_data(silent=True)
            self.load_tabs_data()
            self.show_toast("Datos eliminados")

    def refresh_all(self):
        """Recarga los datos de todas las pestañas."""
        self.load_tabs_data()
        self.show_toast("Datos actualizados")

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║  8. MODALES DE AYUDA Y ACERCA DE                               ║
    # ╚══════════════════════════════════════════════════════════════════╝

    def show_quick_guide(self):
        """Muestra ventana modal con la guía rápida institucional."""
        self._close_more_options_panel()
        modal = ctk.CTkToplevel(self)
        modal.title("Guía rápida - PEA-i")
        modal.geometry("540x480")
        modal.resizable(False, False)
        modal.configure(fg_color=COLORS["bg"])
        modal.transient(self)
        modal.grab_set()

        self.update_idletasks()
        try:
            x = self.winfo_x() + max(0, (self.winfo_width() - 540) // 2)
            y = self.winfo_y() + max(0, (self.winfo_height() - 480) // 2)
            modal.geometry(f"540x480+{x}+{y}")
        except Exception:
            pass

        card_box = tarjeta(modal, corner_radius=RADIUS["card"])
        card_box.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["md"])

        title_lbl = ctk.CTkLabel(
            card_box,
            text="📖  Guía Rápida de Uso",
            font=font("heading"),
            text_color=COLORS["ink"],
            anchor="w",
        )
        title_lbl.pack(fill="x", padx=SPACING["md"], pady=(SPACING["md"], SPACING["sm"]))

        desc_lbl = ctk.CTkLabel(
            card_box,
            text=(
                "Funciones principales del sistema PEA-i:\n\n"
                "• Barra lateral: Navegación directa entre Grupos, Investigadores, "
                "Productos y el panel de Estadísticas.\n\n"
                "• Descargar del SCIENTI: Extrae automáticamente el grupo, integrantes "
                "y productos clasificados desde el portal GrupLAC de MinCiencias.\n\n"
                "• Búsqueda y Filtros: Búsqueda dinámica en tiempo real por código, "
                "nombre o líder.\n\n"
                "• Barra de Selección: Permite editar, activar/desactivar o eliminar "
                "registros individualmente o por lotes.\n\n"
                "• Más opciones (⚙): Cargar/guardar JSON, exportar a CSV o importar archivos."
            ),
            font=font("body"),
            text_color=COLORS["ink_soft"],
            anchor="w",
            justify="left",
            wraplength=480,
        )
        desc_lbl.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["sm"])

        btn_close = ctk.CTkButton(
            card_box,
            text="Cerrar",
            command=modal.destroy,
            height=38,
            corner_radius=RADIUS["control"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=font("body_bold"),
        )
        btn_close.pack(anchor="e", padx=SPACING["md"], pady=SPACING["md"])

    def about(self):
        """Muestra ventana modal con información del sistema institucional."""
        self._close_more_options_panel()
        modal = ctk.CTkToplevel(self)
        modal.title("Acerca de PEA-i")
        modal.geometry("480x300")
        modal.resizable(False, False)
        modal.configure(fg_color=COLORS["bg"])
        modal.transient(self)
        modal.grab_set()

        self.update_idletasks()
        try:
            x = self.winfo_x() + max(0, (self.winfo_width() - 480) // 2)
            y = self.winfo_y() + max(0, (self.winfo_height() - 300) // 2)
            modal.geometry(f"480x300+{x}+{y}")
        except Exception:
            pass

        card_box = tarjeta(modal, corner_radius=RADIUS["card"])
        card_box.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["md"])

        title_lbl = ctk.CTkLabel(
            card_box,
            text="PEA-i · Sistema de Investigación",
            font=font("heading"),
            text_color=COLORS["ink"],
            anchor="w",
        )
        title_lbl.pack(fill="x", padx=SPACING["md"], pady=(SPACING["md"], 4))

        sub_lbl = ctk.CTkLabel(
            card_box,
            text="Universidad Popular del Cesar · Versión 2.0",
            font=font("small_bold"),
            text_color=COLORS["primary"],
            anchor="w",
        )
        sub_lbl.pack(fill="x", padx=SPACING["md"], pady=(0, SPACING["sm"]))

        info_lbl = ctk.CTkLabel(
            card_box,
            text=(
                "Plataforma para la gestión y análisis estadístico de grupos de investigación, "
                "investigadores y productos académicos clasificados por MinCiencias.\n\n"
                "Desarrollado en Python con CustomTkinter, multilista ortogonal en memoria "
                "y persistencia JSON."
            ),
            font=font("body"),
            text_color=COLORS["ink_soft"],
            anchor="w",
            justify="left",
            wraplength=420,
        )
        info_lbl.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["sm"])

        btn_close = ctk.CTkButton(
            card_box,
            text="Entendido",
            command=modal.destroy,
            height=38,
            corner_radius=RADIUS["control"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=font("body_bold"),
        )
        btn_close.pack(anchor="e", padx=SPACING["md"], pady=SPACING["md"])

    def _bind_global_events(self):
        """Registra listeners de teclado globales (F5, Escape)."""
        self.bind_all("<F5>", lambda e: self.refresh_all())
        self.bind_all("<Escape>", lambda e: self._close_more_options_panel())


if __name__ == "__main__":
    app = App()
    app.mainloop()