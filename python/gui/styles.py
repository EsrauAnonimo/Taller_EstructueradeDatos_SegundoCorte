# -*- coding: utf-8 -*-
"""
PEA-i  ·  Sistema de diseño central
=====================================
Paleta institucional Unicesar:
- Sidebar: Azul marino oscuro #0F1B3D
- Header: Azul #1E3A8A
- Fondo del contenido: #F3F4F6
- Tarjetas: Blanco #FFFFFF con borde #E5E7EB y radio 12
- Primario: Azul #2563EB (hover #1D4ED8)
- Éxito: #16A34A sobre #DCFCE7
- Peligro: #DC2626 (borde y texto rojo, fondo blanco, hover #FEE2E2)
- Tipografía Segoe UI, controles de 36-44 px, radio 8
- Íconos de texto Unicode sin archivos de imagen externos
"""

from typing import Dict, Any, Optional, List, Callable
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

# ╔══════════════════════════════════════════════════════════════════════╗
# ║  1. PALETA DE COLORES                                              ║
# ╚══════════════════════════════════════════════════════════════════════╝

COLORS: Dict[str, str] = {
    # — Estructura principal —
    'sidebar':          '#0F1B3D',       # Azul marino oscuro sidebar
    'sidebar_hover':    '#1E293B',       # Hover elementos sidebar
    'sidebar_active':   '#1D4ED8',       # Fondo elemento activo sidebar
    'sidebar_text':     '#94A3B8',       # Texto inactivo sidebar
    'sidebar_text_active':'#FFFFFF',     # Texto activo sidebar
    'sidebar_border':   '#1E293B',       # Divisor sidebar

    'header':           '#1E3A8A',       # Azul header
    'header_text':      '#FFFFFF',       # Título header blanco bold
    'header_sub':       '#BFDBFE',       # Subtítulo header celeste suave

    # — Superficies y fondos —
    'bg':               '#F3F4F6',       # Fondo general de la aplicación
    'surface':          '#FFFFFF',       # Fondo tarjetas y contenedores
    'surface_alt':      '#F9FAFB',       # Fondo alterno / hover suave
    'surface_subtle':   '#F3F4F6',
    'border':           '#E5E7EB',       # Bordes principales
    'border_subtle':    '#F3F4F6',

    # — Jerarquía tipográfica (Ink) —
    'ink':              '#111827',       # Texto principal oscuro
    'ink_soft':         '#374151',       # Texto intermedio
    'muted':            '#6B7280',       # Texto secundario / gris
    'muted_light':      '#9CA3AF',       # Texto deshabilitado / placeholder

    # — Colores primarios y acentos —
    'primary':          '#2563EB',       # Azul primario
    'primary_hover':    '#1D4ED8',       # Hover azul primario
    'accent':           '#2563EB',       # Alias primario
    'accent_hover':     '#1D4ED8',
    'accent_soft':      '#EFF6FF',       # Fondo azul muy suave para selección
    'accent_border':    '#BFDBFE',

    # — Estados semánticos —
    'success':          '#16A34A',       # Verde éxito
    'success_soft':     '#DCFCE7',       # Fondo badge activo
    'success_border':   '#BBF7D0',
    'warning':          '#D97706',       # Ámbar alerta
    'warning_soft':     '#FFFBEB',
    'warning_border':   '#FDE68A',
    'danger':           '#DC2626',       # Rojo peligro
    'danger_hover':     '#FEE2E2',       # Hover botón peligro
    'danger_soft':      '#FEE2E2',
    'danger_border':    '#DC2626',

    # — Badges de estado —
    'badge_active_bg':  '#DCFCE7',
    'badge_active_text':'#16A34A',
    'badge_inactive_bg':'#F3F4F6',
    'badge_inactive_text':'#6B7280',

    # — Pestañas / selectores —
    'segment_bg':       '#E5E7EB',

    # — Utilidades —
    'white':            '#FFFFFF',
    'transparent':      'transparent',

    # — Alias de retrocompatibilidad —
    'fg':               '#111827',
    'accent_text':      '#FFFFFF',
}

COLOR_PALETTE = COLORS

# Paleta curada para gráficos estadísticos (azul, teal, ámbar, púrpura, gris)
CHART_COLORS: List[str] = ['#2563EB', '#0D9488', '#F59E0B', '#8B5CF6', '#6B7280']
BAR_WIDTH: float = 0.52

# ╔══════════════════════════════════════════════════════════════════════╗
# ║  2. CONSTANTES DE ÍCONOS UNICODE (Sin archivos de imagen)         ║
# ╚══════════════════════════════════════════════════════════════════════╝

