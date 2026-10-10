# -*- coding: utf-8 -*-
"""Design system and styles for the desktop application."""

from typing import Dict, Any, Optional
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

# Paleta de colores curada del sistema de diseño (Tema claro profesional con acento Índigo)
COLORS: Dict[str, str] = {
    # Superficies y fondos
    'bg': '#F8FAFC',
    'surface': '#FFFFFF',
    'surface_alt': '#F1F5F9',
    'surface_subtle': '#F8FAFC',
    'border': '#E2E8F0',
    'border_subtle': '#EDF2F7',

    # Jerarquía tipográfica (Ink)
    'ink': '#0F172A',
    'ink_soft': '#334155',
    'muted': '#64748B',
    'muted_light': '#94A3B8',

    # Colores de acento e interacción (Índigo profesional)
    'accent': '#4F46E5',
    'accent_hover': '#4338CA',
    'accent_soft': '#EEF2FF',
    'accent_border': '#C7D2FE',

    # Estados semánticos y destructivos
    'danger': '#DC2626',
    'danger_hover': '#FEE2E2',
    'danger_soft': '#FEF2F2',
    'danger_border': '#FECACA',
    'success': '#16A34A',
    'success_soft': '#F0FDF4',
    'success_border': '#BBF7D0',
    'warning': '#D97706',
    'warning_soft': '#FFFBEB',
    'warning_border': '#FDE68A',

    # Badges y estados
    'badge_active_bg': '#DCFCE7',
    'badge_active_text': '#15803D',
    'badge_inactive_bg': '#F1F5F9',
    'badge_inactive_text': '#64748B',

    # Pestañas y selectores segmentados
    'segment_bg': '#E2E8F0',

    # Utilidades
    'white': '#FFFFFF',
    'transparent': 'transparent',

    # Alias para compatibilidad
    'fg': '#0F172A',
    'accent_text': '#FFFFFF',
}

# Paleta curada para gráficos estadísticos
CHART_COLORS = ['#4F46E5', '#0D9488', '#F59E0B', '#8B5CF6', '#64748B']
BAR_WIDTH = 0.52

# Alias de compatibilidad previa
COLOR_PALETTE = COLORS

# Escala de espaciado estándar (múltiplos de 4)
SPACING: Dict[str, int] = {
    'xs': 4,
    'sm': 8,
    'md': 16,
    'lg': 24,
    'xl': 32,
}

# Radios de curvatura de esquinas consistentes
RADIUS: Dict[str, int] = {
    'card': 12,
    'control': 8,
    'badge': 6,
    'pill': 100,
}

# Altura estándar unificada para todos los controles interactivos
CONTROL_HEIGHT = 36

