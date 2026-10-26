# -*- coding: utf-8 -*-
"""
PEA-i  ·  Sistema de diseño central
=====================================
Paleta institucional Unicesar refinada:
- Sidebar: Azul marino slate #0B132B con hover #1C2541 y acento activo
- Header: Azul institucional #1E3A8A con contraste nítido y texto blanco
- Fondo del contenido: #F8FAFC (Slate-50)
- Tarjetas: Blanco #FFFFFF con borde sutil #E2E8F0 y radio 12
- Primario: Azul #2563EB (hover #1D4ED8)
- Éxito: Esmeralda #10B981 (soft #ECFDF5)
- Advertencia: Ámbar #F59E0B (soft #FFFBEB)
- Peligro: Rojo #EF4444 (hover #FEE2E2, soft #FEF2F2)
- Tipografía Segoe UI, controles de 36-40 px, radio 8
- Íconos de texto Unicode integrados sin archivos externos
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
    'sidebar':            '#0B132B',       # Azul marino slate profundo
    'sidebar_hover':      '#1C2541',       # Hover elementos sidebar
    'sidebar_active':     '#1D4ED8',       # Fondo elemento activo sidebar
    'sidebar_indicator':  '#38BDF8',       # Barra de acento celeste brillante
    'sidebar_text':       '#94A3B8',       # Texto inactivo sidebar (Slate-400)
    'sidebar_text_active':'#FFFFFF',       # Texto activo sidebar
    'sidebar_border':     '#1E293B',       # Divisor sidebar (Slate-800)

    'header':             '#1E3A8A',       # Azul institucional Unicesar
    'header_text':        '#FFFFFF',       # Título header blanco bold
    'header_sub':         '#BFDBFE',       # Subtítulo header celeste suave
    'header_badge_bg':    '#172554',       # Fondo badge en header

    # — Superficies y fondos —
    'bg':                 '#F8FAFC',       # Fondo general de la aplicación (Slate-50)
    'surface':            '#FFFFFF',       # Fondo tarjetas y contenedores
    'surface_alt':        '#F1F5F9',       # Fondo alterno / hover suave (Slate-100)
    'surface_subtle':     '#F8FAFC',       # Fondo muy suave
    'border':             '#E2E8F0',       # Bordes principales (Slate-200)
    'border_subtle':      '#F1F5F9',       # Borde sutil

    # — Jerarquía tipográfica (Ink) —
    'ink':                '#0F172A',       # Texto principal oscuro (Slate-900)
    'ink_soft':           '#334155',       # Texto intermedio (Slate-700)
    'muted':              '#64748B',       # Texto secundario (Slate-500)
    'muted_light':        '#94A3B8',       # Texto deshabilitado / placeholder (Slate-400)

    # — Colores primarios y acentos —
    'primary':            '#2563EB',       # Azul primario (Blue-600)
    'primary_hover':      '#1D4ED8',       # Hover azul primario (Blue-700)
    'accent':             '#2563EB',       # Alias primario
    'accent_hover':       '#1D4ED8',
    'accent_soft':        '#EFF6FF',       # Fondo azul muy suave para selección (Blue-50)
    'accent_border':      '#BFDBFE',       # Borde acento suave (Blue-200)

    # — Estados semánticos —
    'success':            '#10B981',       # Verde esmeralda (Emerald-500)
    'success_hover':      '#059669',       # Emerald-600
    'success_soft':       '#ECFDF5',       # Fondo badge activo (Emerald-50)
    'success_border':     '#A7F3D0',       # Borde éxito suave (Emerald-200)

    'warning':            '#F59E0B',       # Ámbar alerta (Amber-500)
    'warning_hover':      '#D97706',       # Amber-600
    'warning_soft':       '#FFFBEB',       # Fondo badge alerta (Amber-50)
    'warning_border':     '#FDE68A',       # Borde alerta suave (Amber-200)

    'danger':             '#EF4444',       # Rojo peligro (Rose-500)
    'danger_hover':       '#FEE2E2',       # Hover botón peligro
    'danger_soft':        '#FEF2F2',       # Fondo peligro suave (Rose-50)
    'danger_border':      '#FCA5A5',       # Borde peligro suave (Rose-300)

    # — Badges de estado —
    'badge_active_bg':    '#ECFDF5',
    'badge_active_text':  '#059669',
    'badge_inactive_bg':  '#F1F5F9',
    'badge_inactive_text':'#64748B',

    # — Pestañas / selectores —
    'segment_bg':         '#E2E8F0',

    # — Utilidades —
    'white':              '#FFFFFF',
    'transparent':        'transparent',

    # — Alias de retrocompatibilidad —
    'fg':                 '#0F172A',
    'accent_text':        '#FFFFFF',
}

COLOR_PALETTE = COLORS

# Paleta curada para gráficos estadísticos (azul, esmeralda, ámbar, violeta, pizarra)
CHART_COLORS: List[str] = ['#2563EB', '#10B981', '#F59E0B', '#8B5CF6', '#64748B', '#06B6D4', '#EC4899']
BAR_WIDTH: float = 0.52

# ╔══════════════════════════════════════════════════════════════════════╗
# ║  2. CONSTANTES DE ÍCONOS UNICODE (Sin archivos de imagen)         ║
# ╚══════════════════════════════════════════════════════════════════════╝

ICONS: Dict[str, str] = {
    'grupos':           '👥',
    'investigadores':   '🧑‍🔬',
    'productos':        '📦',
    'indicadores':      '📈',
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
    'undo':             '↶',
    'info':             'ℹ',
    'alerta':           '⚠️',
    'limpiar':          '✕',
    'carpeta':          '📁',
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
    'display':    {'size': 22, 'weight': 'bold'},
    'title':      {'size': 18, 'weight': 'bold'},
    'heading':    {'size': 14, 'weight': 'bold'},
    'subheading': {'size': 13, 'weight': 'bold'},
    'body':       {'size': 13, 'weight': 'normal'},
    'body_bold':  {'size': 13, 'weight': 'bold'},
    'texto':      {'size': 12, 'weight': 'normal'},
    'small':      {'size': 11, 'weight': 'normal'},
    'small_bold': {'size': 11, 'weight': 'bold'},
    'badge':      {'size': 11, 'weight': 'bold'},
    'stat':       {'size': 26, 'weight': 'bold'},
    'icon_lg':    {'size': 26, 'weight': 'bold'},
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
    'input':   8,        # Alias para campos de entrada y combos
    'button':  8,        # Alias para botones
    'badge':   6,        # Badges pequeños con radio 6
    'pill':    100,      # Píldoras redondas
}

CONTROL_HEIGHT: int = 38  # Altura estándar de controles (36-40 px)

SPACING: Dict[str, int] = {
    'xs': 4,
    'sm': 8,
    'md': 16,
    'lg': 20,
    'xl': 28,
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
    """Botón blanco con borde sutil #E2E8F0 y texto oscuro."""
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


