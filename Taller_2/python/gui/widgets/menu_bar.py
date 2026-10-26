# -*- coding: utf-8 -*-
"""MenuBarModerno: Barra de menú moderna con desplegables integrados en la ventana raíz."""

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
    """Barra de menú superior integrada.
    
    Los desplegables son CTkFrame hijos de la ventana principal posicionados con
    place() y lift() justo debajo de cada botón, evitando ventanas CTkToplevel flotantes.
    """

    def __init__(self, master, app=None, height: int = 40, **kwargs):
        base_kwargs = {
            "height": height,
            "fg_color": COLORS["surface"],
            "corner_radius": 0,
        }
        merged_kwargs = {**base_kwargs, **kwargs}
        super().__init__(master, **merged_kwargs)

        self.app = app or master
        self._top_window = self.winfo_toplevel()

        self.menus_config: Dict[str, List[Dict[str, Any]]] = {}
        self.menu_buttons: Dict[str, ctk.CTkButton] = {}
        self.menu_order: List[str] = []

        self.active_menu_name: Optional[str] = None
        self.active_popup: Optional[ctk.CTkFrame] = None
        self._bind_click_id: Optional[str] = None

        # Contenedor horizontal interno
        self.bar_container = ctk.CTkFrame(self, fg_color="transparent", height=height - 1)
        self.bar_container.pack(fill="both", expand=True, padx=SPACING["sm"], pady=(0, 1))

        # Borde inferior de 1 px
        self.bottom_border = ctk.CTkFrame(
            self,
            height=1,
            fg_color=COLORS["border"],
            corner_radius=0,
        )
        self.bottom_border.pack(fill="x", side="bottom")

        # Contenedor para botones
        self.buttons_frame = ctk.CTkFrame(self.bar_container, fg_color="transparent")
        self.buttons_frame.pack(side="left", fill="y", pady=3)

        # Enlace de eventos globales de teclado y ventana
        self._bind_window_events()

    # -----------------------------------------------------------------------
    # Listeners de eventos de la ventana raíz
    # -----------------------------------------------------------------------

    def _bind_window_events(self):
        """Registra listeners de teclado y ventana para cerrar el desplegable."""
        toplevel = self._top_window
        # Esc cierra el menú activo
        toplevel.bind("<Escape>", lambda e: self.close_active_menu(), add="+")
        # Redimensionar o mover ventana principal
        toplevel.bind("<Configure>", self._on_configure, add="+")
        # Perder foco la ventana
        toplevel.bind("<FocusOut>", lambda e: self.close_active_menu(), add="+")
        toplevel.bind("<Deactivate>", lambda e: self.close_active_menu(), add="+")

    def _on_configure(self, event):
        """Cierra el menú si la ventana principal cambia de tamaño o se mueve."""
        try:
            if not self.winfo_exists():
                return
            if event.widget == self._top_window and self.active_popup is not None:
                self.close_active_menu()
        except Exception:
            pass

    # -----------------------------------------------------------------------
    # Registro de menús
    # -----------------------------------------------------------------------

    def add_menu(self, title: str, items: List[Dict[str, Any]]):
        """Registra una sección de menú con sus opciones."""
        self.menus_config[title] = items
        self.menu_order.append(title)

        btn = ctk.CTkButton(
            self.buttons_frame,
            text=title,
            width=70,
            height=30,
            corner_radius=6,
            fg_color="transparent",
            hover_color=COLORS["surface_alt"],
            text_color=COLORS["ink"],
            font=font("body"),
            command=lambda t=title: self._toggle_menu(t),
        )
        btn.pack(side="left", padx=(0, 2), pady=2)
        btn.bind("<Enter>", lambda e, t=title: self._on_button_hover_switch(t))
        self.menu_buttons[title] = btn

    def _on_button_hover_switch(self, title: str):
        """Si ya hay un menú abierto y pasamos el mouse sobre otro botón, cambia de menú."""
        if self.active_menu_name is not None and self.active_menu_name != title:
            self._open_menu(title)

    def _toggle_menu(self, title: str):
        """Abre o cierra el menú al hacer clic en su botón."""
        if self.active_menu_name == title:
            self.close_active_menu()
        else:
            self._open_menu(title)

    # -----------------------------------------------------------------------
    # Apertura y renderizado del desplegable como CTkFrame
    # -----------------------------------------------------------------------

    def _open_menu(self, title: str):
        """Construye y posiciona el desplegable como CTkFrame hijo de la ventana principal."""
        self.close_active_menu()

        if title not in self.menus_config:
            return

        self.active_menu_name = title
        btn = self.menu_buttons[title]

        # Resaltar botón activo
        btn.configure(
            fg_color=COLORS["accent_soft"],
            text_color=COLORS["accent"],
            hover_color=COLORS["accent_soft"],
        )

        try:
            toplevel = self._top_window
            toplevel.update_idletasks()
            btn.update_idletasks()

            # Crear el popup como CTkFrame hijo directo del toplevel (no recortado)
            popup = ctk.CTkFrame(
                toplevel,
                fg_color=COLORS["surface"],
                border_width=1,
                border_color=COLORS["border"],
                corner_radius=RADIUS["card"],
            )
            self.active_popup = popup

            # Contenedor interno con padding de 6 px
            content = ctk.CTkFrame(popup, fg_color="transparent")
            content.pack(fill="both", expand=True, padx=6, pady=6)

            # Generar las filas de opciones
            for item in self.menus_config[title]:
                if item.get("separator"):
                    sep = ctk.CTkFrame(
                        content,
                        height=1,
                        fg_color=COLORS["border"],
                        corner_radius=0,
                    )
                    sep.pack(fill="x", padx=4, pady=4)
                    continue

                label = item.get("label", "")
                icon_char = item.get("icon", "")
                command = item.get("command")
                enabled_check = item.get("enabled", True)
                is_enabled = enabled_check() if callable(enabled_check) else bool(enabled_check)

                row = ctk.CTkFrame(
                    content,
                    height=34,
                    corner_radius=6,
                    fg_color="transparent",
                )
                row.pack(fill="x", pady=1)

                if icon_char and icon_char.strip():
                    icon_lbl = ctk.CTkLabel(
                        row,
                        text=icon_char,
                        width=26,
                        font=("Segoe UI Emoji", 12),
                        text_color=COLORS["ink"] if is_enabled else COLORS["muted_light"],
                        anchor="center",
                    )
                    icon_lbl.pack(side="left", padx=(6, 4))
                    left_pad = (0, 24)
                else:
                    left_pad = (12, 24)

                text_lbl = ctk.CTkLabel(
                    row,
                    text=label,
                    font=font("body"),
                    text_color=COLORS["ink"] if is_enabled else COLORS["muted_light"],
                    anchor="w",
                )
                text_lbl.pack(side="left", padx=left_pad, fill="x", expand=True)

                if is_enabled:
                    for w in (row, text_lbl) + ((icon_lbl,) if (icon_char and icon_char.strip()) else ()):
                        w.bind("<Enter>", lambda e, r=row: r.configure(fg_color=COLORS["surface_alt"]))
                        w.bind("<Leave>", lambda e, r=row: r.configure(fg_color="transparent"))
                        w.bind("<Button-1>", lambda e, cmd=command: self._execute_and_close(cmd))

            # Calcular posición relativa exacta respecto a toplevel
            popup.update_idletasks()
            rx = btn.winfo_rootx() - toplevel.winfo_rootx()
            ry = (btn.winfo_rooty() - toplevel.winfo_rooty()) + btn.winfo_height() + 2

            menu_w = max(210, popup.winfo_reqwidth())
            root_w = toplevel.winfo_width()
            if rx + menu_w > root_w - 8:
                rx = max(8, root_w - menu_w - 8)

            # Posicionar sin pasar width/height a place() (evita ValueError en CustomTkinter)
            popup.place(x=rx, y=ry)
            popup.lift()

            # Diferir el registro del bind de clic fuera para evitar capturar el clic actual
            self.after(50, self._enable_click_outside)
        except Exception:
            pass

    def _enable_click_outside(self):
        """Activa el listener de clic fuera únicamente cuando el popup está activo."""
        if self.active_popup is not None and self._bind_click_id is None:
            self._bind_click_id = self._top_window.bind("<Button-1>", self._on_root_click, add="+")

    def _on_root_click(self, event):
        """Detecta clics fuera del menú activo y de sus botones para cerrarlo de forma segura."""
        if not self.active_popup:
            return

        # 1. Comprobar si el clic cayó dentro del popup activo (coordenadas de pantalla)
        try:
            px = self.active_popup.winfo_rootx()
            py = self.active_popup.winfo_rooty()
            pw = self.active_popup.winfo_width()
            ph = self.active_popup.winfo_height()
            if px <= event.x_root <= px + pw and py <= event.y_root <= py + ph:
                return  # Clic dentro del menú desplegable
        except Exception:
            pass

        # 2. Comprobar si el clic cayó en algún botón de la barra de menú
        for b in self.menu_buttons.values():
            try:
                bx = b.winfo_rootx()
                by = b.winfo_rooty()
                bw = b.winfo_width()
                bh = b.winfo_height()
                if bx <= event.x_root <= bx + bw and by <= event.y_root <= by + bh:
                    return  # Clic en un botón de menú (su propio callback lo gestiona)
            except Exception:
                pass

        # 3. Comprobación por jerarquía de widgets (winfo_parent)
        try:
            curr = event.widget
            popup_id = str(self.active_popup)
            while curr:
                if str(curr) == popup_id:
                    return
                parent_id = getattr(curr, "winfo_parent", lambda: "")()
                if not parent_id:
                    break
                try:
                    curr = self._top_window.nametowidget(parent_id)
                except Exception:
                    break
        except Exception:
            pass

        # Clic fuera: cerrar inmediatamente
        self.close_active_menu()

    # -----------------------------------------------------------------------
    # Cierre y ejecución
    # -----------------------------------------------------------------------

    def _execute_and_close(self, command: Optional[Callable]):
        """Cierra el desplegable y ejecuta el callback de forma asíncrona (after 10ms)."""
        self.close_active_menu()
        if command:
            self.after(10, command)

    def close_active_menu(self):
        """Cierra el menú desplegable activo y restablece el botón."""
        # Desvincular listener de clic fuera si estaba activo
        if self._bind_click_id and self._top_window:
            try:
                self._top_window.unbind("<Button-1>", self._bind_click_id)
            except Exception:
                pass
            self._bind_click_id = None

        try:
            if not self.winfo_exists():
                return
        except Exception:
            return

        try:
            if self.active_menu_name and self.active_menu_name in self.menu_buttons:
                self.menu_buttons[self.active_menu_name].configure(
                    fg_color="transparent",
                    text_color=COLORS["ink"],
                    hover_color=COLORS["surface_alt"],
                )

            if self.active_popup is not None:
                try:
                    self.active_popup.place_forget()
                    self.active_popup.destroy()
                except Exception:
                    pass
                self.active_popup = None

            self.active_menu_name = None
        except Exception:
            pass
