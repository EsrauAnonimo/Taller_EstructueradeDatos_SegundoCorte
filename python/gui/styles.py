# -*- coding: utf-8 -*-
"""
PEA-i  ·  Sistema de diseño central
=====================================
Paleta índigo profesional, tipografía Segoe UI, funciones fábrica para
widgets estilizados, Treeview con tema «clam», estados vacíos y badges.

Todas las constantes y funciones anteriores se mantienen como alias para
garantizar retrocompatibilidad con los módulos que ya las importan.
"""

from typing import Dict, Any, Optional, List, Callable
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

# ╔══════════════════════════════════════════════════════════════════════╗
# ║  1. PALETA DE COLORES                                              ║
# ╚══════════════════════════════════════════════════════════════════════╝

COLORS: Dict[str, str] = {
    # — Superficies y fondos —
    'bg':               '#F3F4F6',
    'surface':          '#FFFFFF',
    'surface_alt':      '#F9FAFB',
    'surface_subtle':   '#F3F4F6',
    'border':           '#E5E7EB',
    'border_subtle':    '#F3F4F6',

    # — Jerarquía tipográfica (Ink) —
    'ink':              '#111827',
    'ink_soft':         '#374151',
    'muted':            '#6B7280',
    'muted_light':      '#9CA3AF',

    # — Acento índigo —
    'accent':           '#2F4BD8',
    'accent_hover':     '#2640B8',
    'accent_soft':      '#EEF2FF',
    'accent_border':    '#C7D2FE',

    # — Estados semánticos —
    'success':          '#16A34A',
    'success_soft':     '#DCFCE7',
    'success_border':   '#BBF7D0',
    'warning':          '#D97706',
    'warning_soft':     '#FFFBEB',
    'warning_border':   '#FDE68A',
    'danger':           '#DC2626',
    'danger_hover':     '#B91C1C',
    'danger_soft':      '#FEE2E2',
    'danger_border':    '#FECACA',

    # — Badges de estado —
    'badge_active_bg':  '#DCFCE7',
    'badge_active_text':'#15803D',
    'badge_inactive_bg':'#F3F4F6',
    'badge_inactive_text':'#6B7280',

    # — Pestañas / selectores segmentados —
    'segment_bg':       '#E5E7EB',

    # — Utilidades —
    'white':            '#FFFFFF',
    'transparent':      'transparent',

    # — Alias de compatibilidad previa —
    'fg':               '#111827',
    'accent_text':      '#FFFFFF',
}

# Paleta curada para gráficos estadísticos
CHART_COLORS: List[str] = ['#2F4BD8', '#0D9488', '#F59E0B', '#8B5CF6', '#6B7280']
BAR_WIDTH: float = 0.52

# Alias de compatibilidad previa
COLOR_PALETTE = COLORS


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  2. TIPOGRAFÍA  –  Segoe UI                                        ║
# ╚══════════════════════════════════════════════════════════════════════╝

FONT_FAMILY = 'Segoe UI'

# Constantes rápidas (familia, tamaño, peso)
TITULO      = (FONT_FAMILY, 26, 'bold')
SUBTITULO   = (FONT_FAMILY, 13, 'normal')
TEXTO       = (FONT_FAMILY, 12, 'normal')
PEQUEÑO     = (FONT_FAMILY, 11, 'normal')

