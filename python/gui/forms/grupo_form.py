# -*- coding: utf-8 -*-
"""Formulario modal para creación y edición de Grupo de Investigación."""

from typing import Optional, Dict, Any, Callable
from gui.forms.base_form import FormularioBase


class GrupoForm(FormularioBase):
    """Modal para captura y modificación de atributos de Grupo de Investigación."""

    def __init__(
        self,
        master,
        data: Optional[Dict[str, Any]] = None,
        grupo: Optional[Any] = None,
        on_save: Optional[Callable[[Dict[str, Any]], None]] = None,
        app: Optional[Any] = None,
        **kwargs,
    ):
        # Convertir objeto entidad a diccionario si se proporcionó
        initial_data = {}
        if data:
            initial_data = dict(data)
        elif grupo is not None:
            if hasattr(grupo, 'to_dict'):
                initial_data = grupo.to_dict()
            elif hasattr(grupo, '__dict__'):
                initial_data = dict(grupo.__dict__)

        is_edit = bool(initial_data)
        title_text = "Editar grupo de investigación" if is_edit else "Crear grupo de investigación"
        sub_text = (
            "Modifica los datos del grupo académico seleccionado"
            if is_edit
            else "Registra un nuevo grupo académico en el sistema"
        )

        super().__init__(
            master=master,
            title=title_text,
            subtitle=sub_text,
            width=500,
            height=580,
            on_save=on_save,
            data=initial_data,
            app=app,
            **kwargs,
        )

        self._build_fields()

    def _build_fields(self):
        """Construye las secciones y campos del formulario."""
        d = self._initial_data

        # --- Sección 1: Información del Grupo ---
        self.add_section("Información del grupo")

        code_val = d.get('code') or d.get('codigo_gruplac', '')
        self.add_text_field(
            key='code',
            label_text="Código Gruplac",
            placeholder="Ej. COL0008234",
            required=True,
            initial_value=str(code_val),
        )

        name_val = d.get('name') or d.get('nombre', '')
        self.add_text_field(
            key='name',
            label_text="Nombre del grupo",
            placeholder="Nombre de la línea o grupo de investigación",
            required=True,
            initial_value=str(name_val),
        )

        cat_val = d.get('category') or d.get('categoria', '')
        self.add_text_field(
            key='category',
            label_text="Categoría",
            placeholder="Ej. A1, A, B, C o Reconocido",
            required=False,
            initial_value=str(cat_val),
        )

        # --- Sección 2: Liderazgo y Estado ---
        self.add_section("Liderazgo y estado")

        leader_val = d.get('leader') or d.get('lider', '')
        self.add_text_field(
            key='leader',
            label_text="Líder del grupo",
            placeholder="Nombre completo del líder o director",
            required=True,
            initial_value=str(leader_val),
        )

        active_val = d.get('active', d.get('activo', True))
        self.add_checkbox_field(
            key='active',
            label_text="Grupo activo en el sistema",
            initial_value=bool(active_val),
        )

    def get_data(self) -> Dict[str, Any]:
        """Extrae el diccionario normalizado con alias completos para la capa CRUD."""
        raw = super().get_data()
        code = raw.get('code', '').strip()
        name = raw.get('name', '').strip()
        cat = raw.get('category', '').strip()
        leader = raw.get('leader', '').strip()
        active = bool(raw.get('active', True))

        return {
            'code': code,
            'codigo_gruplac': code,
            'name': name,
            'nombre': name,
            'category': cat,
            'categoria': cat,
            'leader': leader,
            'lider': leader,
            'active': active,
            'activo': active,
        }