ICONS: Dict[str, str] = {
    'grupos':           '👥',
    'investigadores':   '🧑‍🔬',
    'productos':        '📦',
    'estadisticas':     '📊',
    'buscar':           '🔍',
    'actualizar':       '⟳',
    'descargar':        '⬇',
    'crear':            '＋',
    'acciones':         '⋮',
    'editar':           '✎',
    'eliminar':         '🗑',
    'usuario':          '👤',
    'opciones':         '⚙',
    'deseleccionar':    '✕',
    'check':            '✓',
    'check_box_on':     '☑',
    'check_box_off':    '☐',
    'asc':              '▲',
    'desc':             '▼',
    'filtro':           '⚡',
}

# ╔══════════════════════════════════════════════════════════════════════╗
# ║  3. TIPOGRAFÍA  –  Segoe UI                                        ║
# ╚══════════════════════════════════════════════════════════════════════╝

FONT_FAMILY = 'Segoe UI'

TITULO      = (FONT_FAMILY, 24, 'bold')
SUBTITULO   = (FONT_FAMILY, 13, 'normal')
TEXTO       = (FONT_FAMILY, 12, 'normal')
PEQUEÑO     = (FONT_FAMILY, 11, 'normal')

FONT_SPECS: Dict[str, Dict[str, Any]] = {
    'display':  {'size': 24, 'weight': 'bold'},
    'title':    {'size': 18, 'weight': 'bold'},
    'heading':  {'size': 14, 'weight': 'bold'},
    'body':     {'size': 13, 'weight': 'normal'},
    'body_bold':{'size': 13, 'weight': 'bold'},
    'texto':    {'size': 12, 'weight': 'normal'},
    'small':    {'size': 11, 'weight': 'normal'},
    'small_bold':{'size': 11, 'weight': 'bold'},
    'badge':    {'size': 11, 'weight': 'bold'},
    'stat':     {'size': 28, 'weight': 'bold'},
    'icon_lg':  {'size': 28, 'weight': 'bold'},
}

_FONT_CACHE: Dict[str, ctk.CTkFont] = {}


def font(role: str) -> ctk.CTkFont:
    """Retorna una fuente CTkFont desde caché según el rol semántico."""
    if role not in _FONT_CACHE:
        spec = FONT_SPECS.get(role, FONT_SPECS['body'])
        _FONT_CACHE[role] = ctk.CTkFont(
            family=FONT_FAMILY,
            size=spec['size'],
            weight=spec['weight'],
        )
    return _FONT_CACHE[role]


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  4. MEDIDAS  –  Radio, alturas y espaciado                         ║
# ╚══════════════════════════════════════════════════════════════════════╝

RADIUS: Dict[str, int] = {
    'card':    12,       # Tarjetas con radio 12
    'control': 8,        # Botones e inputs con radio 8
    'badge':   6,
    'pill':    100,
}

CONTROL_HEIGHT: int = 38  # Rango 36-44 px

SPACING: Dict[str, int] = {
    'xs': 4,
    'sm': 8,
    'md': 16,
    'lg': 24,
    'xl': 32,
}

SPACING_BASE: int = 8


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  5. FUNCIONES FÁBRICA  –  Widgets estilizados                       ║
# ╚══════════════════════════════════════════════════════════════════════╝

def boton_primario(master, text: str = '', command=None, **kwargs) -> ctk.CTkButton:
    """Botón azul #2563EB sólido (hover #1D4ED8), texto blanco."""
    kwargs.pop('variant', None)
    base: Dict[str, Any] = {
        'height':               CONTROL_HEIGHT,
        'corner_radius':        RADIUS['control'],
        'font':                 font('body_bold'),
        'command':              command,
        'fg_color':             COLORS['primary'],
        'hover_color':          COLORS['primary_hover'],
        'text_color':           COLORS['white'],
        'text_color_disabled':  COLORS['muted_light'],
        'border_width':         0,
    }
    return ctk.CTkButton(master, text=text, **{**base, **kwargs})


def boton_secundario(master, text: str = '', command=None, **kwargs) -> ctk.CTkButton:
    """Botón blanco con borde sutil #E5E7EB y texto oscuro."""
    kwargs.pop('variant', None)
    base: Dict[str, Any] = {
        'height':               CONTROL_HEIGHT,
        'corner_radius':        RADIUS['control'],
        'font':                 font('body'),
        'command':              command,
        'fg_color':             COLORS['surface'],
        'hover_color':          COLORS['surface_alt'],
        'text_color':           COLORS['ink'],
        'text_color_disabled':  COLORS['muted_light'],
        'border_width':         1,
        'border_color':         COLORS['border'],
    }
    return ctk.CTkButton(master, text=text, **{**base, **kwargs})


