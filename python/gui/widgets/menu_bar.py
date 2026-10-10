# -*- coding: utf-8 -*-
"""MenuBarModerno: Barra de menú moderna integrada con soporte de atajos y temas."""

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
    """Barra de menú horizontal integrada para la ventana principal.

    Características:
    - Altura estándar ~40 px con borde inferior sutil de 1 px.
    - Botones planos con hover suave y estado activo índigo.
    - Menús desplegables tipo tarjeta flotante con esquinas redondeadas.
    - Íconos a la izquierda, etiquetas y atajos alineados a la derecha.
    - Separadores y soporte para opciones deshabilitadas.
    - Cierre automático al hacer clic fuera o presionar Escape.
    - Navegación fluida con teclado (flechas y Enter).
    """

    def __init__(self, master, app=None, **kwargs):
        base_kwargs = {
            'height': 40,
            'fg_color': COLORS['surface'],
            'corner_radius': 0,
        }
        merged_kwargs = {**base_kwargs, **kwargs}
        super().__init__(master, **merged_kwargs)

        self.app = app or master
        self.menus_config: Dict[str, List[Dict[str, Any]]] = {}
        self.menu_buttons: Dict[str, ctk.CTkButton] = {}
        self.active_menu_name: Optional[str] = None
        self.active_popup: Optional[ctk.CTkToplevel] = None
        self.menu_order: List[str] = []

        # Estado de navegación con teclado
        self._highlighted_item_idx: int = -1
        self._current_items_widgets: List[Dict[str, Any]] = []

        # Barra contenedora de botones de menú
        self.bar_container = ctk.CTkFrame(self, fg_color='transparent', height=39)
        self.bar_container.pack(fill='both', expand=True, padx=SPACING['sm'], pady=(0, 1))

        # Borde inferior sutil de 1 px
        self.bottom_border = ctk.CTkFrame(
            self,
            height=1,
            fg_color=COLORS['border'],
            corner_radius=0,
        )
        self.bottom_border.pack(fill='x', side='bottom')

        # Contenedor a la izquierda para los menús desplegables
        self.buttons_frame = ctk.CTkFrame(self.bar_container, fg_color='transparent')
        self.buttons_frame.pack(side='left', fill='y', pady=3)

        # Enlace de clic global en la ventana para cerrar menús desplegables al hacer clic fuera
        self._bind_root_click_dismiss()

    def _bind_root_click_dismiss(self):
        """Monitorea clics en la ventana principal para cerrar desplegables si se hace clic fuera."""
        toplevel = self.winfo_toplevel()
        toplevel.bind('<Button-1>', self._on_root_click, add='+')
        toplevel.bind('<Escape>', lambda e: self.close_active_menu(), add='+')
        toplevel.bind('<Configure>', lambda e: self.close_active_menu(), add='+')

    def _on_root_click(self, event):
        """Cierra el menú si el usuario hace clic fuera del menú activo y sus botones."""
        if not self.active_popup or not self.active_popup.winfo_exists():
            return

        # Verifica si el clic ocurrió dentro del botón del menú activo
        if self.active_menu_name and self.active_menu_name in self.menu_buttons:
            btn = self.menu_buttons[self.active_menu_name]
            bx, by = btn.winfo_rootx(), btn.winfo_rooty()
            bw, bh = btn.winfo_width(), btn.winfo_height()
            if bx <= event.x_root <= bx + bw and by <= event.y_root <= by + bh:
                return

        # Verifica si el clic ocurrió dentro del popup
        try:
            px, py = self.active_popup.winfo_rootx(), self.active_popup.winfo_rooty()
            pw, ph = self.active_popup.winfo_width(), self.active_popup.winfo_height()
            if px <= event.x_root <= px + pw and py <= event.y_root <= py + ph:
                return
        except Exception:
            pass

        self.close_active_menu()

    def add_menu(self, title: str, items: List[Dict[str, Any]]):
        """Registra un menú superior con su lista de elementos configurados."""
        self.menus_config[title] = items
        self.menu_order.append(title)

        # Botón de menú superior estilizado
        btn = ctk.CTkButton(
            self.buttons_frame,
            text=title,
            width=68,
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
        """Si ya hay un menú abierto, deslizar el mouse a otro abre automáticamente ese menú."""
        if self.active_menu_name is not None and self.active_menu_name != title:
            self._open_menu(title)

    def _toggle_menu(self, title: str):
        """Abre o cierra el menú correspondiente al presionar su botón."""
        if self.active_menu_name == title:
            self.close_active_menu()
        else:
            self._open_menu(title)

    def _open_menu(self, title: str):
        """Construye y despliega el popup flotante para el menú seleccionado."""
        self.close_active_menu()

        if title not in self.menus_config:
            return

        self.active_menu_name = title
        btn = self.menu_buttons[title]

        # Estilo de botón activo mientras el menú está desplegado
        btn.configure(
            fg_color=COLORS['accent_soft'],
            text_color=COLORS['accent'],
            hover_color=COLORS['accent_soft'],
        )

        # Posicionamiento calculado debajo del botón
        self.update_idletasks()
        btn.update_idletasks()
        rx = btn.winfo_rootx()
        ry = btn.winfo_rooty() + btn.winfo_height() + 2

        # Ventana emergente toplevel sin bordes de ventana del SO
        popup = ctk.CTkToplevel(self)
        popup.overrideredirect(True)
        popup.attributes('-topmost', True)
        popup.configure(fg_color=COLORS['surface'])
        self.active_popup = popup

        # Tarjeta contenedora con borde y esquinas redondeadas (radio 8)
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

        # Construcción de filas del menú
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

            row_frame = ctk.CTkFrame(
                content_frame,
                height=34,
                corner_radius=6,
                fg_color='transparent',
            )
            row_frame.pack(fill='x', pady=1)

            # Elementos de la fila
            icon_lbl = ctk.CTkLabel(
                row_frame,
                text=icon_char,
                width=24,
                font=('Segoe UI Emoji', 13),
                text_color=COLORS['ink'] if is_enabled else COLORS['muted_light'],
                anchor='center',
            )
            icon_lbl.pack(side='left', padx=(6, 4))

            text_lbl = ctk.CTkLabel(
                row_frame,
                text=label,
                font=font('body'),
                text_color=COLORS['ink'] if is_enabled else COLORS['muted_light'],
                anchor='w',
            )
            text_lbl.pack(side='left', padx=(0, 24), fill='x', expand=True)

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

            item_record = {
                'frame': row_frame,
                'labels': [icon_lbl, text_lbl] + ([sc_lbl] if sc_lbl else []),
                'command': command,
                'enabled': is_enabled,
            }
            self._current_items_widgets.append(item_record)

            if is_enabled:
                # Eventos hover y click
                idx = len(self._current_items_widgets) - 1
                for widget in (row_frame, icon_lbl, text_lbl) + ((sc_lbl,) if sc_lbl else ()):
                    widget.bind('<Enter>', lambda e, i=idx: self._highlight_item(i))
                    widget.bind('<Leave>', lambda e, i=idx: self._unhighlight_item(i))
                    widget.bind('<Button-1>', lambda e, cmd=command: self._execute_and_close(cmd))

        # Ajuste de tamaño y posición exacta
        popup.update_idletasks()
        pw = max(220, popup.winfo_reqwidth())
        ph = popup.winfo_reqheight()
        popup.geometry(f"{pw}x{ph}+{rx}+{ry}")

        # Enlace de teclado para el popup
        popup.bind('<Escape>', lambda e: self.close_active_menu())
        popup.bind('<Down>', lambda e: self._navigate_arrow(1))
        popup.bind('<Up>', lambda e: self._navigate_arrow(-1))
        popup.bind('<Return>', lambda e: self._trigger_highlighted())
        popup.bind('<Left>', lambda e: self._switch_menu_arrow(-1))
        popup.bind('<Right>', lambda e: self._switch_menu_arrow(1))
        popup.focus_force()

    def _highlight_item(self, idx: int):
        """Resalta visualmente un elemento del menú."""
        if 0 <= idx < len(self._current_items_widgets):
            item = self._current_items_widgets[idx]
            if item['enabled']:
                self._unhighlight_item(self._highlighted_item_idx)
                item['frame'].configure(fg_color=COLORS['surface_alt'])
                self._highlighted_item_idx = idx

    def _unhighlight_item(self, idx: int):
        """Restaura el fondo normal del elemento."""
        if 0 <= idx < len(self._current_items_widgets):
            item = self._current_items_widgets[idx]
            item['frame'].configure(fg_color='transparent')
            if self._highlighted_item_idx == idx:
                self._highlighted_item_idx = -1

    def _navigate_arrow(self, step: int):
        """Mueve el resaltado de teclado hacia arriba o abajo en elementos habilitados."""
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
        """Ejecuta el elemento actualmente seleccionado con teclado."""
        if 0 <= self._highlighted_item_idx < len(self._current_items_widgets):
            item = self._current_items_widgets[self._highlighted_item_idx]
            if item['enabled'] and item['command']:
                self._execute_and_close(item['command'])

    def _switch_menu_arrow(self, step: int):
        """Cambia al menú anterior o siguiente con las flechas Izquierda/Derecha."""
        if not self.active_menu_name or not self.menu_order:
            return
        idx = self.menu_order.index(self.active_menu_name)
        new_idx = (idx + step) % len(self.menu_order)
        self._open_menu(self.menu_order[new_idx])

    def _execute_and_close(self, command: Optional[Callable]):
        """Cierra el menú desplegado y dispara el callback de la acción."""
        self.close_active_menu()
        if command:
            self.after(10, command)

    def close_active_menu(self):
        """Cierra cualquier menú desplegado y restaura el estado visual de los botones."""
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
