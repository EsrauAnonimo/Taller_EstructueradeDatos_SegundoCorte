# -*- coding: utf-8 -*-
"""Modal dialog for importing MinCiencias / SCIENTI groups via URL with loading state and validation."""

import threading
import re
from typing import Optional, Callable, Dict, Any
import customtkinter as ctk

from gui.styles import (
    COLORS,
    RADIUS,
    SPACING,
    font,
    button,
    entry,
)
from scraping import scienti


class UrlImportModal(ctk.CTkToplevel):
    """Ventana modal para importar datos desde MinCiencias con validación y estado de carga interactivo."""

    def __init__(
        self,
        parent,
        on_success: Optional[Callable[[Dict[str, Any]], None]] = None,
        initial_url: str = "",
    ):
        super().__init__(parent)
        self.parent = parent
        self._on_success = on_success
        self._is_loading = False

        self.title("Importar desde MinCiencias")
        self.geometry("520x340")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['bg'])

        # Modal behavior
        self.transient(parent)
        self.grab_set()

        # Centrar sobre la ventana padre
        self._center_window()

        # Contenedor principal con estilo tarjeta
        self.main_card = ctk.CTkFrame(
            self,
            fg_color=COLORS['surface'],
            corner_radius=RADIUS['card'],
            border_width=1,
            border_color=COLORS['border'],
        )
        self.main_card.pack(fill='both', expand=True, padx=SPACING['md'], pady=SPACING['md'])

        # --- Encabezado ---
        self.header_frame = ctk.CTkFrame(self.main_card, fg_color='transparent')
        self.header_frame.pack(fill='x', padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['sm']))

        self.header_icon = ctk.CTkLabel(
            self.header_frame,
            text="",
            font=('Segoe UI', 12),
            width=8,
            height=36,
            corner_radius=4,
            fg_color=COLORS['accent'],
        )
        self.header_icon.pack(side='left', padx=(0, SPACING['sm']))

        self.header_texts = ctk.CTkFrame(self.header_frame, fg_color='transparent')
        self.header_texts.pack(side='left', fill='x', expand=True)

        self.lbl_title = ctk.CTkLabel(
            self.header_texts,
            text="Importar grupo desde MinCiencias",
            font=font('heading'),
            text_color=COLORS['ink'],
            anchor='w',
        )
        self.lbl_title.pack(fill='x', anchor='w')

        self.lbl_subtitle = ctk.CTkLabel(
            self.header_texts,
            text="Ingresa el enlace de GrupLAC para extraer investigadores y productos.",
            font=font('small'),
            text_color=COLORS['muted'],
            anchor='w',
        )
        self.lbl_subtitle.pack(fill='x', anchor='w')

        # --- Formulario ---
        self.form_frame = ctk.CTkFrame(self.main_card, fg_color='transparent')
        self.form_frame.pack(fill='x', padx=SPACING['lg'], pady=(SPACING['sm'], 0))

        self.lbl_field = ctk.CTkLabel(
            self.form_frame,
            text="URL de la página de GrupLAC:",
            font=font('small'),
            text_color=COLORS['ink_soft'],
            anchor='w',
        )
        self.lbl_field.pack(fill='x', anchor='w', pady=(0, SPACING['xs']))

        self.url_entry = entry(
            self.form_frame,
            placeholder_text="https://scienti.minciencias.gov.co/gruplac/jsp/visualiza/...",
            width=460,
        )
        if initial_url:
            self.url_entry.insert(0, initial_url)
        self.url_entry.pack(fill='x', pady=(0, SPACING['xs']))
        self.url_entry.bind('<KeyRelease>', lambda e: self._clear_error())
        self.url_entry.bind('<Return>', lambda e: self._on_submit())

        # Mensaje de error / validación
        self.error_label = ctk.CTkLabel(
            self.form_frame,
            text="",
            font=font('small'),
            text_color=COLORS['danger'],
            anchor='w',
        )
        self.error_label.pack(fill='x', anchor='w')

        # Estado de carga / Barra de progreso
        self.loading_frame = ctk.CTkFrame(self.main_card, fg_color='transparent')
        self.loading_frame.pack(fill='x', padx=SPACING['lg'], pady=(SPACING['xs'], SPACING['xs']))

        self.progress_bar = ctk.CTkProgressBar(
            self.loading_frame,
            mode='indeterminate',
            height=6,
            corner_radius=3,
            progress_color=COLORS['accent'],
        )

        self.status_label = ctk.CTkLabel(
            self.loading_frame,
            text="",
            font=font('small'),
            text_color=COLORS['muted'],
            anchor='center',
        )

        # --- Botones inferiores ---
        self.actions_frame = ctk.CTkFrame(self.main_card, fg_color='transparent')
        self.actions_frame.pack(side='bottom', fill='x', padx=SPACING['lg'], pady=(0, SPACING['lg']))

        self.btn_submit = button(
            self.actions_frame,
            text="Importar datos",
            variant='primary',
            command=self._on_submit,
        )
        self.btn_submit.pack(side='right', padx=(SPACING['sm'], 0))

        self.btn_cancel = button(
            self.actions_frame,
            text="Cancelar",
            variant='secondary',
            command=self.destroy,
        )
        self.btn_cancel.pack(side='right')

        # Enfocar el campo de texto
        self.after(100, self.url_entry.focus_set)

    def _center_window(self):
        """Centra el diálogo modal relativo a la ventana principal."""
        self.update_idletasks()
        try:
            pw = self.parent.winfo_width()
            ph = self.parent.winfo_height()
            px = self.parent.winfo_x()
            py = self.parent.winfo_y()
            w = 520
            h = 340
            x = px + max(0, (pw - w) // 2)
            y = py + max(0, (ph - h) // 2)
            self.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            self.geometry("520x340")

    def _clear_error(self):
        """Limpia el mensaje de error cuando el usuario interactúa."""
        self.error_label.configure(text="")

    def _validate_url(self, url: str) -> Optional[str]:
        """Valida que la URL tenga formato válido para GrupLAC."""
        if not url:
            return "Por favor ingresa una URL."
        url = url.strip()
        if not (url.startswith("http://") or url.startswith("https://")):
            return "La URL debe iniciar con 'http://' o 'https://'."
        if len(url) < 15:
            return "La URL ingresada es demasiado corta."
        return None

    def _on_submit(self):
        """Valida e inicia el proceso de descarga en segundo plano."""
        if self._is_loading:
            return

        url = self.url_entry.get().strip()
        err = self._validate_url(url)
        if err:
            self.error_label.configure(text=err)
            return

        self._set_loading(True)
        # Ejecución en hilo separado para no bloquear la animación ni la interfaz
        thread = threading.Thread(target=self._scrape_worker, args=(url,), daemon=True)
        thread.start()

    def _set_loading(self, loading: bool):
        """Actualiza el estado visual entre cargando y reposo."""
        self._is_loading = loading
        if loading:
            self.btn_submit.configure(state='disabled', text="Descargando...")
            self.btn_cancel.configure(state='disabled')
            self.url_entry.configure(state='disabled')
            self.status_label.configure(text="Conectando con MinCiencias y procesando datos...")
            self.status_label.pack(fill='x', pady=(0, SPACING['xs']))
            self.progress_bar.pack(fill='x')
            self.progress_bar.start()
            self._clear_error()
        else:
            self.btn_submit.configure(state='normal', text="Importar datos")
            self.btn_cancel.configure(state='normal')
            self.url_entry.configure(state='normal')
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            self.status_label.pack_forget()

    def _scrape_worker(self, url: str):
        """Worker en segundo plano para realizar el web scraping sin congelar la GUI."""
        try:
            datos = scienti.download_group(url)
            if not datos or "error" in datos:
                error_msg = datos.get("error", "No se encontraron datos en la página indicada.") if isinstance(datos, dict) else "Error al procesar la respuesta."
                self.after(0, self._on_scrape_error, error_msg)
            else:
                self.after(0, self._on_scrape_success, datos)
        except Exception as e:
            self.after(0, self._on_scrape_error, str(e))

    def _on_scrape_success(self, datos: Dict[str, Any]):
        """Notifica el éxito de la descarga y cierra el modal."""
        self._set_loading(False)
        if self._on_success:
            self._on_success(datos)
        self.destroy()

    def _on_scrape_error(self, message: str):
        """Muestra el error dentro del modal para que el usuario pueda corregirlo."""
        self._set_loading(False)
        self.error_label.configure(text=message)
