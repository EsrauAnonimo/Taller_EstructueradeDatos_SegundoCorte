# -*- coding: utf-8 -*-
"""Ventana principal de la aplicación PEA-i (Sistema de Gestión de Investigación - Unicesar)."""

import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk

import customtkinter as ctk

_BASE_DIR = Path(__file__).resolve().parent
if str(_BASE_DIR) not in sys.path:
    sys.path.insert(0, str(_BASE_DIR))

# URL oficial de MinCiencias por defecto para descarga directa en un clic
DEFAULT_SCIENTI_URL = "https://scienti.minciencias.gov.co/gruplac/jsp/visualiza/visualizagr.jsp?nro=00000000002099"

from persistencia.persistencia_json import PersistenciaJSON
from modelos.multilista import Multilist
from modelos.pila import Stack
from modelos.cola import Queue
from crud.crud_grupos import GrupoCRUD
from crud.crud_investigadores import InvestigadorCRUD
from crud.crud_productos import ProductoCRUD
from entidades.grupo import Grupo
from entidades.investigador import Investigador
from entidades.producto import Producto
from gui.tabs.grupos_tab import GruposTab
from gui.tabs.investigadores_tab import InvestigadoresTab
from gui.tabs.productos_tab import ProductosTab
from gui.tabs.indicadores_tab import IndicadoresTab
from gui.tabs.estadisticas_tab import EstadisticasTab
from gui.dialogs.url_modal import UrlImportModal
from gui.dialogs.cola_importacion_modal import ColaImportacionModal
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

