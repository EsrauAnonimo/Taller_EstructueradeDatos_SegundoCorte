# -*- coding: utf-8 -*-
"""Design system and styles for the desktop application."""

from typing import Dict, Any, Optional
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

# Paleta de colores oficial del sistema de diseño (Tema claro)
COLORS: Dict[str, str] = {
    # Superficies y fondos
    'bg': '#F3F4F6',
    'surface': '#FFFFFF',
    'surface_alt': '#F9FAFB',
    'border': '#E3E5E9',

    # Jerarquía tipográfica (Ink)
    'ink': '#111827',
    'ink_soft': '#374151',
    'muted': '#6B7280',

    # Colores de acento e interacción
    'accent': '#2F49D1',
    'accent_hover': '#2438A8',
    'accent_soft': '#E8ECFB',

    # Estados semánticos
    'danger': '#B42318',
    'danger_hover': '#911C13',
    'danger_soft': '#FDECEA',
    'success': '#1F7A55',
    'success_soft': '#E4F4EC',

    # Pestañas y selectores segmentados
    'segment_bg': '#E5E7EB',

    # Utilidades
    'white': '#FFFFFF',
    'transparent': 'transparent',

    # Alias para compatibilidad con código existente
    'fg': '#111827',
    'accent_text': '#FFFFFF',
}

# Paleta curada para gráficos estadísticos
CHART_COLORS = ['#2F49D1', '#0E8F8A', '#C98A1B', '#7A5AF8', '#98A2B3']
BAR_WIDTH = 0.55

# Alias de compatibilidad previa
COLOR_PALETTE = COLORS

# Escala de espaciado (múltiplos de 4)
SPACING: Dict[str, int] = {
    'xs': 4,
    'sm': 8,
    'md': 16,
    'lg': 24,
    'xl': 32,
}

# Radios de curvatura de esquinas
RADIUS: Dict[str, int] = {
    'card': 12,
    'control': 8,
    'pill': 100,
}

# Especificación y escala de tipografía
FONT_SPECS: Dict[str, Dict[str, Any]] = {
    'display': {'size': 28, 'weight': 'bold'},
    'title': {'size': 18, 'weight': 'bold'},
    'heading': {'size': 14, 'weight': 'bold'},
    'body': {'size': 13, 'weight': 'normal'},
    'small': {'size': 12, 'weight': 'normal'},
    'stat': {'size': 36, 'weight': 'bold'},
}

# Caché interno de fuentes CTkFont
_FONT_CACHE: Dict[str, ctk.CTkFont] = {}


def font(role: str) -> ctk.CTkFont:
    """Retorna una fuente CTkFont desde caché según el rol semántico."""
    if role not in _FONT_CACHE:
        spec = FONT_SPECS.get(role, FONT_SPECS['body'])
        _FONT_CACHE[role] = ctk.CTkFont(
            family='Segoe UI',
            size=spec['size'],
            weight=spec['weight']
        )
    return _FONT_CACHE[role]


def get_dpi_scale(root=None) -> float:
    """Calcula el factor de escala DPI en Windows para ajustar rowheight y paddings."""
    try:
        if root is not None:
            dpi = float(root.winfo_fpixels('1i'))
            scale = dpi / 96.0
            return scale if scale > 0 else 1.0
    except Exception:
        pass
    return 1.0