# Especificación y escala de tipografía
FONT_SPECS: Dict[str, Dict[str, Any]] = {
    'display': {'size': 24, 'weight': 'bold'},
    'title': {'size': 18, 'weight': 'bold'},
    'heading': {'size': 14, 'weight': 'bold'},
    'body': {'size': 13, 'weight': 'normal'},
    'small': {'size': 11, 'weight': 'normal'},
    'badge': {'size': 11, 'weight': 'bold'},
    'stat': {'size': 28, 'weight': 'bold'},
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
    """Calcula el factor de escala DPI para ajustar rowheight y paddings."""
    try:
        if root is not None:
            dpi = float(root.winfo_fpixels('1i'))
            scale = dpi / 96.0
            return scale if scale > 0 else 1.0
    except Exception:
        pass
    return 1.0


def button(master, text: str, variant: str = 'secondary', command=None, **kwargs) -> ctk.CTkButton:
    """Crea un CTkButton con sistema estricto de jerarquía visual.

    Jerarquías disponibles:
    - 'primary': Relleno en color acento (índigo), texto blanco.
    - 'secondary': Fondo blanco con borde sutil y texto oscuro.
    - 'danger': Destructivo en rojo suave (fondo tenue, texto y borde rojo).
    - 'tertiary' / 'ghost': Fondo blanco o transparente con ícono/borde sutil.
    """
    base_kwargs: Dict[str, Any] = {
        'height': CONTROL_HEIGHT,
        'corner_radius': RADIUS['control'],
        'font': font('body'),
        'command': command,
    }

    if variant == 'primary':
        variant_kwargs = {
            'fg_color': COLORS['accent'],
            'hover_color': COLORS['accent_hover'],
            'text_color': COLORS['white'],
            'text_color_disabled': COLORS['muted_light'],
            'border_width': 0,
        }
    elif variant == 'secondary':
        variant_kwargs = {
            'fg_color': COLORS['surface'],
            'hover_color': COLORS['surface_alt'],
            'text_color': COLORS['ink'],
            'text_color_disabled': COLORS['muted_light'],
            'border_width': 1,
            'border_color': COLORS['border'],
        }
    elif variant == 'danger':
        # Destructivo en rojo suave con hover sutil
        variant_kwargs = {
            'fg_color': COLORS['danger_soft'],
            'hover_color': COLORS['danger_hover'],
            'text_color': COLORS['danger'],
            'text_color_disabled': COLORS['muted_light'],
            'border_width': 1,
            'border_color': COLORS['danger_border'],
        }
    elif variant in ('tertiary', 'ghost'):
        # Terciario para acciones como 'Actualizar' con ícono
        variant_kwargs = {
            'fg_color': COLORS['surface'],
            'hover_color': COLORS['surface_alt'],
            'text_color': COLORS['ink_soft'],
            'text_color_disabled': COLORS['muted_light'],
            'border_width': 1,
            'border_color': COLORS['border'],
        }
    else:
        variant_kwargs = {
            'fg_color': COLORS['surface'],
            'hover_color': COLORS['surface_alt'],
            'text_color': COLORS['ink'],
            'text_color_disabled': COLORS['muted_light'],
            'border_width': 1,
            'border_color': COLORS['border'],
        }

    merged_kwargs = {**base_kwargs, **variant_kwargs, **kwargs}
    return ctk.CTkButton(master, text=text, **merged_kwargs)


def entry(master, placeholder_text: str = '', width: Optional[int] = None, **kwargs) -> ctk.CTkEntry:
    """Crea un CTkEntry con bordes sutiles y dimensiones unificadas."""
    base_kwargs: Dict[str, Any] = {
        'height': CONTROL_HEIGHT,
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


def option_menu(master, values, variable=None, command=None, width: int = 150, **kwargs) -> ctk.CTkOptionMenu:
    """Crea un CTkOptionMenu estilizado con altura unificada y estética limpia."""
    base_kwargs: Dict[str, Any] = {
        'values': values,
        'variable': variable,
        'command': command,
        'height': CONTROL_HEIGHT,
        'width': width,
        'corner_radius': RADIUS['control'],
        'font': font('body'),
        'dropdown_font': font('body'),
        'fg_color': COLORS['surface'],
        'button_color': COLORS['surface_alt'],
        'button_hover_color': COLORS['border'],
        'text_color': COLORS['ink'],
        'dropdown_fg_color': COLORS['surface'],
        'dropdown_text_color': COLORS['ink'],
        'dropdown_hover_color': COLORS['accent_soft'],
        'dynamic_resizing': False,
    }
    merged_kwargs = {**base_kwargs, **kwargs}
    return ctk.CTkOptionMenu(master, **merged_kwargs)


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
    """Configura las pestañas de CTkTabview con estilo moderno."""
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
    try:
        tabview._segmented_button.configure(
            corner_radius=RADIUS['control'],
            font=font('heading'),
            height=34,
        )
    except Exception:
        pass


def apply_ttk_styles(root=None):
    """Aplica temas y estilos limpios para ttk.Treeview y ttk.Scrollbar."""
    style = ttk.Style(root)
    try:
        style.theme_use('clam')
    except Exception:
        pass

    dpi_scale = get_dpi_scale(root)
    row_height = int(round(38 * dpi_scale))
    pad_x = int(round(14 * dpi_scale))
    pad_y = int(round(10 * dpi_scale))

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
        font=('Segoe UI', 9, 'bold'),
        relief='flat',
        borderwidth=0,
        padding=(pad_x, pad_y),
    )

    style.map(
        'Pea.Treeview.Heading',
        background=[('active', COLORS['border']), ('pressed', COLORS['border'])],
        foreground=[('active', COLORS['ink'])],
    )

    # Scrollbar vertical delgada y minimalista
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
        troughcolor=COLORS['surface'],
        background=COLORS['border'],
        bordercolor=COLORS['surface'],
        lightcolor=COLORS['surface'],
        darkcolor=COLORS['surface'],
        arrowcolor=COLORS['surface'],
        gripcount=0,
        width=8,
    )

    style.map(
        'Pea.Vertical.TScrollbar',
        background=[('active', COLORS['muted'])],
    )


def apply_treeview_tags(tree: ttk.Treeview):
    """Configura las etiquetas zebra, hover y estados de color en el Treeview."""
    tree.tag_configure('odd', background=COLORS['surface'], foreground=COLORS['ink'])
    tree.tag_configure('even', background=COLORS['surface_subtle'], foreground=COLORS['ink'])
    tree.tag_configure('hover', background=COLORS['accent_soft'], foreground=COLORS['ink'])
    tree.tag_configure('active_badge', foreground=COLORS['badge_active_text'])
    tree.tag_configure('inactive_badge', foreground=COLORS['badge_inactive_text'])


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
        mpl.rcParams['grid.alpha'] = 0.6
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
    ax.yaxis.grid(True, color=COLORS['border'], linestyle='-', linewidth=0.8, alpha=0.6)
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