_TAB_NAMES = ["Grupos", "Investigadores", "Productos", "Indicadores", "Estadísticas"]


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
        "Indicadores": {
            "icon": ICONS["indicadores"],
            "title": "Indicador de Producción Científica",
            "subtitle": "Cálculo y desglose MinCiencias (Nc_Top, Nc_A, Nc_B, AP, DPC, Fr_A, Fr_B, Cohe, Coop)",
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

        self.title("PEA-i · Gestión de Investigación UPC")
        self.geometry("1280x760")
        self.minsize(1200, 700)

        # Configuración del ícono institucional de la ventana
        self._setup_window_icon()

        # Inicialización de modelos de datos y CRUDs
        self.persistencia = None
        self.multilista = Multilist()
        self.grupo_crud = GrupoCRUD(self.multilista)
        self.inv_crud = InvestigadorCRUD(self.multilista)
        self.prod_crud = ProductoCRUD(self.multilista)

        # ── Pila de deshacer (Stack propia, no list) ─────────────────────
        self.undo_stack: Stack = Stack()

        # ── Cola de importación (Queue propia, no deque) ────────────────
        self.import_queue: Queue = Queue()
        # Referencia a la ventana de cola si está abierta
        self._cola_window: Optional[ctk.CTkToplevel] = None

        self._last_saved: str = ""
        self._startup_source: str = "Arranque: listas vacías"
        self._status_toast_timer = None

        # Variables para el popup moderno de opciones (CTkToplevel sobre la tuerca)
        self._gear_popup: Optional[ctk.CTkToplevel] = None
        self._last_gear_popup_closed: float = 0.0
        self._popup_click_bind_id: Optional[str] = None
        self._menu_icons: Dict[str, ctk.CTkImage] = {}
        self._options_panel: Optional[ctk.CTkFrame] = None
        self._options_bind_id: Optional[str] = None
        self._gear_menu = None

        self.init_persistence()

        # Barra de menú superior eliminada (funciones reubicadas en la tuerca del sidebar)

        # ── Estructura General ──────────────────────────────────────────
        # 1. Barra lateral izquierda (ancho ~259 px, fondo #0F1B3D)
        self._build_sidebar()

        # 2. Contenedor principal derecho (header azul + tarjeta blanca)
        self._build_main_container()

        # 3. Montar vistas dentro de la tarjeta blanca
        self._build_views()

        # Atajos de teclado y listeners globales
        self._bind_global_events()

        # Inicializar estructuras vacías en memoria antes de la decisión del usuario (no cargar nada antes)
        self.start_empty_data()
        self.navigate_to(_TAB_NAMES[0])

        # Diálogo modal de inicio: el usuario decide si cargar datos o iniciar sin datos
        self.after(50, self._prompt_startup_choice)

    def _prompt_startup_choice(self):
        """Muestra un diálogo modal al iniciar con dos opciones:
        'Cargar datos del archivo' e 'Iniciar sin datos'.
        Si elige cargar y el archivo no existe o está corrupto, avisa y ofrece iniciar vacío.
        No carga nada antes de que el usuario elija."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Inicio del Sistema · PEA-i UPC")
        w, h = 480, 270
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        try:
            self.update_idletasks()
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            x = max(0, (sw - w) // 2)
            y = max(0, (sh - h) // 2)
            dialog.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            dialog.geometry(f"{w}x{h}")

        dialog.attributes("-topmost", True)
        dialog.lift()
        dialog.focus_force()

        card = ctk.CTkFrame(dialog, fg_color=COLORS.get("surface", "#FFFFFF"), corner_radius=12)
        card.pack(fill="both", expand=True, padx=14, pady=14)

        lbl_icon = ctk.CTkLabel(card, text="🏛️", font=(FONT_FAMILY, 28))
        lbl_icon.pack(pady=(8, 2))

        lbl_title = ctk.CTkLabel(
            card,
            text="Sistema de Investigación PEA-i",
            font=(FONT_FAMILY, 15, "bold"),
            text_color=COLORS.get("primary", "#1E3A8A"),
        )
        lbl_title.pack(pady=(0, 2))

        lbl_desc = ctk.CTkLabel(
            card,
            text="Seleccione cómo desea iniciar la aplicación:",
            font=(FONT_FAMILY, 11),
            text_color=COLORS.get("ink_soft", "#64748B"),
            justify="center",
        )
        lbl_desc.pack(pady=(0, 14), padx=16)

        btn_box = ctk.CTkFrame(card, fg_color="transparent")
        btn_box.pack(fill="x", padx=36, pady=4)

        def _action_load():
            try:
                if not hasattr(self, "persistencia") or not self.persistencia.exists():
                    dialog.grab_release()
                    dialog.destroy()
                    res = messagebox.askyesno(
                        "Archivo no encontrado",
                        "El archivo de datos guardados no existe.\n\n¿Desea iniciar con las listas vacías?"
                    )
                    if res:
                        self.start_empty_data()
                        self.show_toast("Iniciado con estructuras vacías")
                    else:
                        path = filedialog.askopenfilename(
                            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")],
                            title="Seleccionar archivo guardado (JSON)",
                        )
                        if path:
                            self.persistencia = PersistenciaJSON(filepath=path)
                            self.load_data()
                            self.show_toast("Datos cargados correctamente")
                        else:
                            self.start_empty_data()
                    return

                self.load_data()
                dialog.grab_release()
                dialog.destroy()
                self.show_toast("Datos cargados correctamente desde el archivo")
            except Exception as e:
                try:
                    dialog.grab_release()
                    dialog.destroy()
                except Exception:
                    pass
                res = messagebox.askyesno(
                    "Error al cargar archivo",
                    f"El archivo de datos está corrupto o es incompatible ({e}).\n\n¿Desea iniciar con las listas vacías?"
                )
                if res:
                    self.start_empty_data()
                    self.show_toast("Iniciado con estructuras vacías")
                else:
                    self.start_empty_data()

        def _action_empty():
            try:
                dialog.grab_release()
                dialog.destroy()
            except Exception:
                pass
            self.start_empty_data()
            self.show_toast("Iniciado con estructuras vacías en memoria")

        dialog.protocol("WM_DELETE_WINDOW", _action_empty)

        btn_load = ctk.CTkButton(
            btn_box,
            text="📂  Cargar datos del archivo",
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            height=38,
            corner_radius=RADIUS["control"],
            command=_action_load,
        )
        btn_load.pack(fill="x", pady=4)

        btn_empty = ctk.CTkButton(
            btn_box,
            text="✨  Iniciar sin datos",
            font=(FONT_FAMILY, 12),
            fg_color="#475569",
            hover_color="#334155",
            height=36,
            corner_radius=RADIUS["control"],
            command=_action_empty,
        )
        btn_empty.pack(fill="x", pady=4)

    def create_menu(self):
        """Compatibilidad: la barra de menú nativa fue reubicada en la tuerca del pie del sidebar."""
        pass

    def _setup_window_icon(self):
        """Establece el ícono institucional de Unicesar en la ventana."""
        logo_path = Path(__file__).resolve().parent / "gui" / "assets" / "logo_unicesar.png"
        if logo_path.exists():
            try:
                pil_icon = Image.open(logo_path)
                self._app_icon = ImageTk.PhotoImage(pil_icon)
                self.wm_iconphoto(True, self._app_icon)
            except Exception as e:
                print("Aviso al configurar ícono de ventana:", e)

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

        # Logo institucional y texto en la esquina superior izquierda
        self.brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.brand_frame.pack(fill="x", padx=16, pady=(20, 16))

        # Cargar logo institucional de Unicesar
        self.logo_image = None
        logo_path = Path(__file__).resolve().parent / "gui" / "assets" / "logo_unicesar.png"
        if logo_path.exists():
            try:
                pil_logo = Image.open(logo_path)
                self.logo_image = ctk.CTkImage(
                    light_image=pil_logo,
                    dark_image=pil_logo,
                    size=(44, 44),
                )
            except Exception as e:
                print("Aviso al cargar logo:", e)

        if self.logo_image:
            self.logo_img_lbl = ctk.CTkLabel(
                self.brand_frame,
                text="",
                image=self.logo_image,
            )
            self.logo_img_lbl.pack(side="left", padx=(0, 10))

        self.brand_text_frame = ctk.CTkFrame(self.brand_frame, fg_color="transparent")
        self.brand_text_frame.pack(side="left", fill="both", expand=True)

        self.logo_title = ctk.CTkLabel(
            self.brand_text_frame,
            text="UNICESAR",
            font=(FONT_FAMILY, 18, "bold"),
            text_color="#FFFFFF",
            anchor="w",
        )
        self.logo_title.pack(fill="x")

        self.logo_sub = ctk.CTkLabel(
            self.brand_text_frame,
            text="Universidad Popular del Cesar",
            font=(FONT_FAMILY, 10),
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
        """Construye el pie de la barra lateral con tarjeta sobria, versión y botón de engranaje."""
        # Cargar ícono de tuerca en alta resolución (PNG institucional)
        self.gear_image = None
        gear_path = Path(__file__).resolve().parent / "gui" / "assets" / "gear.png"
        if gear_path.exists():
            try:
                pil_gear = Image.open(gear_path)
                self.gear_image = ctk.CTkImage(
                    light_image=pil_gear,
                    dark_image=pil_gear,
                    size=(18, 18),
                )
            except Exception as e:
                print("Aviso al cargar ícono de engranaje:", e)

        # Contenedor inferior en el sidebar
        self.footer_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.footer_container.pack(side="bottom", fill="x", padx=14, pady=14)

        # Tarjeta sobria con fondo ligeramente más claro que el sidebar (#16223F) y bordes redondeados
        self.footer_card = ctk.CTkFrame(
            self.footer_container,
            fg_color="#16223F",
            corner_radius=10,
            border_width=1,
            border_color="#1E293B",
        )
        self.footer_card.pack(fill="x", ipady=4)

        # Fila interna
        self.footer_row = ctk.CTkFrame(self.footer_card, fg_color="transparent")
        self.footer_row.pack(fill="x", padx=12, pady=8)

        # Textos a la izquierda: Título PEA-i en negrita y subtítulo con persistencia
        self.footer_text_frame = ctk.CTkFrame(self.footer_row, fg_color="transparent")
        self.footer_text_frame.pack(side="left", fill="both", expand=True)

        self.sidebar_app_title = ctk.CTkLabel(
            self.footer_text_frame,
            text="PEA-i",
            font=(FONT_FAMILY, 13, "bold"),
            text_color="#FFFFFF",
            anchor="w",
        )
        self.sidebar_app_title.pack(fill="x")

        self.sidebar_version_lbl = ctk.CTkLabel(
            self.footer_text_frame,
            text="v1.0 · Persistencia: JSON",
            font=(FONT_FAMILY, 9),
            text_color="#94A3B8",
            anchor="w",
        )
        self.sidebar_version_lbl.pack(fill="x", pady=(1, 0))

        # Botón con ícono de tuerca (engranaje) a la derecha, sin fondo, con hover
        self.btn_gear = ctk.CTkButton(
            self.footer_row,
            text="",
            image=self.gear_image,
            width=32,
            height=32,
            corner_radius=6,
            fg_color="transparent",
            hover_color="#1E293B",
            command=self._open_gear_menu,
        )
        self.btn_gear.pack(side="right")
        self.btn_more_options = self.btn_gear

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

        self.status_count_badge = ctk.CTkFrame(
            self.header_right,
            fg_color=COLORS["header_badge_bg"],
            corner_radius=RADIUS["pill"],
        )
        self.status_count_badge.pack(side="top", anchor="e", pady=(4, 0))

        self.status_count_lbl = ctk.CTkLabel(
            self.status_count_badge,
            text="Persistencia: JSON | Sin datos cargados",
            font=font("small"),
            text_color=COLORS["header_sub"],
            anchor="center",
        )
        self.status_count_lbl.pack(padx=12, pady=3)

        # Barra de estado inferior institucional
        self.status_bar_frame = ctk.CTkFrame(
            self.right_container,
            height=28,
            fg_color=COLORS["surface"],
            corner_radius=0,
            border_width=1,
            border_color=COLORS["border"],
        )
        self.status_bar_frame.pack(side="bottom", fill="x")
        self.status_bar_frame.pack_propagate(False)

        self.status_bar_lbl = ctk.CTkLabel(
            self.status_bar_frame,
            text="Persistencia: JSON | Sin datos cargados",
            font=font("small"),
            text_color=COLORS["muted"],
            anchor="w",
        )
        self.status_bar_lbl.pack(side="left", padx=16, pady=2)

        # Área de contenido con margen de 24 px
        self.content_area = ctk.CTkFrame(self.right_container, fg_color="transparent")
        self.content_area.pack(fill="both", expand=True, padx=24, pady=(16, 12))

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
        self.indicadores_tab = IndicadoresTab(self._tab_frames["Indicadores"], app=self)
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

        # 1. Actualizar apariencia de botones en la barra lateral con indicador visual activo
        for name, btn in self.nav_buttons.items():
            if name == section_name:
                btn.configure(
                    fg_color=COLORS["sidebar_active"],
                    hover_color=COLORS["sidebar_active"],
                    text_color=COLORS["sidebar_text_active"],
                    font=font("body_bold"),
                    border_width=1,
                    border_color=COLORS["sidebar_indicator"],
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    hover_color=COLORS["sidebar_hover"],
                    text_color=COLORS["sidebar_text"],
                    font=font("body"),
                    border_width=0,
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

        # Si se navega a Indicadores o Estadísticas, refrescar vistas
        if section_name == "Indicadores" and hasattr(self, "indicadores_tab"):
            try:
                self.indicadores_tab.refresh()
            except Exception:
                pass

        if section_name == "Estadísticas" and hasattr(self, "estadisticas_tab"):
            try:
                self.estadisticas_tab.refresh()
            except Exception:
                pass

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║  4. MENÚ CONTEXTUAL DE CONFIGURACIÓN (Tuerca / Gear Popup)      ║
    # ╚══════════════════════════════════════════════════════════════════╝

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║  4. POPUP MODERNO DE OPCIONES (CTkToplevel sobre Tuerca)         ║
    # ╚══════════════════════════════════════════════════════════════════╝

    def _load_menu_icons(self) -> Dict[str, ctk.CTkImage]:
        """Carga en caché los íconos PNG institucionales para el popup moderno."""
        if hasattr(self, "_menu_icons") and self._menu_icons:
            return self._menu_icons

        self._menu_icons = {}
        icons_dir = Path(__file__).resolve().parent / "gui" / "assets" / "icons"
        icon_names = ["folder_open", "save", "download", "csv", "queue", "info", "logout"]
        for name in icon_names:
            p = icons_dir / f"{name}.png"
            if p.exists():
                try:
                    pil_img = Image.open(p)
                    self._menu_icons[name] = ctk.CTkImage(
                        light_image=pil_img,
                        dark_image=pil_img,
                        size=(16, 16),
                    )
                except Exception as e:
                    print(f"Aviso al cargar ícono {name}:", e)
        return self._menu_icons

    def _open_gear_menu(self):
        """Abre o cierra (toggle) el popup moderno con CTkToplevel posicionado sobre la tuerca."""
        now = time.time()
        # Evitar reapertura accidental si se acaba de cerrar mediante clic en la tuerca
        if hasattr(self, "_last_gear_popup_closed") and (now - self._last_gear_popup_closed < 0.22):
            return

        # Si ya está abierto, cerrarlo (comportamiento toggle)
        if hasattr(self, "_gear_popup") and self._gear_popup is not None:
            try:
                if self._gear_popup.winfo_exists():
                    self._close_gear_popup()
                    return
            except Exception:
                pass

        self._load_menu_icons()

        # Ventana emergente moderna sin bordes nativos
        popup = ctk.CTkToplevel(self)
        self._gear_popup = popup

        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
        popup.transient(self)

        # Transparencia de esquinas en Windows si está soportada
        try:
            popup.attributes("-transparentcolor", "#000001")
            popup.configure(fg_color="#000001")
        except Exception:
            popup.configure(fg_color="#16223F")

        # Iniciar invisible para animación de fade-in
        try:
            popup.attributes("-alpha", 0.0)
        except Exception:
            pass

        # Contenedor CTkFrame con corner_radius=12, borde sutil y tono más claro que el sidebar
        container = ctk.CTkFrame(
            popup,
            width=260,
            corner_radius=12,
            fg_color="#16223F",
            border_width=1,
            border_color="#2A3B5C",
        )
        container.pack(fill="both", expand=True)

        content = ctk.CTkFrame(container, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=8, pady=8)

        def add_header(title: str, is_first: bool = False):
            lbl = ctk.CTkLabel(
                content,
                text=title,
                font=(FONT_FAMILY, 10, "bold"),
                text_color="#64748B",
                anchor="w",
            )
            lbl.pack(fill="x", padx=6, pady=(3 if is_first else 9, 2))

        def add_option(label: str, icon_key: str, command: Optional[Callable], shortcut: Optional[str] = None, is_danger: bool = False):
            icon_img = self._menu_icons.get(icon_key)
            text_color = "#F87171" if is_danger else "#F8FAFC"
            hover_color = "#3B1824" if is_danger else "#1E2D5A"

            btn = ctk.CTkButton(
                content,
                text=f"  {label}",
                image=icon_img,
                compound="left",
                anchor="w",
                height=34,
                corner_radius=8,
                fg_color="transparent",
                hover_color=hover_color,
                text_color=text_color,
                font=(FONT_FAMILY, 11),
                command=lambda c=command: self._exec_gear_option(c),
            )
            btn.pack(fill="x", pady=1)

            if shortcut:
                lbl_shortcut = ctk.CTkLabel(
                    btn,
                    text=shortcut,
                    font=(FONT_FAMILY, 10),
                    text_color="#94A3B8",
                    fg_color="transparent",
                )
                lbl_shortcut.place(relx=1.0, rely=0.5, anchor="e", x=-10)
                lbl_shortcut.bind("<Button-1>", lambda e, c=command: self._exec_gear_option(c))
                lbl_shortcut.bind("<Enter>", lambda e, b=btn: b._on_enter())
                lbl_shortcut.bind("<Leave>", lambda e, b=btn: b._on_leave())

        # ── Sección ARCHIVO ─────────────────────────────────────────────
        add_header("ARCHIVO", is_first=True)
        add_option("Cargar datos", "folder_open", self.load_from_json, shortcut="Ctrl+O")
        add_option("Guardar datos", "save", self.save_data, shortcut="Ctrl+S")

        # ── Sección DATOS ───────────────────────────────────────────────
        add_header("DATOS")
        add_option("Descargar del SCIENTI", "download", self.download_scienti_default)
        add_option("Cargar desde CSV", "csv", self.import_from_csv)
        add_option("Cola de importación", "queue", self.open_cola_importacion)

        # ── Sección AYUDA ───────────────────────────────────────────────
        add_header("AYUDA")
        add_option("Acerca de", "info", self.about)

        # Separador fino antes de salir
        sep = ctk.CTkFrame(content, height=1, fg_color="#1E293B")
        sep.pack(fill="x", padx=4, pady=(6, 4))

        # ── SALIR ──────────────────────────────────────────────────────
        add_option("Salir", "logout", self.exit_app, is_danger=True)

        popup.update_idletasks()

        # Dimensiones y posicionamiento justo encima y alineado a la derecha de la tuerca
        popup_w = 260
        popup_h = container.winfo_reqheight()

        try:
            btn_x = self.btn_gear.winfo_rootx()
            btn_y = self.btn_gear.winfo_rooty()
            btn_w = self.btn_gear.winfo_width()

            # Alinear el borde derecho del popup con el borde derecho de la tuerca
            pos_x = max(self.winfo_rootx() + 8, (btn_x + btn_w) - popup_w)
            # Posicionar justo encima de la tuerca con 6 px de separación
            pos_y = max(10, btn_y - popup_h - 6)
        except Exception:
            pos_x = self.winfo_rootx() + 16
            pos_y = self.winfo_rooty() + 200

        popup.geometry(f"{popup_w}x{popup_h}+{pos_x}+{pos_y}")

        # Pequeña animación de aparición suave (alpha 0 -> 1 en ~120 ms)
        def _fade_in(step=0):
            if not self._gear_popup or not self._gear_popup.winfo_exists():
                return
            alpha = min(1.0, (step + 1) * 0.18)
            try:
                self._gear_popup.attributes("-alpha", alpha)
            except Exception:
                return
            if alpha < 1.0:
                self.after(20, lambda: _fade_in(step + 1))

        self.after(10, _fade_in)

        # Cierre con Escape
        popup.bind("<Escape>", lambda e: self._close_gear_popup())

        # Cierre al perder el foco de la ventana emergente
        def _on_focus_out(e):
            try:
                focused = popup.focus_get()
                if focused and str(focused).startswith(str(popup)):
                    return
            except Exception:
                pass
            self.after(60, self._close_gear_popup)

        popup.bind("<FocusOut>", _on_focus_out)

        # Cierre al hacer clic fuera dentro de la ventana principal
        if hasattr(self, "_popup_click_bind_id") and self._popup_click_bind_id:
            try:
                self.unbind("<Button-1>", self._popup_click_bind_id)
            except Exception:
                pass
        self._popup_click_bind_id = self.bind("<Button-1>", self._on_window_click_outside_popup, add="+")

        # Establecer foco para capturar eventos de teclado
        popup.after(30, popup.focus_set)

    def _exec_gear_option(self, command: Optional[Callable]):
        """Cierra el popup de la tuerca y ejecuta el callback correspondiente."""
        self._close_gear_popup()
        if command:
            self.after(20, command)

    def _close_gear_popup(self):
        """Cierra la ventana emergente de la tuerca y limpia bindings auxiliares."""
        if hasattr(self, "_popup_click_bind_id") and self._popup_click_bind_id:
            try:
                self.unbind("<Button-1>", self._popup_click_bind_id)
            except Exception:
                pass
            self._popup_click_bind_id = None

        if hasattr(self, "_gear_popup") and self._gear_popup is not None:
            self._last_gear_popup_closed = time.time()
            try:
                self._gear_popup.destroy()
            except Exception:
                pass
            self._gear_popup = None

        # Devolver el foco a la ventana principal para mantenerla activa
        try:
            self.focus_set()
        except Exception:
            pass

    def _close_more_options_panel(self):
        """Alias de compatibilidad para cerrar el popup emergente."""
        self._close_gear_popup()

    def _on_window_click_outside_popup(self, event):
        """Detecta clics fuera del popup dentro de la ventana principal y lo cierra."""
        if not hasattr(self, "_gear_popup") or self._gear_popup is None:
            return

        # Si el clic fue en la tuerca, el toggle se encarga
        try:
            bx = self.btn_gear.winfo_rootx()
            by = self.btn_gear.winfo_rooty()
            bw = self.btn_gear.winfo_width()
            bh = self.btn_gear.winfo_height()
            if bx <= event.x_root <= bx + bw and by <= event.y_root <= by + bh:
                return
        except Exception:
            pass

        # Si el clic fue dentro del popup, mantenerlo
        try:
            px = self._gear_popup.winfo_rootx()
            py = self._gear_popup.winfo_rooty()
            pw = self._gear_popup.winfo_width()
            ph = self._gear_popup.winfo_height()
            if px <= event.x_root <= px + pw and py <= event.y_root <= py + ph:
                return
        except Exception:
            pass

        self._close_gear_popup()

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║  5. PERSISTENCIA Y OPERACIONES CRUD                            ║
    # ╚══════════════════════════════════════════════════════════════════╝

    def init_persistence(self):
        """Inicializa la persistencia directa con archivo JSON."""
        datos_path = Path(__file__).resolve().parent / "datos" / "datos.json"
        self.persistencia = PersistenciaJSON(filepath=str(datos_path))

    def has_data(self) -> bool:
        """Indica si existen grupos cargados en la multilista."""
        return len(self.grupo_crud.list_all()) > 0

    def load_from_json(self):
        """Carga datos desde el archivo de persistencia guardado (JSON) o un archivo seleccionado."""
        self._close_more_options_panel()
        try:
            if not self.persistencia.exists():
                path = filedialog.askopenfilename(
                    filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")],
                    title="Seleccionar archivo guardado (JSON)",
                )
                if not path:
                    return
                self.persistencia = PersistenciaJSON(filepath=path)

            self.load_data()
            self.show_toast("Datos cargados desde archivo guardado (JSON)")
        except Exception as e:
            self._show_import_error(f"Error al cargar desde JSON: {e}", origen="JSON")

    def start_empty_data(self):
        """Inicia la sesión con estructuras vacías sin borrar la persistencia activa."""
        self.multilista = Multilist()
        self.grupo_crud = GrupoCRUD(self.multilista)
        self.inv_crud = InvestigadorCRUD(self.multilista)
        self.prod_crud = ProductoCRUD(self.multilista)
        self.undo_stack = Stack()
        self.import_queue = Queue()
        self.load_tabs_data()

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
                                plan=g.get("plan", ""),
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
                            cat_p = p.get("categoria_producto") or p.get("categoria") or "Nuevo conocimiento"
                            val_p = p.get("validacion") or "No validado"
                            prod_obj = Producto(
                                id=p.get("id"),
                                titulo=p.get("title") or p.get("titulo", ""),
                                tipo=p.get("type") or p.get("tipo", ""),
                                categoria=cat_p,
                                validado=p.get("active", p.get("validado", True)),
                                anio=anio_val,
                                investigador_id=inv_id_val,
                                grupo_id=p.get("grupo_id") or p.get("group"),
                                gran_categoria=p.get("gran_categoria", "Sin clasificar"),
                                codigo_minciencias=p.get("codigo_minciencias", ""),
                                categoria_producto=cat_p,
                                validacion=val_p,
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
            self.indicadores_tab.refresh()
        except Exception:
            pass
        try:
            self.estadisticas_tab.refresh()
        except Exception:
            pass
        self._refresh_status_bar()

    def _refresh_status_bar(self):
        """Actualiza indicadores numéricos, deshacer y tamaño de cola en el encabezado y barra de estado."""
        try:
            ng = len(self.grupo_crud.list_all())
            ni = len(self.inv_crud.list_all())
            np_ = len(self.prod_crud.list_all())
            nu = len(self.undo_stack) if hasattr(self, 'undo_stack') else 0
            nq = len(self.import_queue) if hasattr(self, 'import_queue') else 0
            undo_text = f"  ·  Deshacer: {nu}" if nu > 0 else ""
            cola_text = f"  ·  Cola: {nq}" if nq > 0 else ""

            if ng == 0 and ni == 0 and np_ == 0:
                base_text = "Persistencia: JSON | Sin datos cargados"
            else:
                base_text = f"Persistencia: JSON | {ng} grupo{'s' if ng != 1 else ''} · {ni} inv. · {np_} prod."

            full_status = f"{base_text}{undo_text}{cola_text}"

            if hasattr(self, "status_bar_lbl") and self.status_bar_lbl:
                self.status_bar_lbl.configure(text=full_status)

            if hasattr(self, "status_count_lbl") and self.status_count_lbl:
                self.status_count_lbl.configure(text=full_status)

            # Actualizar estado de persistencia real en el pie del sidebar
            pers_name = "JSON"
            if hasattr(self, "persistencia") and self.persistencia:
                if hasattr(self.persistencia, "tipo"):
                    pers_name = str(self.persistencia.tipo)
                elif hasattr(self.persistencia, "filepath"):
                    ext = Path(self.persistencia.filepath).suffix.replace(".", "").upper()
                    if ext:
                        pers_name = ext
            if hasattr(self, "sidebar_version_lbl") and self.sidebar_version_lbl:
                self.sidebar_version_lbl.configure(text=f"v1.0 · Persistencia: {pers_name}")
        except Exception:
            pass

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║  PILA DE DESHACER ELIMINACIÓN (Stack propia)                   ║
    # ╚══════════════════════════════════════════════════════════════════╝

    def push_undo(self, tipo: str, objeto, posicion: dict):
        """Apila una operación de eliminación para poder deshacerla.

        Args:
            tipo: 'grupo', 'investigador' o 'producto'
            objeto: instancia completa del objeto eliminado
            posicion: dict con metadatos de posición y relaciones necesarias
                      para reinsertar en la multilista exactamente.
        """
        self.undo_stack.push({'tipo': tipo, 'objeto': objeto, 'posicion': posicion})
        self._refresh_status_bar()
        self._sync_undo_buttons()

    def undo_delete(self):
        """Extrae el tope de la pila y reinserta el objeto eliminado en su posición."""
        if self.undo_stack.is_empty():
            return

        entrada = self.undo_stack.pop()  # pop() de la Stack propia
        tipo = entrada['tipo']
        obj = entrada['objeto']
        pos = entrada['posicion']

        try:
            if tipo == 'grupo':
                self._undo_grupo(obj, pos)
            elif tipo == 'investigador':
                self._undo_investigador(obj, pos)
            elif tipo == 'producto':
                self._undo_producto(obj, pos)
        except Exception as e:
            self.show_toast(f"Error al deshacer: {e}", color="#FCA5A5")
            return

        self.save_data(silent=True)
        self.load_tabs_data()
        self._refresh_status_bar()
        self._sync_undo_buttons()
        self.show_toast(f"Eliminación de {tipo} deshecha correctamente")

    def _undo_grupo(self, grupo, pos: dict):
        """Reinserta un grupo en la multilista en su posición original."""
        # Restaurar todos los investigadores y productos del grupo
        # (almacenados en pos['investigadores'])
        grupo.activo = True
        self.grupo_crud.create(grupo)

        invs = pos.get('investigadores', [])
        for inv_entry in invs:
            inv = inv_entry['investigador']
            inv.activo = True
            inv.grupo_id = getattr(grupo, 'id', inv.grupo_id)
            try:
                self.inv_crud.create(inv)
            except Exception:
                pass
            for prod in inv_entry.get('productos', []):
                prod.investigador_cedula = getattr(inv, 'cedula', None)
                prod.investigador_id = getattr(inv, 'cedula', None)
                prod.grupo_id = getattr(grupo, 'id', prod.grupo_id)
                try:
                    self.prod_crud.create(prod)
                except Exception:
                    pass

    def _undo_investigador(self, inv, pos: dict):
        """Reinserta un investigador y sus productos en la multilista."""
        inv.activo = True
        try:
            self.inv_crud.create(inv)
        except Exception:
            pass
        for prod in pos.get('productos', []):
            prod.investigador_cedula = getattr(inv, 'cedula', None)
            prod.investigador_id = getattr(inv, 'cedula', None)
            try:
                self.prod_crud.create(prod)
            except Exception:
                pass

    def _undo_producto(self, prod, pos: dict):
        """Reinserta un producto en la multilista."""
        try:
            self.prod_crud.create(prod)
        except Exception:
            pass

    def _sync_undo_buttons(self):
        """Habilita o deshabilita todos los botones 'Deshacer' según el estado de la pila."""
        tiene_acciones = not self.undo_stack.is_empty()
        tabs = [
            getattr(self, 'grupos_tab', None),
            getattr(self, 'investigadores_tab', None),
            getattr(self, 'productos_tab', None),
        ]
        for tab in tabs:
            if tab is not None and hasattr(tab, 'btn_undo'):
                try:
                    state = 'normal' if tiene_acciones else 'disabled'
                    tab.btn_undo.configure(state=state)
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
        self.download_scienti_default()

    def download_scienti_default(self):
        """Descarga del SCIENTI (URL por defecto de GrupLAC de la UPC)."""
        self._close_more_options_panel()
        self.download_from_url(DEFAULT_SCIENTI_URL)

    def download_from_url(self, url: str):
        """Descarga e integra la información de un grupo desde la URL en hilo secundario."""
        if not url or not (url.startswith("http://") or url.startswith("https://")):
            self._show_import_error("La URL ingresada no es válida o está vacía.", origen="SCIENTI")
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
            error_msg = datos.get("error", "Error al descargar desde SCIENTI.") if isinstance(datos, dict) else "Error al descargar desde SCIENTI."
            self.show_toast("Error al descargar", color="#FCA5A5")
            self._show_import_error(error_msg, origen="SCIENTI")
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
                    # El codigo_gruplac es el código SCIENTI; el id lo genera el CRUD
                    codigo_g = grupo_raw.get("codigo_gruplac") or grupo_raw.get("id", "")
                    existing = self.grupo_crud.get_by_code(codigo_g) if codigo_g else None
                    if not existing:
                        grupo_obj = Grupo(
                            id=None,
                            codigo_gruplac=codigo_g,
                            nombre=grupo_raw.get("nombre") or grupo_raw.get("name") or "Grupo SCIENTI",
                            categoria=grupo_raw.get("categoria", ""),
                            lider=grupo_raw.get("lider", ""),
                            activo=True,
                            fecha_creacion=grupo_raw.get("fecha_creacion", ""),
                            plan=grupo_raw.get("plan", ""),
                        )
                        self.grupo_crud.create(grupo_obj)
                    else:
                        grupo_obj = existing
                    gid = getattr(grupo_obj, "id", None)
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

    def download_scienti_custom(self):
        """Descarga del SCIENTI (otra URL): pide la URL en un cuadro de diálogo."""
        self._close_more_options_panel()
        dialog = ctk.CTkToplevel(self)
        dialog.title("Descargar del SCIENTI (otra URL)")
        dialog.geometry("540x220")
        dialog.resizable(False, False)
        dialog.configure(fg_color=COLORS["bg"])
        dialog.transient(self)
        dialog.grab_set()

        try:
            dialog.update_idletasks()
            x = self.winfo_x() + max(0, (self.winfo_width() - 540) // 2)
            y = self.winfo_y() + max(0, (self.winfo_height() - 220) // 2)
            dialog.geometry(f"540x220+{x}+{y}")
        except Exception:
            pass

        card = tarjeta(dialog, corner_radius=RADIUS["card"])
        card.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["md"])

        ctk.CTkLabel(
            card,
            text="Descargar grupo desde SCIENTI / GrupLAC",
            font=font("heading"),
            text_color=COLORS["ink"],
            anchor="w",
        ).pack(fill="x", padx=SPACING["lg"], pady=(SPACING["md"], SPACING["xs"]))

        ctk.CTkLabel(
            card,
            text="Ingresa la URL del grupo de investigación en MinCiencias:",
            font=font("body"),
            text_color=COLORS["muted"],
            anchor="w",
        ).pack(fill="x", padx=SPACING["lg"], pady=(0, SPACING["sm"]))

        from gui.styles import entry as _entry
        url_entry = _entry(card, placeholder_text="https://scienti.minciencias.gov.co/gruplac/jsp/visualiza/...", width=480)
        url_entry.pack(fill="x", padx=SPACING["lg"], pady=(0, SPACING["xs"]))

        err_lbl = ctk.CTkLabel(card, text="", font=font("small"), text_color=COLORS["danger"], anchor="w")
        err_lbl.pack(fill="x", padx=SPACING["lg"])

        def _do_download():
            url = url_entry.get().strip()
            if not url or not (url.startswith("http://") or url.startswith("https://")):
                err_lbl.configure(text="Por favor ingresa una URL válida (http:// o https://)")
                return
            dialog.destroy()
            self.download_from_url(url)

        btns = ctk.CTkFrame(card, fg_color="transparent")
        btns.pack(fill="x", padx=SPACING["lg"], pady=(SPACING["xs"], SPACING["md"]))

        from gui.styles import boton_primario, boton_secundario
        boton_primario(btns, text="Descargar", command=_do_download, height=36).pack(side="right", padx=(SPACING["sm"], 0))
        boton_secundario(btns, text="Cancelar", command=dialog.destroy, height=36).pack(side="right")

        url_entry.bind("<Return>", lambda e: _do_download())
        dialog.after(100, url_entry.focus_set)

    def download_from_custom_url(self):
        """Alias compatible para download_scienti_custom."""
        self.download_scienti_custom()

    def _on_url_modal_success(self, datos: dict):
        """Callback al descargar exitosamente desde UrlImportModal."""
        self.process_downloaded_data(datos)

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║  COLA DE IMPORTACIÓN (Queue propia)                            ║
    # ╚══════════════════════════════════════════════════════════════════╝

    def open_cola_importacion(self):
        """Abre (o trae al frente) la ventana de Cola de Importación."""
        self._close_more_options_panel()
        # Reutilizar la ventana si ya está abierta
        if self._cola_window is not None:
            try:
                self._cola_window.lift()
                self._cola_window.focus_force()
                return
            except Exception:
                self._cola_window = None

        self._cola_window = ColaImportacionModal(parent=self, app_ref=self)
        # Limpiar la referencia cuando se cierre
        self._cola_window.bind(
            "<Destroy>",
            lambda e: setattr(self, '_cola_window', None),
        )

    def queue_add_url_and_show(self):
        """Abre un mini-diálogo para encolar una URL SCIENTI y luego muestra la cola."""
        self._close_more_options_panel()
        # Diálogo simple de entrada
        dialog = ctk.CTkToplevel(self)
        dialog.title("Agregar URL a la cola")
        dialog.geometry("520x180")
        dialog.resizable(False, False)
        dialog.configure(fg_color=COLORS["bg"])
        dialog.transient(self)
        dialog.grab_set()

        try:
            x = self.winfo_x() + max(0, (self.winfo_width() - 520) // 2)
            y = self.winfo_y() + max(0, (self.winfo_height() - 180) // 2)
            dialog.geometry(f"520x180+{x}+{y}")
        except Exception:
            pass

        from gui.styles import tarjeta, RADIUS
        card = tarjeta(dialog, corner_radius=RADIUS["card"])
        card.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["md"])

        from gui.styles import entry as _entry
        ctk.CTkLabel(
            card,
            text="URL de GrupLAC para encolar:",
            font=font("body_bold"),
            text_color=COLORS["ink"],
            anchor="w",
        ).pack(fill="x", padx=SPACING["lg"], pady=(SPACING["md"], SPACING["xs"]))

        url_var = ctk.StringVar()
        url_field = _entry(card, placeholder_text="https://scienti.minciencias.gov.co/gruplac/...", width=460)
        url_field.pack(fill="x", padx=SPACING["lg"], pady=(0, SPACING["sm"]))

        err_lbl = ctk.CTkLabel(card, text="", font=font("small"), text_color=COLORS["danger"], anchor="w")
        err_lbl.pack(fill="x", padx=SPACING["lg"])

        def _do_enqueue():
            url = url_field.get().strip()
            if not url or not (url.startswith("http://") or url.startswith("https://")):
                err_lbl.configure(text="Ingresa una URL válida (http:// o https://)")
                return
            self.import_queue.enqueue({"tipo": "url", "valor": url, "etiqueta": url[:60]})
            self._refresh_status_bar()
            dialog.destroy()
            self.open_cola_importacion()

        btns = ctk.CTkFrame(card, fg_color="transparent")
        btns.pack(fill="x", padx=SPACING["lg"], pady=(SPACING["xs"], SPACING["md"]))

        from gui.styles import boton_primario, boton_secundario
        boton_primario(btns, text="Agregar a cola", command=_do_enqueue, height=36).pack(side="right", padx=(SPACING["sm"], 0))
        boton_secundario(btns, text="Cancelar", command=dialog.destroy, height=36).pack(side="right")

        url_field.bind("<Return>", lambda e: _do_enqueue())
        dialog.after(100, url_field.focus_set)



    # ╔══════════════════════════════════════════════════════════════════╗
    # ║  7. EXPORTACIÓN Y ARCHIVOS (CSV, PDF)                          ║
    # ╚══════════════════════════════════════════════════════════════════╝

    def import_from_csv(self, path: Optional[str] = None):
        """Importa datos desde un archivo CSV y actualiza las pestañas."""
        self._close_more_options_panel()
        try:
            if not path:
                path = filedialog.askopenfilename(
                    filetypes=[
                        ("Archivos CSV", "*.csv"),
                        ("Todos los archivos", "*.*"),
                    ],
                    title="Seleccionar archivo CSV para importar",
                )
            if not path:
                return

            datos = scienti.load_from_csv(path)
            if not datos or (isinstance(datos, dict) and "error" in datos):
                err = datos.get("error", "Error al leer el archivo CSV.") if isinstance(datos, dict) else "Error al leer CSV."
                self._show_import_error(err, origen="CSV")
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
                    self.show_toast("Datos importados desde CSV exitosamente")
                    return

            self._show_import_error("El archivo CSV no contiene registros de grupos válidos.", origen="CSV")
        except Exception as e:
            self._show_import_error(f"Error inesperado al importar CSV: {e}", origen="CSV")

    def import_from_pdf(self, path: Optional[str] = None):
        """Importa datos desde un archivo PDF y actualiza las pestañas."""
        self._close_more_options_panel()
        try:
            if not path:
                path = filedialog.askopenfilename(
                    filetypes=[
                        ("Archivos PDF", "*.pdf"),
                        ("Todos los archivos", "*.*"),
                    ],
                    title="Seleccionar archivo PDF para importar",
                )
            if not path:
                return

            datos = scienti.load_from_pdf(path)
            if not datos or (isinstance(datos, dict) and "error" in datos):
                err = datos.get("error", "No se pudo extraer información del archivo PDF.") if isinstance(datos, dict) else "Error al leer PDF."
                self._show_import_error(err, origen="PDF")
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
                    self.show_toast("Datos importados desde PDF exitosamente")
                    return

            self._show_import_error(
                "El archivo PDF no contiene tablas de grupos estructuradas compatibles.",
                origen="PDF"
            )
        except Exception as e:
            self._show_import_error(f"Error inesperado al importar PDF: {e}", origen="PDF")

    def load_from_csv(self, path: str = None):
        """Alias compatible para importar desde CSV o PDF."""
        if path and str(path).lower().endswith(".pdf"):
            self.import_from_pdf(path)
        else:
            self.import_from_csv(path)

    def _show_import_error(self, error_msg: str, origen: str = ""):
        """Muestra ventana modal con el error de importación y ofrece alternativas (CSV o PDF) sin cerrar la app."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Error de importación")
        dialog.geometry("540x320")
        dialog.resizable(False, False)
        dialog.configure(fg_color=COLORS["bg"])
        dialog.transient(self)
        dialog.grab_set()

        try:
            dialog.update_idletasks()
            x = self.winfo_x() + max(0, (self.winfo_width() - 540) // 2)
            y = self.winfo_y() + max(0, (self.winfo_height() - 320) // 2)
            dialog.geometry(f"540x320+{x}+{y}")
        except Exception:
            pass

        content = ctk.CTkFrame(
            dialog,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["card"],
            border_width=1,
            border_color=COLORS["border"],
        )
        content.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["md"])

        origen_txt = f" ({origen})" if origen else ""
        ctk.CTkLabel(
            content,
            text=f"⚠️  Error al importar datos{origen_txt}",
            font=font("heading"),
            text_color=COLORS["danger"],
            anchor="w",
        ).pack(fill="x", padx=SPACING["lg"], pady=(SPACING["md"], SPACING["xs"]))

        err_box = ctk.CTkTextbox(
            content,
            height=75,
            font=font("small"),
            text_color=COLORS["ink"],
            fg_color=COLORS["surface_alt"],
            border_width=1,
            border_color=COLORS["border"],
        )
        err_box.pack(fill="x", padx=SPACING["lg"], pady=(0, SPACING["sm"]))
        err_box.insert("1.0", str(error_msg))
        err_box.configure(state="disabled")

        ctk.CTkLabel(
            content,
            text="La operación no pudo completarse. Puedes intentar con alguna de estas fuentes alternativas:",
            font=font("body"),
            text_color=COLORS["ink_soft"],
            anchor="w",
            wraplength=460,
            justify="left",
        ).pack(fill="x", padx=SPACING["lg"], pady=(0, SPACING["sm"]))

        btn_row = ctk.CTkFrame(content, fg_color="transparent")
        btn_row.pack(fill="x", padx=SPACING["lg"], pady=(SPACING["xs"], SPACING["md"]))

        def _try_csv():
            dialog.destroy()
            self.after(60, self.import_from_csv)

        def _try_pdf():
            dialog.destroy()
            self.after(60, self.import_from_pdf)

        btn_csv = ctk.CTkButton(
            btn_row,
            text="Importar desde CSV",
            height=36,
            corner_radius=RADIUS["control"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            text_color="#FFFFFF",
            font=font("body_bold"),
            command=_try_csv,
        )
        btn_csv.pack(side="left", padx=(0, SPACING["sm"]))

        btn_pdf = ctk.CTkButton(
            btn_row,
            text="Importar desde PDF",
            height=36,
            corner_radius=RADIUS["control"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            text_color="#FFFFFF",
            font=font("body_bold"),
            command=_try_pdf,
        )
        btn_pdf.pack(side="left", padx=(0, SPACING["sm"]))

        btn_cerrar = ctk.CTkButton(
            btn_row,
            text="Cerrar",
            height=36,
            corner_radius=RADIUS["control"],
            fg_color=COLORS["surface_alt"],
            hover_color=COLORS["border"],
            text_color=COLORS["ink"],
            font=font("body"),
            command=dialog.destroy,
        )
        btn_cerrar.pack(side="right")

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

    def exit_app(self):
        """Cierra la aplicación de manera limpia exclusivamente desde Archivo > Salir."""
        self.quit()

    def _bind_global_events(self):
        """Registra listeners de teclado globales (F5, Escape, Ctrl+Z, Ctrl+S, Ctrl+O)."""
        self.bind_all("<F5>", lambda e: self.refresh_all())
        self.bind_all("<Escape>", lambda e: self._close_more_options_panel())
        self.bind_all("<Control-z>", lambda e: self.undo_delete())
        self.bind_all("<Control-Z>", lambda e: self.undo_delete())
        self.bind_all("<Control-s>", lambda e: self.save_data())
        self.bind_all("<Control-S>", lambda e: self.save_data())
        self.bind_all("<Control-o>", lambda e: self.load_from_json())
        self.bind_all("<Control-O>", lambda e: self.load_from_json())


if __name__ == "__main__":
    app = App()
    app.mainloop()
