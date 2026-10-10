# -*- coding: utf-8 -*-
"""MenuBarModerno: Barra de menú moderna integrada con soporte de atajos y diseño CustomTkinter."""

from typing import List, Dict, Any, Optional, Callable
import tkinter as tk
import customtkinter as ctk

from gui.styles import (
    COLORS,
    RADIUS,
    SPACING,
    font,
)


class MenuBarModerno(ctk.CTkFrame):
    """Barra de menú horizontal moderna e integrada para ventanas CustomTkinter.

    Características principales:
    1. Barra superior blanca, altura ~40 px, con borde inferior sutil de 1 px.
    2. Botones planos con hover gris claro y estado activo con fondo índigo suave.
    3. Paneles desplegables tipo tarjeta flotante con esquinas redondeadas (radio 8),
       borde de elevación sutil, padding interno de 6 px y filas interactivas de 34 px.
    4. Cada opción incluye ícono a la izquierda, etiqueta central y atajo alineado a la derecha.
    5. Separadores finos (1 px) entre grupos de opciones.
    6. Opciones deshabilitadas con estilo atenuado en gris y sin interacción.
    7. Cierre automático al hacer clic fuera o presionar Esc; navegación fluida con teclado (flechas y Enter).
    8. Vinculación automática y global de atajos de teclado en la ventana principal.
    """

    def __init__(self, master, app=None, height: int = 40, **kwargs):
        base_kwargs = {
            'height': height,
            'fg_color': COLORS['surface'],
            'corner_radius': 0,
        }
        merged_kwargs = {**base_kwargs, **kwargs}
        super().__init__(master, **merged_kwargs)

        self.app = app or master
        self.menus_config: Dict[str, List[Dict[str, Any]]] = {}
        self.menu_buttons: Dict[str, ctk.CTkButton] = {}
        self.menu_order: List[str] = []

        self.active_menu_name: Optional[str] = None
        self.active_popup: Optional[ctk.CTkToplevel] = None

        # Estado de navegación con teclado
        self._highlighted_item_idx: int = -1
        self._current_items_widgets: List[Dict[str, Any]] = []

        # Contenedor horizontal interno
        self.bar_container = ctk.CTkFrame(self, fg_color='transparent', height=height - 1)
        self.bar_container.pack(fill='both', expand=True, padx=SPACING['sm'], pady=(0, 1))

        # Borde inferior sutil de 1 px (#E2E8F0)
        self.bottom_border = ctk.CTkFrame(
            self,
            height=1,
            fg_color=COLORS['border'],
            corner_radius=0,
        )
        self.bottom_border.pack(fill='x', side='bottom')

        # Contenedor a la izquierda para los botones de menús
        self.buttons_frame = ctk.CTkFrame(self.bar_container, fg_color='transparent')
        self.buttons_frame.pack(side='left', fill='y', pady=3)

        # Enlace de eventos globales para cierre con clic fuera o redimensionamiento
        self._bind_root_events()

    def _bind_root_events(self):
        """Registra listeners en la ventana principal para cerrar desplegables."""
        toplevel = self.winfo_toplevel()
        toplevel.bind('<Button-1>', self._on_root_click, add='+')
        toplevel.bind('<Escape>', lambda e: self.close_active_menu(), add='+')
        toplevel.bind('<Configure>', lambda e: self.close_active_menu(), add='+')

    def _parse_shortcut(self, sc: str) -> List[str]:
        """Convierte una cadena de atajo (ej. 'Ctrl+O', 'Ctrl+Shift+C', 'F5') en secuencias Tkinter."""
        if not sc:
            return []
        parts = [p.strip() for p in sc.split('+')]
        has_ctrl = any(p.lower() in ('ctrl', 'control') for p in parts)
        has_shift = any(p.lower() == 'shift' for p in parts)
        has_alt = any(p.lower() == 'alt' for p in parts)

        keys = [p for p in parts if p.lower() not in ('ctrl', 'control', 'shift', 'alt')]
        if not keys:
            return []
        key = keys[-1]

        mods = []
        if has_ctrl:
            mods.append("Control")
        if has_shift:
            mods.append("Shift")
        if has_alt:
            mods.append("Alt")

        prefix = f"{'-'.join(mods)}-" if mods else ""

        if key.lower() in ('del', 'delete'):
            return [f"<{prefix}Delete>"]
        elif key.upper().startswith('F') and key[1:].isdigit():
            return [f"<{prefix}{key.upper()}>"]
        else:
            return [f"<{prefix}{key.lower()}>", f"<{prefix}{key.upper()}>"]

    def _bind_global_shortcut(self, shortcut: str, command: Callable, enabled_check: Any):
        """Registra un atajo de teclado global en la ventana toplevel."""
        if not shortcut or not command:
            return

        toplevel = self.winfo_toplevel()
        sequences = self._parse_shortcut(shortcut)

        def _handler(event, cmd=command, check=enabled_check):
            is_enabled = check() if callable(check) else bool(check)
            if is_enabled and cmd:
                self.close_active_menu()
                self.after(10, cmd)
            return "break"

        for seq in sequences:
            try:
                toplevel.bind_all(seq, _handler, add='+')
            except Exception:
                pass

    def add_menu(self, title: str, items: List[Dict[str, Any]]):
        """Registra un menú superior con sus opciones y vincula sus atajos globales.

        Args:
            title: Nombre del menú (ej. "Archivo", "Datos", "Ayuda").
            items: Lista de diccionarios que definen las opciones del menú:
                - label: Texto de la opción.
                - icon: Ícono o emoji decorativo.
                - shortcut: Texto del atajo (ej. "Ctrl+O").
                - command: Función callback a ejecutar.
                - enabled: Booleano o función callable que retorna bool indicando disponibilidad.
                - separator: True si representa un divisor visual.
        """
        self.menus_config[title] = items
        self.menu_order.append(title)

        # Registro de atajos globales configurados en este menú
        for item in items:
            if not item.get('separator') and item.get('shortcut') and item.get('command'):
                self._bind_global_shortcut(
                    item['shortcut'],
                    item['command'],
                    item.get('enabled', True),
                )

        # Botón superior plano para el menú
        btn = ctk.CTkButton(
            self.buttons_frame,
            text=title,
            width=70,
            height=30,
            corner_radius=6,
            fg_color='transparent',
            hover_color=COLORS['surface_alt'],
            text_color=COLORS['ink'],
            font=font('body'),
            command=lambda t=title: self._toggle_menu(t),
        )
        btn.pack(side='left', padx=(0, 2), pady=2)
        btn.bind('<Enter>', lambda e, t=title: self._on_button_hover_switch(t))
        self.menu_buttons[title] = btn

    def _on_button_hover_switch(self, title: str):
        """Al deslizar el cursor sobre otro botón mientras un menú está abierto, cambia al nuevo menú."""
        if self.active_menu_name is not None and self.active_menu_name != title:
            self._open_menu(title)

    def _toggle_menu(self, title: str):
        """Abre o cierra el menú al hacer clic en su botón superior."""
        if self.active_menu_name == title:
            self.close_active_menu()
        else:
            self._open_menu(title)

    def _open_menu(self, title: str):
        """Construye y despliega el popup flotante con diseño moderno para el menú solicitado."""
        self.close_active_menu()

        if title not in self.menus_config:
            return

        self.active_menu_name = title
        btn = self.menu_buttons[title]

        # Estado visual activo del botón: fondo índigo suave y texto índigo
        btn.configure(
            fg_color=COLORS['accent_soft'],
            text_color=COLORS['accent'],
            hover_color=COLORS['accent_soft'],
        )

        # Posicionamiento calculado exactamente debajo del botón
        self.update_idletasks()
        btn.update_idletasks()
        rx = btn.winfo_rootx()
        ry = btn.winfo_rooty() + btn.winfo_height() + 2

        # Ventana emergente toplevel sin bordes nativos del sistema operativo
        popup = ctk.CTkToplevel(self)
        popup.overrideredirect(True)
        popup.attributes('-topmost', True)
        popup.configure(fg_color=COLORS['surface'])
        self.active_popup = popup

        # Tarjeta contenedora con borde sutil y esquinas redondeadas (radio 8)
        card_frame = ctk.CTkFrame(
            popup,
            corner_radius=RADIUS['control'],
            fg_color=COLORS['surface'],
            border_width=1,
            border_color=COLORS['border'],
        )
        card_frame.pack(fill='both', expand=True, padx=0, pady=0)

        # Contenedor interno con padding de 6 px
        content_frame = ctk.CTkFrame(card_frame, fg_color='transparent')
        content_frame.pack(fill='both', expand=True, padx=6, pady=6)

        self._current_items_widgets.clear()
        self._highlighted_item_idx = -1

        # Generación de elementos de menú
        for item in self.menus_config[title]:
            if item.get('separator'):
                sep = ctk.CTkFrame(
                    content_frame,
                    height=1,
                    fg_color=COLORS['border'],
                    corner_radius=0,
                )
                sep.pack(fill='x', padx=4, pady=4)
                continue

            label = item.get('label', '')
            icon_char = item.get('icon', '  ')
            shortcut = item.get('shortcut', '')
            command = item.get('command')
            enabled_check = item.get('enabled', True)
            is_enabled = enabled_check() if callable(enabled_check) else bool(enabled_check)

            # Fila de 34 px de alto con esquinas redondeadas
            row_frame = ctk.CTkFrame(
                content_frame,
                height=34,
                corner_radius=6,
                fg_color='transparent',
            )
            row_frame.pack(fill='x', pady=1)

            # Ícono a la izquierda
            icon_lbl = ctk.CTkLabel(
                row_frame,
                text=icon_char,
                width=24,
                font=('Segoe UI Emoji', 12),
                text_color=COLORS['ink'] if is_enabled else COLORS['muted_light'],
                anchor='center',
            )
            icon_lbl.pack(side='left', padx=(6, 4))

            # Texto de la opción
            text_lbl = ctk.CTkLabel(
                row_frame,
                text=label,
                font=font('body'),
                text_color=COLORS['ink'] if is_enabled else COLORS['muted_light'],
                anchor='w',
            )
            text_lbl.pack(side='left', padx=(0, 24), fill='x', expand=True)

            # Atajo de teclado alineado a la derecha en gris tenue
            if shortcut:
                sc_lbl = ctk.CTkLabel(
                    row_frame,
                    text=shortcut,
                    font=font('small'),
                    text_color=COLORS['muted'] if is_enabled else COLORS['muted_light'],
                    anchor='e',
                )
                sc_lbl.pack(side='right', padx=(0, 8))
            else:
                sc_lbl = None

            widgets_in_row = (row_frame, icon_lbl, text_lbl) + ((sc_lbl,) if sc_lbl else ())
            item_record = {
                'frame': row_frame,
                'widgets': widgets_in_row,
                'command': command,
                'enabled': is_enabled,
            }
            self._current_items_widgets.append(item_record)

            if is_enabled:
                idx = len(self._current_items_widgets) - 1
                for w in widgets_in_row:
                    w.bind('<Enter>', lambda e, i=idx: self._highlight_item(i))
                    w.bind('<Leave>', lambda e, i=idx: self._unhighlight_item(i))
                    w.bind('<Button-1>', lambda e, cmd=command: self._execute_and_close(cmd))

        # Ajuste de dimensiones y posición exacta en pantalla
        popup.update_idletasks()
        pw = max(230, popup.winfo_reqwidth())
        ph = popup.winfo_reqheight()
        popup.geometry(f"{pw}x{ph}+{rx}+{ry}")

        # Atajos y navegación con teclado en el popup
        popup.bind('<Escape>', lambda e: self.close_active_menu())
        popup.bind('<Down>', lambda e: self._navigate_arrow(1))
        popup.bind('<Up>', lambda e: self._navigate_arrow(-1))
        popup.bind('<Return>', lambda e: self._trigger_highlighted())
        popup.bind('<Left>', lambda e: self._switch_menu_arrow(-1))
        popup.bind('<Right>', lambda e: self._switch_menu_arrow(1))
        popup.focus_force()

    def _highlight_item(self, idx: int):
        """Resalta visualmente una fila habilitada con hover gris suave."""
        if 0 <= idx < len(self._current_items_widgets):
            item = self._current_items_widgets[idx]
            if item['enabled']:
                self._unhighlight_item(self._highlighted_item_idx)
                item['frame'].configure(fg_color=COLORS['surface_alt'])
                self._highlighted_item_idx = idx

    def _unhighlight_item(self, idx: int):
        """Restaura el fondo transparente de una fila del menú."""
        if 0 <= idx < len(self._current_items_widgets):
            item = self._current_items_widgets[idx]
            item['frame'].configure(fg_color='transparent')
            if self._highlighted_item_idx == idx:
                self._highlighted_item_idx = -1

    def _navigate_arrow(self, step: int):
        """Navega verticalmente entre opciones habilitadas con las flechas Arriba/Abajo."""
        total = len(self._current_items_widgets)
        if total == 0:
            return

        next_idx = self._highlighted_item_idx
        for _ in range(total):
            next_idx = (next_idx + step) % total
            if self._current_items_widgets[next_idx]['enabled']:
                self._highlight_item(next_idx)
                break

    def _trigger_highlighted(self):
        """Ejecuta la opción seleccionada actualmente mediante la tecla Enter."""
        if 0 <= self._highlighted_item_idx < len(self._current_items_widgets):
            item = self._current_items_widgets[self._highlighted_item_idx]
            if item['enabled'] and item['command']:
                self._execute_and_close(item['command'])

    def _switch_menu_arrow(self, step: int):
        """Cambia al menú anterior o siguiente con las teclas Flecha Izquierda / Derecha."""
        if not self.active_menu_name or not self.menu_order:
            return
        try:
            curr_idx = self.menu_order.index(self.active_menu_name)
            new_idx = (curr_idx + step) % len(self.menu_order)
            self._open_menu(self.menu_order[new_idx])
        except ValueError:
            pass

    def _execute_and_close(self, command: Optional[Callable]):
        """Cierra el menú desplegado y dispara el callback asociado de forma asíncrona sutil."""
        self.close_active_menu()
        if command:
            self.after(10, command)

    def close_active_menu(self):
        """Cierra cualquier desplegable abierto y restaura el estado visual del botón superior."""
        if self.active_menu_name and self.active_menu_name in self.menu_buttons:
            self.menu_buttons[self.active_menu_name].configure(
                fg_color='transparent',
                text_color=COLORS['ink'],
                hover_color=COLORS['surface_alt'],
            )

        if self.active_popup and self.active_popup.winfo_exists():
            try:
                self.active_popup.destroy()
            except Exception:
                pass

        self.active_menu_name = None
        self.active_popup = None
        self._highlighted_item_idx = -1
        self._current_items_widgets.clear()

    def _on_root_click(self, event):
        """Detecta clics fuera del menú activo y del botón para cerrar el desplegable."""
        if not self.active_popup or not self.active_popup.winfo_exists():
            return

        # Si el clic ocurrió sobre el botón activo, permite que su propio evento controle la apertura/cierre
        if self.active_menu_name and self.active_menu_name in self.menu_buttons:
            btn = self.menu_buttons[self.active_menu_name]
            try:
                bx, by = btn.winfo_rootx(), btn.winfo_rooty()
                bw, bh = btn.winfo_width(), btn.winfo_height()
                if bx <= event.x_root <= bx + bw and by <= event.y_root <= by + bh:
                    return
            except Exception:
                pass

        # Si el clic ocurrió fuera, cerramos el menú
        self.close_active_menu()