def button(master, text: str, variant: str = 'secondary', command=None, **kwargs) -> ctk.CTkButton:
    """Crea un CTkButton respetando la jerarquía visual del sistema de diseño."""
    base_kwargs: Dict[str, Any] = {
        'height': 36,
        'corner_radius': RADIUS['control'],
        'font': font('body'),
        'command': command,
    }

    if variant == 'primary':
        variant_kwargs = {
            'fg_color': COLORS['accent'],
            'hover_color': COLORS['accent_hover'],
            'text_color': COLORS['white'],
            'text_color_disabled': COLORS['muted'],
            'border_width': 0,
        }
    elif variant == 'secondary':
        variant_kwargs = {
            'fg_color': COLORS['surface'],
            'hover_color': COLORS['surface_alt'],
            'text_color': COLORS['ink'],
            'text_color_disabled': COLORS['muted'],
            'border_width': 1,
            'border_color': COLORS['border'],
        }
    elif variant == 'ghost':
        variant_kwargs = {
            'fg_color': 'transparent',
            'hover_color': COLORS['surface_alt'],
            'text_color': COLORS['ink'],
            'text_color_disabled': COLORS['muted'],
            'border_width': 0,
        }
    elif variant == 'danger':
        variant_kwargs = {
            'fg_color': 'transparent',
            'hover_color': COLORS['danger_soft'],
            'text_color': COLORS['danger'],
            'text_color_disabled': COLORS['muted'],
            'border_width': 0,
        }
    else:
        variant_kwargs = {
            'fg_color': COLORS['surface'],
            'hover_color': COLORS['surface_alt'],
            'text_color': COLORS['ink'],
            'text_color_disabled': COLORS['muted'],
            'border_width': 1,
            'border_color': COLORS['border'],
        }

    merged_kwargs = {**base_kwargs, **variant_kwargs, **kwargs}
    return ctk.CTkButton(master, text=text, **merged_kwargs)


def entry(master, placeholder_text: str = '', width: Optional[int] = None, **kwargs) -> ctk.CTkEntry:
    """Crea un CTkEntry con bordes sutiles y estilos unificados."""
    base_kwargs: Dict[str, Any] = {
        'height': 36,
        'corner_radius': RADIUS['control'],
        'border_width': 1,
        'border_color': COLORS['border'],
        'fg_color': COLORS['surface'],
        'text_color': COLORS['ink'],
        'placeholder_text_color': COLORS['muted'],
        'font': font('body'),
    }
    if width is not None:
        base_kwargs['width'] = width

    merged_kwargs = {**base_kwargs, **kwargs}
    return ctk.CTkEntry(master, placeholder_text=placeholder_text, **merged_kwargs)


def card(master, **kwargs) -> ctk.CTkFrame:
    """Crea un CTkFrame contenedor con estilo de tarjeta limpia."""
    base_kwargs: Dict[str, Any] = {
        'corner_radius': RADIUS['card'],
        'fg_color': COLORS['surface'],
        'border_width': 1,
        'border_color': COLORS['border'],
    }
    merged_kwargs = {**base_kwargs, **kwargs}
    return ctk.CTkFrame(master, **merged_kwargs)


def style_tabview(tabview: ctk.CTkTabview):
    """Configura las pestañas de CTkTabview con estilo tipo pill moderno."""
    tabview.configure(
        segmented_button_fg_color=COLORS['segment_bg'],
        segmented_button_selected_color=COLORS['surface'],
        segmented_button_selected_hover_color=COLORS['surface'],
        segmented_button_unselected_color=COLORS['segment_bg'],
        segmented_button_unselected_hover_color=COLORS['border'],
        text_color=COLORS['ink'],
        text_color_disabled=COLORS['muted'],
        fg_color='transparent',
        bg_color='transparent',
    )
    # Configuración de tipografía interna del botón segmentado si está disponible
    try:
        tabview._segmented_button.configure(
            corner_radius=RADIUS['control'],
            font=font('heading'),
        )
    except Exception:
        pass