def boton_advertencia(master, text: str = '', command=None, **kwargs) -> ctk.CTkButton:
    """Botón ámbar/advertencia (hover #D97706), texto blanco."""
    kwargs.pop('variant', None)
    base: Dict[str, Any] = {
        'height':               CONTROL_HEIGHT,
        'corner_radius':        RADIUS['control'],
        'font':                 font('body_bold'),
        'command':              command,
        'fg_color':             COLORS['warning'],
        'hover_color':          COLORS['warning_hover'],
        'text_color':           COLORS['white'],
        'text_color_disabled':  COLORS['muted_light'],
        'border_width':         0,
    }
    return ctk.CTkButton(master, text=text, **{**base, **kwargs})


def boton_peligro(master, text: str = '', command=None, **kwargs) -> ctk.CTkButton:
    """Botón destructivo: borde y texto rojo #EF4444, fondo blanco, hover #FEE2E2."""
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
    w = kwargs.pop('width', CONTROL_HEIGHT)
    h = kwargs.pop('height', CONTROL_HEIGHT)
    base: Dict[str, Any] = {
        'width':                w,
        'height':               h,
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


def boton_fantasma(master, text: str = '', command=None, **kwargs) -> ctk.CTkButton:
    """Botón transparente con hover suave para acciones secundarias o de deselección."""
    kwargs.pop('variant', None)
    h = kwargs.pop('height', 30)
    base: Dict[str, Any] = {
        'height':               h,
        'corner_radius':        RADIUS['control'],
        'font':                 font('body'),
        'command':              command,
        'fg_color':             'transparent',
        'hover_color':          COLORS['surface_alt'],
        'text_color':           COLORS['ink_soft'],
        'text_color_disabled':  COLORS['muted_light'],
        'border_width':         0,
    }
    return ctk.CTkButton(master, text=text, **{**base, **kwargs})


def button(master, text: str = '', command=None, variant: str = 'secondary', **kwargs) -> ctk.CTkButton:
    """Fábrica de botones compatible con el parámetro variant."""
    if variant == 'primary':
        return boton_primario(master, text=text, command=command, **kwargs)
    elif variant == 'danger':
        return boton_peligro(master, text=text, command=command, **kwargs)
    elif variant == 'warning':
        return boton_advertencia(master, text=text, command=command, **kwargs)
    elif variant == 'icon':
        return boton_icono(master, text=text, command=command, **kwargs)
    elif variant in ('ghost', 'tertiary'):
        return boton_fantasma(master, text=text, command=command, **kwargs)
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
    """CTkOptionMenu estilizado con altura estándar."""
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
    """Contenedor de tarjeta blanco con borde #E2E8F0 y radio 12."""
    base: Dict[str, Any] = {
        'corner_radius': corner_radius,
        'fg_color':      COLORS['surface'],
        'border_width':  1,
        'border_color':  COLORS['border'],
    }
    return ctk.CTkFrame(master, **{**base, **kwargs})


# Alias de compatibilidad previa
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
    row_height = int(round(44 * dpi_scale))
    pad_x = int(round(12 * dpi_scale))
    pad_y = int(round(9 * dpi_scale))

    style.layout('Pea.Treeview', [('Treeview.treearea', {'sticky': 'nswe'})])

    style.configure(
        'Pea.Treeview',
        background=COLORS['surface'],
        foreground=COLORS['ink'],
        fieldbackground=COLORS['surface'],
        rowheight=row_height,
        font=(FONT_FAMILY, 11),
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
        background='#F8FAFC',
        foreground=COLORS['muted'],
        font=(FONT_FAMILY, 10, 'bold'),
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
        width=7,
    )

    return style


configurar_treeview = setup_treeview_style


def apply_treeview_tags(tree: ttk.Treeview):
    """Configura las etiquetas de alternancia de filas y estado."""
    tree.tag_configure('odd',            background=COLORS['surface'],     foreground=COLORS['ink'])
    tree.tag_configure('even',           background='#F8FAFC',             foreground=COLORS['ink'])
    tree.tag_configure('hover',          background=COLORS['accent_soft'], foreground=COLORS['ink'])
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
    ax.spines['left'].set_linewidth(1.0)
    ax.spines['bottom'].set_linewidth(1.0)
    ax.grid(axis='y', linestyle='--', alpha=0.35, color=COLORS['border'])
    ax.tick_params(colors=COLORS['ink_soft'], labelsize=9.5, width=0.8)


def setup_app(root):
    """Inicializa el tema CustomTkinter y estilos del Treeview."""
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    root.configure(fg_color=COLORS['bg'])
    setup_treeview_style(root)