def boton_peligro(master, text: str = '', command=None, **kwargs) -> ctk.CTkButton:
    """Botón destructivo: borde y texto rojo #DC2626, fondo blanco, hover #FEE2E2."""
    kwargs.pop('variant', None)
    base: Dict[str, Any] = {
        'height':               CONTROL_HEIGHT,
        'corner_radius':        RADIUS['control'],
        'font':                 font('body_bold'),
        'command':              command,
        'fg_color':             COLORS['white'],
        'hover_color':          COLORS['danger_hover'],
        'text_color':           COLORS['danger'],
        'text_color_disabled':  COLORS['muted_light'],
        'border_width':         1,
        'border_color':         COLORS['danger'],
    }
    return ctk.CTkButton(master, text=text, **{**base, **kwargs})


def boton_icono(master, text: str = '', command=None, **kwargs) -> ctk.CTkButton:
    """Botón cuadrado discreto pensado para íconos (ej. «⟳», «✕»)."""
    kwargs.pop('variant', None)
    base: Dict[str, Any] = {
        'width':                CONTROL_HEIGHT,
        'height':               CONTROL_HEIGHT,
        'corner_radius':        RADIUS['control'],
        'font':                 font('body'),
        'command':              command,
        'fg_color':             COLORS['surface'],
        'hover_color':          COLORS['surface_alt'],
        'text_color':           COLORS['ink_soft'],
        'text_color_disabled':  COLORS['muted_light'],
        'border_width':         1,
        'border_color':         COLORS['border'],
    }
    return ctk.CTkButton(master, text=text, **{**base, **kwargs})


def button(master, text: str = '', command=None, variant: str = 'secondary', **kwargs) -> ctk.CTkButton:
    """Fábrica de botones compatible con el parámetro variant."""
    if variant == 'primary':
        return boton_primario(master, text=text, command=command, **kwargs)
    elif variant == 'danger':
        return boton_peligro(master, text=text, command=command, **kwargs)
    elif variant == 'icon':
        return boton_icono(master, text=text, command=command, **kwargs)
    elif variant == 'ghost':
        h = kwargs.pop('height', 28)
        base = {
            'height':               h,
            'corner_radius':        RADIUS['control'],
            'font':                 font('body'),
            'command':              command,
            'fg_color':             'transparent',
            'hover_color':          COLORS['surface_alt'],
            'text_color':           COLORS['ink'],
            'border_width':         0,
        }
        return ctk.CTkButton(master, text=text, **{**base, **kwargs})
    else:
        return boton_secundario(master, text=text, command=command, **kwargs)


def entrada_busqueda(
    master,
    placeholder: str = '🔍  Buscar por código, nombre o líder...',
    width: Optional[int] = 340,
    **kwargs,
) -> ctk.CTkEntry:
    """Campo de búsqueda amplio con placeholder e ícono de lupa."""
    ph = kwargs.pop('placeholder_text', placeholder)
    base: Dict[str, Any] = {
        'height':                   CONTROL_HEIGHT,
        'corner_radius':            RADIUS['control'],
        'border_width':             1,
        'border_color':             COLORS['border'],
        'fg_color':                 COLORS['surface'],
        'text_color':               COLORS['ink'],
        'placeholder_text_color':   COLORS['muted'],
        'font':                     font('body'),
    }
    if width is not None:
        base['width'] = width

    e = ctk.CTkEntry(master, placeholder_text=ph, **{**base, **kwargs})

    def _on_focus_in(_evt):
        try:
            e.configure(border_color=COLORS['primary'])
        except Exception:
            pass

    def _on_focus_out(_evt):
        try:
            e.configure(border_color=COLORS['border'])
        except Exception:
            pass

    e.bind('<FocusIn>', _on_focus_in)
    e.bind('<FocusOut>', _on_focus_out)
    return e


def combo(
    master,
    values: list,
    variable=None,
    command=None,
    width: int = 160,
    **kwargs,
) -> ctk.CTkOptionMenu:
    """CTkOptionMenu estilizado."""
    base: Dict[str, Any] = {
        'values':               values,
        'variable':             variable,
        'command':              command,
        'height':               CONTROL_HEIGHT,
        'width':                width,
        'corner_radius':        RADIUS['control'],
        'font':                 font('body'),
        'dropdown_font':        font('body'),
        'fg_color':             COLORS['surface'],
        'button_color':         COLORS['surface_alt'],
        'button_hover_color':   COLORS['border'],
        'text_color':           COLORS['ink'],
        'dropdown_fg_color':    COLORS['surface'],
        'dropdown_text_color':  COLORS['ink'],
        'dropdown_hover_color': COLORS['accent_soft'],
        'dynamic_resizing':     False,
    }
    return ctk.CTkOptionMenu(master, **{**base, **kwargs})