FONT_SPECS: Dict[str, Dict[str, Any]] = {
    'display':  {'size': 26, 'weight': 'bold'},
    'title':    {'size': 18, 'weight': 'bold'},
    'heading':  {'size': 14, 'weight': 'bold'},
    'body':     {'size': 13, 'weight': 'normal'},
    'texto':    {'size': 12, 'weight': 'normal'},
    'small':    {'size': 11, 'weight': 'normal'},
    'badge':    {'size': 11, 'weight': 'bold'},
    'stat':     {'size': 28, 'weight': 'bold'},
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
# ║  3. MEDIDAS  –  radio, alturas y espaciado                         ║
# ╚══════════════════════════════════════════════════════════════════════╝

RADIUS: Dict[str, int] = {
    'card':    8,
    'control': 8,
    'badge':   6,
    'pill':    100,
}

CONTROL_HEIGHT: int = 36

SPACING: Dict[str, int] = {
    'xs': 4,
    'sm': 8,       # base
    'md': 16,
    'lg': 24,
    'xl': 32,
}

SPACING_BASE: int = 8


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  4. FUNCIONES FÁBRICA  –  Widgets ya estilizados                   ║
# ╚══════════════════════════════════════════════════════════════════════╝

# ----- Botones -------------------------------------------------------

def boton_primario(master, text: str, command=None, **kwargs) -> ctk.CTkButton:
    """Botón con relleno índigo sólido y texto blanco."""
    base: Dict[str, Any] = {
        'height':               CONTROL_HEIGHT,
        'corner_radius':        RADIUS['control'],
        'font':                 font('body'),
        'command':              command,
        'fg_color':             COLORS['accent'],
        'hover_color':          COLORS['accent_hover'],
        'text_color':           COLORS['white'],
        'text_color_disabled':  COLORS['muted_light'],
        'border_width':         0,
    }
    return ctk.CTkButton(master, text=text, **{**base, **kwargs})


def boton_secundario(master, text: str, command=None, **kwargs) -> ctk.CTkButton:
    """Botón blanco con borde sutil gris y texto oscuro."""
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


def boton_peligro(master, text: str, command=None, **kwargs) -> ctk.CTkButton:
    """Botón destructivo con fondo rojo suave (#FEE2E2), texto rojo, borde rojo."""
    base: Dict[str, Any] = {
        'height':               CONTROL_HEIGHT,
        'corner_radius':        RADIUS['control'],
        'font':                 font('body'),
        'command':              command,
        'fg_color':             COLORS['danger_soft'],
        'hover_color':          COLORS['danger_border'],
        'text_color':           COLORS['danger'],
        'text_color_disabled':  COLORS['muted_light'],
        'border_width':         1,
        'border_color':         COLORS['danger_border'],
    }
    return ctk.CTkButton(master, text=text, **{**base, **kwargs})


def boton_icono(master, text: str = '', command=None, **kwargs) -> ctk.CTkButton:
    """Botón cuadrado discreto pensado para íconos (ej. «⟳», «✕»).
    Fondo transparente hasta hover, bordes sutiles."""
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


# ----- Entradas de texto --------------------------------------------

def entrada_busqueda(
    master,
    placeholder: str = '🔍  Buscar…',
    width: Optional[int] = 260,
    **kwargs,
) -> ctk.CTkEntry:
    """Campo de búsqueda con placeholder e ícono de lupa integrado."""
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

    e = ctk.CTkEntry(master, placeholder_text=placeholder, **{**base, **kwargs})

    # Efecto de focus: borde índigo
    def _on_focus_in(_evt):
        try:
            e.configure(border_color=COLORS['accent'])
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


# ----- Combo / OptionMenu -------------------------------------------

def combo(
    master,
    values: list,
    variable=None,
    command=None,
    width: int = 150,
    **kwargs,
) -> ctk.CTkOptionMenu:
    """CTkOptionMenu estilizado con la paleta del sistema de diseño."""
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


# ----- Etiquetas -----------------------------------------------------

def etiqueta_titulo(master, text: str, **kwargs) -> ctk.CTkLabel:
    """Etiqueta de título principal (26 px bold, tinta oscura)."""
    base: Dict[str, Any] = {
        'font':       font('display'),
        'text_color': COLORS['ink'],
        'anchor':     'w',
    }
    return ctk.CTkLabel(master, text=text, **{**base, **kwargs})


def etiqueta_subtitulo(master, text: str, **kwargs) -> ctk.CTkLabel:
    """Etiqueta de subtítulo (13 px, gris secundario)."""
    base: Dict[str, Any] = {
        'font':       font('body'),
        'text_color': COLORS['muted'],
        'anchor':     'w',
    }
    return ctk.CTkLabel(master, text=text, **{**base, **kwargs})


# ----- Tarjeta -------------------------------------------------------

def tarjeta(master, **kwargs) -> ctk.CTkFrame:
    """CTkFrame blanco con borde sutil (#E5E7EB) y radio 8."""
    base: Dict[str, Any] = {
        'corner_radius': RADIUS['card'],
        'fg_color':      COLORS['surface'],
        'border_width':  1,
        'border_color':  COLORS['border'],
    }
    return ctk.CTkFrame(master, **{**base, **kwargs})


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  5. TREEVIEW  –  Tema clam, filas alternas, scrollbar delgada      ║
# ╚══════════════════════════════════════════════════════════════════════╝

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


def configurar_treeview(root=None) -> ttk.Style:
    """Aplica tema «clam» con encabezado gris claro en negrita,
    filas de 34 px, selección índigo suave, bordes sutiles y
    scrollbar delgada estilizada.  Devuelve el objeto ttk.Style.

    Tags configurados:
        'odd'   → fondo blanco
        'even'  → fondo #F9FAFB (zebra)
        'hover' → fondo índigo suave
        'active_badge'   → texto verde  «● Activo»
        'inactive_badge' → texto gris   «● Inactivo»
    """
    style = ttk.Style(root)
    try:
        style.theme_use('clam')
    except Exception:
        pass

    dpi_scale = get_dpi_scale(root)
    row_height = int(round(34 * dpi_scale))
    pad_x = int(round(14 * dpi_scale))
    pad_y = int(round(8 * dpi_scale))

    # Eliminar bordes del treearea
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
        foreground=[('selected', COLORS['accent'])],
    )

    # Encabezado gris claro en negrita
    style.configure(
        'Pea.Treeview.Heading',
        background='#F3F4F6',
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

    # Scrollbar vertical delgada y minimalista
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

    style.map(
        'Pea.Vertical.TScrollbar',
        background=[('active', COLORS['muted'])],
    )

    return style


def apply_treeview_tags(tree: ttk.Treeview):
    """Configura las etiquetas zebra, hover y badges de estado."""
    tree.tag_configure('odd',  background=COLORS['surface'],     foreground=COLORS['ink'])
    tree.tag_configure('even', background=COLORS['surface_alt'], foreground=COLORS['ink'])
    tree.tag_configure('hover', background=COLORS['accent_soft'], foreground=COLORS['ink'])
    # Badges de estado (ver sección 7)
    tree.tag_configure('active_badge',   background=COLORS['badge_active_bg'],
                       foreground=COLORS['badge_active_text'])
    tree.tag_configure('inactive_badge', background=COLORS['badge_inactive_bg'],
                       foreground=COLORS['badge_inactive_text'])


def insertar_fila(
    tree: ttk.Treeview,
    values: tuple,
    index: int,
    parent: str = '',
    iid: Optional[str] = None,
) -> str:
    """Inserta una fila en el Treeview con tag alternado (zebra).

    Args:
        tree:   El widget Treeview.
        values: Tupla de valores para las columnas.
        index:  Índice secuencial de la fila (0-based) para calcular par/impar.
        parent: Nodo padre ('' = raíz).
        iid:    Identificador interno opcional.

    Returns:
        El iid asignado a la fila insertada.
    """
    tag = 'even' if index % 2 == 0 else 'odd'
    kwargs: Dict[str, Any] = {'parent': parent, 'index': 'end', 'values': values, 'tags': (tag,)}
    if iid is not None:
        kwargs['iid'] = iid
    return tree.insert(**kwargs)


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  6. ESTADOS VACÍOS                                                 ║
# ╚══════════════════════════════════════════════════════════════════════╝

def estado_vacio(
    parent,
    icono: str = '📭',
    titulo: str = 'Sin registros',
    mensaje: str = 'Aún no hay datos para mostrar.',
    texto_boton: Optional[str] = None,
    comando: Optional[Callable] = None,
) -> ctk.CTkFrame:
    """Muestra un mensaje centrado con ícono y acción opcional.

    Retorna el frame contenedor para poder destruirlo cuando haya datos.
    """
    frame = ctk.CTkFrame(parent, fg_color='transparent')
    frame.pack(fill='both', expand=True)

    # Contenedor interno centrado
    inner = ctk.CTkFrame(frame, fg_color='transparent')
    inner.place(relx=0.5, rely=0.45, anchor='center')

    ctk.CTkLabel(
        inner,
        text=icono,
        font=ctk.CTkFont(family=FONT_FAMILY, size=48),
        text_color=COLORS['muted_light'],
    ).pack(pady=(0, SPACING['sm']))

    ctk.CTkLabel(
        inner,
        text=titulo,
        font=font('heading'),
        text_color=COLORS['ink'],
    ).pack(pady=(0, SPACING['xs']))

    ctk.CTkLabel(
        inner,
        text=mensaje,
        font=font('body'),
        text_color=COLORS['muted'],
        wraplength=320,
    ).pack(pady=(0, SPACING['md']))

    if texto_boton and comando:
        boton_primario(inner, text=texto_boton, command=comando).pack()

    return frame


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  7. BADGES DE ESTADO                                               ║
# ╚══════════════════════════════════════════════════════════════════════╝

BADGE_ACTIVO   = '● Activo'
BADGE_INACTIVO = '● Inactivo'


def badge_estado(activo: bool) -> str:
    """Retorna el texto de badge según el estado booleano."""
    return BADGE_ACTIVO if activo else BADGE_INACTIVO


def badge_tag(activo: bool) -> str:
    """Retorna el nombre del tag de Treeview para el badge."""
    return 'active_badge' if activo else 'inactive_badge'


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  COMPATIBILIDAD  –  Funciones y alias del API anterior             ║
# ╚══════════════════════════════════════════════════════════════════════╝

def button(master, text: str, variant: str = 'secondary', command=None, **kwargs) -> ctk.CTkButton:
    """Crea un CTkButton con sistema estricto de jerarquía visual.

    Jerarquías disponibles:
    - 'primary': Relleno en color acento (índigo), texto blanco.
    - 'secondary': Fondo blanco con borde sutil y texto oscuro.
    - 'danger': Destructivo en rojo suave (fondo tenue, texto y borde rojo).
    - 'tertiary' / 'ghost': Fondo blanco o transparente con ícono/borde sutil.
    """
    base_kwargs: Dict[str, Any] = {
        'height':        CONTROL_HEIGHT,
        'corner_radius': RADIUS['control'],
        'font':          font('body'),
        'command':       command,
    }

    if variant == 'primary':
        variant_kwargs = {
            'fg_color':            COLORS['accent'],
            'hover_color':         COLORS['accent_hover'],
            'text_color':          COLORS['white'],
            'text_color_disabled': COLORS['muted_light'],
            'border_width':        0,
        }
    elif variant == 'secondary':
        variant_kwargs = {
            'fg_color':            COLORS['surface'],
            'hover_color':         COLORS['surface_alt'],
            'text_color':          COLORS['ink'],
            'text_color_disabled': COLORS['muted_light'],
            'border_width':        1,
            'border_color':        COLORS['border'],
        }
    elif variant == 'danger':
        variant_kwargs = {
            'fg_color':            COLORS['danger_soft'],
            'hover_color':         COLORS['danger_border'],
            'text_color':          COLORS['danger'],
            'text_color_disabled': COLORS['muted_light'],
            'border_width':        1,
            'border_color':        COLORS['danger_border'],
        }
    elif variant in ('tertiary', 'ghost'):
        variant_kwargs = {
            'fg_color':            COLORS['surface'],
            'hover_color':         COLORS['surface_alt'],
            'text_color':          COLORS['ink_soft'],
            'text_color_disabled': COLORS['muted_light'],
            'border_width':        1,
            'border_color':        COLORS['border'],
        }
    else:
        variant_kwargs = {
            'fg_color':            COLORS['surface'],
            'hover_color':         COLORS['surface_alt'],
            'text_color':          COLORS['ink'],
            'text_color_disabled': COLORS['muted_light'],
            'border_width':        1,
            'border_color':        COLORS['border'],
        }

    merged = {**base_kwargs, **variant_kwargs, **kwargs}
    return ctk.CTkButton(master, text=text, **merged)


def entry(master, placeholder_text: str = '', width: Optional[int] = None, **kwargs) -> ctk.CTkEntry:
    """Crea un CTkEntry con bordes sutiles y dimensiones unificadas."""
    base_kwargs: Dict[str, Any] = {
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
        base_kwargs['width'] = width

    return ctk.CTkEntry(master, placeholder_text=placeholder_text, **{**base_kwargs, **kwargs})


def option_menu(master, values, variable=None, command=None, width: int = 150, **kwargs) -> ctk.CTkOptionMenu:
    """Crea un CTkOptionMenu estilizado con altura unificada y estética limpia."""
    return combo(master, values=values, variable=variable, command=command, width=width, **kwargs)


def card(master, **kwargs) -> ctk.CTkFrame:
    """Crea un CTkFrame contenedor con estilo de tarjeta limpia."""
    return tarjeta(master, **kwargs)


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
    """Alias de compatibilidad → delega a configurar_treeview."""
    configurar_treeview(root)


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  MATPLOTLIB  –  Estilos unificados                                 ║
# ╚══════════════════════════════════════════════════════════════════════╝

def apply_matplotlib_style():
    """Configura rcParams globales para unificar el aspecto de Matplotlib."""
    try:
        import matplotlib as mpl
        mpl.rcParams['font.family']       = 'sans-serif'
        mpl.rcParams['font.sans-serif']   = [FONT_FAMILY, 'DejaVu Sans', 'Arial']
        mpl.rcParams['figure.facecolor']  = COLORS['surface']
        mpl.rcParams['axes.facecolor']    = COLORS['surface']
        mpl.rcParams['text.color']        = COLORS['ink']
        mpl.rcParams['axes.labelcolor']   = COLORS['ink_soft']
        mpl.rcParams['xtick.color']       = COLORS['muted']
        mpl.rcParams['ytick.color']       = COLORS['muted']
        mpl.rcParams['grid.color']        = COLORS['border']
        mpl.rcParams['grid.linestyle']    = '-'
        mpl.rcParams['grid.linewidth']    = 0.8
        mpl.rcParams['grid.alpha']        = 0.6
        mpl.rcParams['axes.grid']         = True
        mpl.rcParams['axes.grid.axis']    = 'y'
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


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  SETUP GENERAL                                                     ║
# ╚══════════════════════════════════════════════════════════════════════╝

def setup_app(root=None):
    """Inicializa el tema visual, estilos de ttk, matplotlib y fondo de ventana."""
    ctk.set_appearance_mode('light')
    ctk.set_default_color_theme('blue')
    if root is not None:
        try:
            root.configure(fg_color=COLORS['bg'])
        except Exception:
            pass
        configurar_treeview(root)
    apply_matplotlib_style()


def apply_theme(root=None):
    """Alias de compatibilidad para código existente."""
    setup_app(root)


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  EJEMPLO MÍNIMO DE USO                                             ║
# ╚══════════════════════════════════════════════════════════════════════╝

if __name__ == '__main__':
    # Demo rápido de todas las funciones fábrica
    app = ctk.CTk()
    app.geometry('860x700')
    app.title('PEA-i · Design System Demo')
    setup_app(app)

    # — Título y subtítulo —
    etiqueta_titulo(app, text='Sistema de Diseño PEA-i').pack(
        anchor='w', padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['xs']),
    )
    etiqueta_subtitulo(app, text='Demostración de cada componente del sistema').pack(
        anchor='w', padx=SPACING['lg'], pady=(0, SPACING['md']),
    )

    # — Tarjeta con botones —
    t = tarjeta(app)
    t.pack(fill='x', padx=SPACING['lg'], pady=SPACING['sm'])

    fila_btns = ctk.CTkFrame(t, fg_color='transparent')
    fila_btns.pack(padx=SPACING['md'], pady=SPACING['md'])

    boton_primario(fila_btns, text='Primario').pack(side='left', padx=4)
    boton_secundario(fila_btns, text='Secundario').pack(side='left', padx=4)
    boton_peligro(fila_btns, text='Peligro').pack(side='left', padx=4)
    boton_icono(fila_btns, text='⟳').pack(side='left', padx=4)

    # — Entrada de búsqueda —
    entrada_busqueda(app).pack(padx=SPACING['lg'], pady=SPACING['sm'], anchor='w')

    # — Combo —
    combo(app, values=['Artículo', 'Libro', 'Capítulo', 'Software']).pack(
        padx=SPACING['lg'], pady=SPACING['sm'], anchor='w',
    )

    # — Treeview con filas alternas y badges —
    tree_frame = tarjeta(app)
    tree_frame.pack(fill='both', expand=True, padx=SPACING['lg'], pady=SPACING['sm'])

    cols = ('nombre', 'categoría', 'estado')
    tree = ttk.Treeview(tree_frame, columns=cols, show='headings', style='Pea.Treeview')
    for col in cols:
        tree.heading(col, text=col.capitalize())
        tree.column(col, width=200)
    tree.pack(fill='both', expand=True, padx=1, pady=1)

    apply_treeview_tags(tree)

    datos_demo = [
        ('Grupo Alpha', 'A1', True),
        ('Grupo Beta', 'B', False),
        ('Grupo Gamma', 'A', True),
        ('Grupo Delta', 'C', False),
    ]
    for i, (nombre, cat, activo) in enumerate(datos_demo):
        iid = insertar_fila(tree, values=(nombre, cat, badge_estado(activo)), index=i)
        # Aplicar tag de badge sobre la misma fila
        tags_actuales = tree.item(iid, 'tags')
        tree.item(iid, tags=(*tags_actuales, badge_tag(activo)))

    # — Estado vacío (en una tarjeta separada para demostración) —
    t_vacia = tarjeta(app)
    t_vacia.pack(fill='x', padx=SPACING['lg'], pady=SPACING['sm'])
    estado_vacio(
        t_vacia,
        icono='📭',
        titulo='Sin productos',
        mensaje='Descargue datos del SCIENTI para comenzar.',
        texto_boton='Descargar ahora',
        comando=lambda: print('¡Descargando!'),
    )

    app.mainloop()