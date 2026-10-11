# -*- coding: utf-8 -*-
"""FormularioBase: Clase base para modales de creación y edición en PEA-i.

Proporciona:
- Ventana modal centrada tipo CTkToplevel con grab_set y tamaño fijo.
- Encabezado con título y subtítulo.
- Agrupación por secciones visuales.
- Campos con etiqueta superior y espaciado consistente de 8 px.
- Validación en línea reactiva (borde rojo y mensaje de error sin cerrar el modal).
- Botones inferiores fijos: Secundario 'Cancelar' (Esc) y Primario 'Guardar' (Enter).
- Helpers para combos de grupos vinculados con 'código - nombre'.
"""

from typing import Optional, Dict, Any, Callable, List, Tuple
import re
import tkinter as tk
import customtkinter as ctk

from gui.styles import (
    COLORS,
    RADIUS,
    SPACING,
    CONTROL_HEIGHT,
    font,
    entry,
    boton_primario,
    boton_secundario,
    combo,
)


class FormularioBase(ctk.CTkToplevel):
    """Componente base reutilizable para formularios modales de la aplicación."""

    def __init__(
        self,
        master,
        title: str,
        subtitle: str,
        width: int = 500,
        height: int = 620,
        on_save: Optional[Callable[[Dict[str, Any]], None]] = None,
        data: Optional[Dict[str, Any]] = None,
        app: Optional[Any] = None,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self.master = master
        self._app_ref = app
        self._on_save = on_save
        self._initial_data = data or {}
        self.result: Optional[Dict[str, Any]] = None

        # Configuración de ventana modal
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.minsize(width, height)
        self.resizable(False, False)
        self.configure(fg_color=COLORS['bg'])

        self.transient(master)
        self.grab_set()

        self._center_window(width, height)

        # Registro interno de campos y validadores
        # {field_key: {'widget': widget, 'error_lbl': lbl, 'required': bool, 'validator': fn, 'type': str, ...}}
        self._fields: Dict[str, Dict[str, Any]] = {}

        # ── Contenedor principal con tarjeta blanca ────────────────────
        self.card = ctk.CTkFrame(
            self,
            fg_color=COLORS['surface'],
            corner_radius=RADIUS['card'],
            border_width=1,
            border_color=COLORS['border'],
        )
        self.card.pack(fill='both', expand=True, padx=SPACING['md'], pady=SPACING['md'])

        # ── 1. Encabezado fijo ─────────────────────────────────────────
        self.header_frame = ctk.CTkFrame(self.card, fg_color='transparent')
        self.header_frame.pack(fill='x', padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['sm']))

        self.lbl_title = ctk.CTkLabel(
            self.header_frame,
            text=title,
            font=font('title'),
            text_color=COLORS['ink'],
            anchor='w',
        )
        self.lbl_title.pack(fill='x', anchor='w')

        self.lbl_subtitle = ctk.CTkLabel(
            self.header_frame,
            text=subtitle,
            font=font('small'),
            text_color=COLORS['muted'],
            anchor='w',
        )
        self.lbl_subtitle.pack(fill='x', anchor='w', pady=(SPACING['xs'], 0))

        # Divisor sutil
        self.header_sep = ctk.CTkFrame(self.card, height=1, fg_color=COLORS['border'], corner_radius=0)
        self.header_sep.pack(fill='x', padx=SPACING['lg'], pady=(SPACING['xs'], SPACING['sm']))

        # ── 2. Botones de acción inferiores fijos ───────────────────────
        self.actions_frame = ctk.CTkFrame(self.card, fg_color='transparent')
        self.actions_frame.pack(side='bottom', fill='x', padx=SPACING['lg'], pady=(SPACING['sm'], SPACING['lg']))

        self.btn_save = boton_primario(
            self.actions_frame,
            text="Guardar",
            command=self.save,
            height=CONTROL_HEIGHT,
            width=110,
        )
        self.btn_save.pack(side='right', padx=(SPACING['sm'], 0))

        self.btn_cancel = boton_secundario(
            self.actions_frame,
            text="Cancelar",
            command=self.cancel,
            height=CONTROL_HEIGHT,
            width=100,
        )
        self.btn_cancel.pack(side='right')

        # ── 3. Cuerpo con campos scrollable ────────────────────────────
        self.body = ctk.CTkScrollableFrame(
            self.card,
            fg_color='transparent',
            corner_radius=0,
        )
        self.body.pack(fill='both', expand=True, padx=SPACING['md'], pady=(0, SPACING['xs']))

        # Atajos de teclado
        self.bind('<Escape>', lambda e: self.cancel())
        self.bind('<Return>', lambda e: self.save())

    def _center_window(self, width: int, height: int):
        """Centra la ventana modal sobre su ventana contenedora."""
        self.update_idletasks()
        try:
            pw = self.master.winfo_width()
            ph = self.master.winfo_height()
            px = self.master.winfo_rootx()
            py = self.master.winfo_rooty()
            x = px + max(0, (pw - width) // 2)
            y = py + max(0, (ph - height) // 2)
            self.geometry(f"{width}x{height}+{x}+{y}")
        except Exception:
            self.geometry(f"{width}x{height}")

    def resolve_app(self):
        """Resuelve la instancia principal de la aplicación."""
        if self._app_ref is not None:
            return self._app_ref
        curr = self.master
        while curr is not None:
            if hasattr(curr, 'grupo_crud') or hasattr(curr, 'multilista'):
                self._app_ref = curr
                return curr
            curr = getattr(curr, 'master', None)
        return None

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║  CREACIÓN DE SECCIONES Y CAMPOS FORMULARIO                     ║
    # ╚══════════════════════════════════════════════════════════════════╝

    def add_section(self, title: str):
        """Agrega un encabezado de sección visual dentro del formulario."""
        sec_frame = ctk.CTkFrame(self.body, fg_color='transparent')
        sec_frame.pack(fill='x', padx=SPACING['sm'], pady=(SPACING['md'], SPACING['xs']))

        sec_label = ctk.CTkLabel(
            sec_frame,
            text=title.upper(),
            font=font('badge'),
            text_color=COLORS['accent'],
            anchor='w',
        )
        sec_label.pack(side='left', padx=(0, SPACING['sm']))

        line = ctk.CTkFrame(sec_frame, height=1, fg_color=COLORS['accent_border'], corner_radius=0)
        line.pack(side='left', fill='x', expand=True, pady=6)

    def add_text_field(
        self,
        key: str,
        label_text: str,
        placeholder: str = "",
        required: bool = False,
        validator: Optional[Callable[[str], Optional[str]]] = None,
        initial_value: str = "",
        disabled: bool = False,
    ) -> ctk.CTkEntry:
        """Crea un campo de texto con etiqueta arriba, asterisco si es obligatorio,
        y mensaje de error en línea."""
        field_container = ctk.CTkFrame(self.body, fg_color='transparent')
        field_container.pack(fill='x', padx=SPACING['sm'], pady=(0, SPACING['sm']))

        # Etiqueta superior con indicador de requerido
        lbl_frame = ctk.CTkFrame(field_container, fg_color='transparent')
        lbl_frame.pack(fill='x', pady=(0, 2))

        lbl = ctk.CTkLabel(
            lbl_frame,
            text=label_text,
            font=font('body'),
            text_color=COLORS['ink'],
            anchor='w',
        )
        lbl.pack(side='left')

        if required:
            req_mark = ctk.CTkLabel(
                lbl_frame,
                text=" *",
                font=font('body'),
                text_color=COLORS['danger'],
            )
            req_mark.pack(side='left')

        # Control de entrada
        widget = entry(
            field_container,
            placeholder_text=placeholder,
            height=CONTROL_HEIGHT,
        )
        if initial_value:
            widget.insert(0, str(initial_value))
        if disabled:
            widget.configure(state='disabled')
        widget.pack(fill='x')

        # Etiqueta de error en línea
        err_lbl = ctk.CTkLabel(
            field_container,
            text="",
            font=font('small'),
            text_color=COLORS['danger'],
            anchor='w',
        )
        err_lbl.pack(fill='x', pady=(1, 0))

        # Limpiar error reactivamente cuando el usuario escribe
        widget.bind('<KeyRelease>', lambda e, k=key: self.clear_error(k))

        self._fields[key] = {
            'type': 'entry',
            'widget': widget,
            'error_lbl': err_lbl,
            'required': required,
            'validator': validator,
            'label': label_text,
        }

        return widget

    def add_combo_field(
        self,
        key: str,
        label_text: str,
        options: List[str],
        required: bool = False,
        initial_value: Optional[str] = None,
        mapping: Optional[Dict[str, Any]] = None,
        reverse_mapping: Optional[Dict[Any, str]] = None,
    ) -> ctk.CTkOptionMenu:
        """Crea un selector combo con opciones legibles y mapeo opcional de IDs."""
        field_container = ctk.CTkFrame(self.body, fg_color='transparent')
        field_container.pack(fill='x', padx=SPACING['sm'], pady=(0, SPACING['sm']))

        lbl_frame = ctk.CTkFrame(field_container, fg_color='transparent')
        lbl_frame.pack(fill='x', pady=(0, 2))

        lbl = ctk.CTkLabel(
            lbl_frame,
            text=label_text,
            font=font('body'),
            text_color=COLORS['ink'],
            anchor='w',
        )
        lbl.pack(side='left')

        if required:
            req_mark = ctk.CTkLabel(
                lbl_frame,
                text=" *",
                font=font('body'),
                text_color=COLORS['danger'],
            )
            req_mark.pack(side='left')

        var = ctk.StringVar()
        safe_options = options if options else ["(Ninguno disponible)"]
        default_val = initial_value if initial_value in safe_options else safe_options[0]
        var.set(default_val)

        widget = combo(
            field_container,
            values=safe_options,
            variable=var,
            width=200,
            command=lambda val, k=key: self.clear_error(k),
        )
        widget.pack(fill='x')

        err_lbl = ctk.CTkLabel(
            field_container,
            text="",
            font=font('small'),
            text_color=COLORS['danger'],
            anchor='w',
        )
        err_lbl.pack(fill='x', pady=(1, 0))

        self._fields[key] = {
            'type': 'combo',
            'widget': widget,
            'var': var,
            'error_lbl': err_lbl,
            'required': required,
            'mapping': mapping or {},
            'reverse_mapping': reverse_mapping or {},
            'label': label_text,
        }

        return widget

    def add_checkbox_field(
        self,
        key: str,
        label_text: str,
        initial_value: bool = True,
    ) -> ctk.CTkCheckBox:
        """Crea un checkbox para atributos booleanos de estado."""
        field_container = ctk.CTkFrame(self.body, fg_color='transparent')
        field_container.pack(fill='x', padx=SPACING['sm'], pady=(SPACING['xs'], SPACING['sm']))

        var = ctk.BooleanVar(value=bool(initial_value))
        widget = ctk.CTkCheckBox(
            field_container,
            text=label_text,
            variable=var,
            font=font('body'),
            text_color=COLORS['ink'],
            fg_color=COLORS['accent'],
            hover_color=COLORS['accent_hover'],
            corner_radius=RADIUS['control'],
        )
        widget.pack(anchor='w')

        self._fields[key] = {
            'type': 'checkbox',
            'widget': widget,
            'var': var,
            'label': label_text,
        }

        return widget

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║  VALIDACIÓN EN LÍNEA                                            ║
    # ╚══════════════════════════════════════════════════════════════════╝

    def set_error(self, key: str, message: str):
        """Muestra un mensaje de error y resalta el borde en rojo."""
        info = self._fields.get(key)
        if not info:
            return

        err_lbl = info.get('error_lbl')
        if err_lbl:
            err_lbl.configure(text=f"• {message}")

        widget = info.get('widget')
        if widget and hasattr(widget, 'configure'):
            try:
                widget.configure(border_color=COLORS['danger'])
            except Exception:
                pass

    def clear_error(self, key: str):
        """Limpia el mensaje de error y restablece el borde."""
        info = self._fields.get(key)
        if not info:
            return

        err_lbl = info.get('error_lbl')
        if err_lbl:
            err_lbl.configure(text="")

        widget = info.get('widget')
        if widget and hasattr(widget, 'configure'):
            try:
                widget.configure(border_color=COLORS['border'])
            except Exception:
                pass

    def validate_all(self) -> bool:
        """Valida todos los campos registrados. Si hay errores, no cierra el modal."""
        is_all_valid = True
        first_error_widget = None

        for key, info in self._fields.items():
            field_type = info['type']
            widget = info['widget']
            val = ""

            if field_type == 'entry':
                val = widget.get().strip()
            elif field_type == 'combo':
                val = info['var'].get().strip()

            # 1. Validación de campo requerido
            if info.get('required') and not val:
                self.set_error(key, f"El campo '{info['label']}' es obligatorio.")
                is_all_valid = False
                if first_error_widget is None:
                    first_error_widget = widget
                continue

            # 2. Validación personalizada por regla
            validator = info.get('validator')
            if validator:
                err_msg = validator(val)
                if err_msg:
                    self.set_error(key, err_msg)
                    is_all_valid = False
                    if first_error_widget is None:
                        first_error_widget = widget
                    continue

            self.clear_error(key)

        if first_error_widget and hasattr(first_error_widget, 'focus_set'):
            first_error_widget.focus_set()

        return is_all_valid

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║  UTILIDADES DE VALIDACIÓN REUTILIZABLES                          ║
    # ╚══════════════════════════════════════════════════════════════════╝

    @staticmethod
    def validator_numerico(val: str) -> Optional[str]:
        """Valida que el valor contenga solo caracteres numéricos."""
        if val and not val.isdigit():
            return "Este campo debe contener únicamente números."
        return None

    @staticmethod
    def validator_cedula(val: str) -> Optional[str]:
        """Valida formato numérico para cédula o identificación."""
        if not val:
            return "La cédula / identificación es obligatoria."
        if not val.isdigit():
            return "La cédula debe contener exclusivamente dígitos numéricos."
        if len(val) < 4:
            return "La identificación debe tener al menos 4 dígitos."
        return None

    @staticmethod
    def validator_email(val: str) -> Optional[str]:
        """Valida formato de correo electrónico."""
        if not val:
            return "El correo electrónico es obligatorio."
        regex = r"^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$"
        if not re.match(regex, val.strip()):
            return "Ingresa un correo electrónico válido (ej. usuario@dominio.edu.co)."
        return None

    @staticmethod
    def validator_anio(val: str) -> Optional[str]:
        """Valida que sea un año de 4 dígitos dentro de un rango razonable."""
        if not val:
            return "El año de publicación es obligatorio."
        if not val.isdigit() or len(val) != 4:
            return "El año debe tener exactamente 4 dígitos (ej. 2024)."
        try:
            year_int = int(val)
            if year_int < 1900 or year_int > 2100:
                return "Ingresa un año válido entre 1900 y 2100."
        except ValueError:
            return "Año numérico inválido."
        return None

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║  HELPER PARA GRUPOS ASOCIADOS (CÓDIGO - NOMBRE)                 ║
    # ╚══════════════════════════════════════════════════════════════════╝

    def get_grupos_combo_data(self) -> Tuple[List[str], Dict[str, Any], Dict[Any, str]]:
        """Obtiene las opciones de grupos formateadas como 'código - nombre' y sus mapeos."""
        app = self.resolve_app()
        options = []
        mapping = {}          # display_str -> grupo_id
        reverse_mapping = {}  # grupo_id -> display_str

        if app and hasattr(app, 'grupo_crud'):
            try:
                grupos = app.grupo_crud.list_all()
                for g in grupos:
                    gid = getattr(g, 'id', None)
                    code = getattr(g, 'codigo_gruplac', '') or getattr(g, 'code', '')
                    name = getattr(g, 'nombre', '') or getattr(g, 'name', '')

                    display_str = f"{code} - {name}" if code and name else (name or code or f"Grupo {gid}")
                    options.append(display_str)
                    mapping[display_str] = gid
                    if gid is not None:
                        reverse_mapping[gid] = display_str
                        reverse_mapping[str(gid)] = display_str
                    if code:
                        reverse_mapping[code] = display_str
            except Exception:
                pass

        if not options:
            options = ["(Sin grupos registrados)"]
            mapping[options[0]] = None

        return options, mapping, reverse_mapping

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║  ACCIONES DE GUARDAR Y CANCELAR                                 ║
    # ╚══════════════════════════════════════════════════════════════════╝

    def get_data(self) -> Dict[str, Any]:
        """Extrae el diccionario normalizado de datos. Sobrescribir en subclases."""
        result = {}
        for key, info in self._fields.items():
            ftype = info['type']
            if ftype == 'entry':
                result[key] = info['widget'].get().strip()
            elif ftype == 'combo':
                disp = info['var'].get()
                mapping = info.get('mapping', {})
                result[key] = mapping.get(disp, disp)
            elif ftype == 'checkbox':
                result[key] = bool(info['var'].get())
        return result

    def save(self):
        """Valida los campos y, de ser válidos, ejecuta callback y cierra."""
        if not self.validate_all():
            return

        data = self.get_data()
        self.result = data

        if self._on_save:
            self._on_save(data)

        self.destroy()

    def cancel(self):
        """Cancela la operación y cierra la ventana."""
        self.result = None
        self.destroy()