def tarjeta(master, corner_radius: int = 12, **kwargs) -> ctk.CTkFrame:
    """Contenedor de tarjeta blanco con borde #E5E7EB y radio 12."""
    base: Dict[str, Any] = {
        'corner_radius': corner_radius,
        'fg_color':      COLORS['surface'],
        'border_width':  1,
        'border_color':  COLORS['border'],
    }
    return ctk.CTkFrame(master, **{**base, **kwargs})


# Alias de compatibilidad previa
button = boton_secundario
card = tarjeta
entry = entrada_busqueda


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  6. ESTILO DEL TREEVIEW (ttk.Style con tema 'clam')                 ║
# ╚══════════════════════════════════════════════════════════════════════╝

def get_dpi_scale(root) -> float:
    """Calcula el factor de escala DPI para renderizado nítido."""
    try:
        dpi = root.winfo_fpixels('1i')
        return max(1.0, dpi / 96.0)
    except Exception:
        return 1.0


def setup_treeview_style(root) -> ttk.Style:
    """Configura el estilo Pea.Treeview sobre el tema clam.
    
    Filas amplias, encabezado gris claro bold, hover suave y sin bordes toscos.
    """
    style = ttk.Style(root)
    try:
        style.theme_use('clam')
    except Exception:
        pass

    dpi_scale = get_dpi_scale(root)
    row_height = int(round(46 * dpi_scale))
    pad_x = int(round(12 * dpi_scale))
    pad_y = int(round(10 * dpi_scale))

    style.layout('Pea.Treeview', [('Treeview.treearea', {'sticky': 'nswe'})])

    style.configure(
        'Pea.Treeview',
        background=COLORS['surface'],
        foreground=COLORS['ink'],
        fieldbackground=COLORS['surface'],
        rowheight=row_height,
        font=(FONT_FAMILY, 12),
        borderwidth=0,
        relief='flat',
    )

    style.map(
        'Pea.Treeview',
        background=[('selected', COLORS['accent_soft'])],
        foreground=[('selected', COLORS['primary'])],
    )

    style.configure(
        'Pea.Treeview.Heading',
        background='#F9FAFB',
        foreground=COLORS['muted'],
        font=(FONT_FAMILY, 11, 'bold'),
        relief='flat',
        borderwidth=0,
        padding=(pad_x, pad_y),
    )

    style.map(
        'Pea.Treeview.Heading',
        background=[('active', COLORS['border']), ('pressed', COLORS['border'])],
        foreground=[('active', COLORS['ink'])],
    )

    # Scrollbar minimalista
    style.layout(
        'Pea.Vertical.TScrollbar',
        [(
            'Vertical.Scrollbar.trough',
            {
                'sticky': 'ns',
                'children': [
                    ('Vertical.Scrollbar.thumb', {'sticky': 'nswe', 'expand': '1'})
                ],
            },
        )],
    )

    style.configure(
        'Pea.Vertical.TScrollbar',
        troughcolor=COLORS['surface'],
        background=COLORS['border'],
        bordercolor=COLORS['surface'],
        lightcolor=COLORS['surface'],
        darkcolor=COLORS['surface'],
        arrowcolor=COLORS['surface'],
        gripcount=0,
        width=6,
    )

    return style


configurar_treeview = setup_treeview_style


def apply_treeview_tags(tree: ttk.Treeview):
    """Configura las etiquetas de alternancia de filas y estado."""
    tree.tag_configure('odd',  background=COLORS['surface'],     foreground=COLORS['ink'])
    tree.tag_configure('even', background=COLORS['surface_alt'], foreground=COLORS['ink'])
    tree.tag_configure('hover', background=COLORS['accent_soft'], foreground=COLORS['ink'])
    tree.tag_configure('active_badge',   foreground=COLORS['success'])
    tree.tag_configure('inactive_badge', foreground=COLORS['muted'])


def style_bar_axes(ax, fig=None):
    """Estiliza los ejes de matplotlib con estilo moderno, limpio y profesional."""
    if fig is not None and hasattr(fig, 'patch'):
        fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(COLORS['border'])
    ax.spines['bottom'].set_color(COLORS['border'])
    ax.grid(axis='y', linestyle='--', alpha=0.35, color=COLORS['muted_light'])
    ax.tick_params(colors=COLORS['ink_soft'], labelsize=10)


def setup_app(root):
    """Inicializa el tema CustomTkinter y estilos del Treeview."""
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    root.configure(fg_color=COLORS['bg'])
    setup_treeview_style(root)