def apply_ttk_styles(root=None):
    """Aplica temas y estilos para ttk.Treeview y ttk.Scrollbar."""
    style = ttk.Style(root)
    try:
        style.theme_use('clam')
    except Exception:
        pass

    dpi_scale = get_dpi_scale(root)
    row_height = int(round(38 * dpi_scale))
    pad_x = int(round(12 * dpi_scale))
    pad_y = int(round(10 * dpi_scale))

    # Quitar el borde interno de ttk.Treeview para que lo aporte la tarjeta contenedora
    style.layout('Pea.Treeview', [('Treeview.treearea', {'sticky': 'nswe'})])

    style.configure(
        'Pea.Treeview',
        background=COLORS['surface'],
        foreground=COLORS['ink'],
        fieldbackground=COLORS['surface'],
        rowheight=row_height,
        font=('Segoe UI', 10),
        borderwidth=0,
        relief='flat',
    )

    style.map(
        'Pea.Treeview',
        background=[('selected', COLORS['accent_soft'])],
        foreground=[('selected', COLORS['accent'])],
    )

    style.configure(
        'Pea.Treeview.Heading',
        background=COLORS['surface_alt'],
        foreground=COLORS['muted'],
        font=('Segoe UI', 10, 'bold'),
        relief='flat',
        borderwidth=0,
        padding=(pad_x, pad_y),
    )

    style.map(
        'Pea.Treeview.Heading',
        background=[('active', COLORS['surface_alt']), ('pressed', COLORS['border'])],
        foreground=[('active', COLORS['ink'])],
    )

    # Scrollbar vertical delgada sin flechas
    style.layout(
        'Pea.Vertical.TScrollbar',
        [
            (
                'Vertical.Scrollbar.trough',
                {
                    'sticky': 'ns',
                    'children': [
                        ('Vertical.Scrollbar.thumb', {'sticky': 'nswe', 'expand': '1'})
                    ],
                },
            )
        ],
    )

    style.configure(
        'Pea.Vertical.TScrollbar',
        troughcolor=COLORS['surface_alt'],
        background=COLORS['border'],
        bordercolor=COLORS['surface_alt'],
        lightcolor=COLORS['surface_alt'],
        darkcolor=COLORS['surface_alt'],
        arrowcolor=COLORS['surface_alt'],
        gripcount=0,
        width=10,
    )

    style.map(
        'Pea.Vertical.TScrollbar',
        background=[('active', COLORS['muted'])],
    )


def apply_treeview_tags(tree: ttk.Treeview):
    """Configura las etiquetas zebra, hover e inactivo en una instancia de Treeview."""
    tree.tag_configure('odd', background=COLORS['surface'], foreground=COLORS['ink'])
    tree.tag_configure('even', background=COLORS['surface_alt'], foreground=COLORS['ink'])
    tree.tag_configure('hover', background=COLORS['accent_soft'], foreground=COLORS['ink'])
    tree.tag_configure('inactive', foreground=COLORS['muted'])


def apply_matplotlib_style():
    """Configura rcParams globales para unificar el aspecto de Matplotlib."""
    try:
        import matplotlib as mpl
        mpl.rcParams['font.family'] = 'sans-serif'
        mpl.rcParams['font.sans-serif'] = ['Segoe UI', 'DejaVu Sans', 'Arial']
        mpl.rcParams['figure.facecolor'] = COLORS['surface']
        mpl.rcParams['axes.facecolor'] = COLORS['surface']
        mpl.rcParams['text.color'] = COLORS['ink']
        mpl.rcParams['axes.labelcolor'] = COLORS['ink_soft']
        mpl.rcParams['xtick.color'] = COLORS['muted']
        mpl.rcParams['ytick.color'] = COLORS['muted']
        mpl.rcParams['grid.color'] = COLORS['border']
        mpl.rcParams['grid.linestyle'] = '-'
        mpl.rcParams['grid.linewidth'] = 0.8
        mpl.rcParams['grid.alpha'] = 0.7
        mpl.rcParams['axes.grid'] = True
        mpl.rcParams['axes.grid.axis'] = 'y'
    except Exception:
        pass


def style_bar_axes(ax, title: Optional[str] = None):
    """Aplica formato limpio y moderno a ejes de gráficos de barras."""
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color(COLORS['border'])
    ax.spines['bottom'].set_linewidth(1)

    ax.tick_params(left=False, bottom=False, labelsize=9, labelcolor=COLORS['muted'])
    ax.yaxis.grid(True, color=COLORS['border'], linestyle='-', linewidth=0.8, alpha=0.7)
    ax.xaxis.grid(False)

    ax.set_facecolor(COLORS['surface'])
    if ax.figure is not None:
        ax.figure.patch.set_facecolor(COLORS['surface'])

    if title:
        ax.set_title(
            title,
            loc='left',
            fontsize=12,
            fontweight='bold',
            color=COLORS['ink'],
            pad=14,
        )


def setup_app(root=None):
    """Inicializa el tema visual, estilos de ttk, matplotlib y fondo de ventana."""
    ctk.set_appearance_mode('light')
    ctk.set_default_color_theme('blue')
    if root is not None:
        try:
            root.configure(fg_color=COLORS['bg'])
        except Exception:
            pass
        apply_ttk_styles(root)
    apply_matplotlib_style()


def apply_theme(root=None):
    """Alias de compatibilidad para código existente."""
    setup_app(root)