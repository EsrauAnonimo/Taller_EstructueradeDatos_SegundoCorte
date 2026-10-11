# -*- coding: utf-8 -*-
"""Formulario modal para creación y edición de Investigador."""

from typing import Optional, Dict, Any, Callable
from gui.forms.base_form import FormularioBase


class InvestigadorForm(FormularioBase):
    """Modal para captura y modificación de atributos de Investigador."""

    def __init__(
        self,
        master,
        data: Optional[Dict[str, Any]] = None,
        investigador: Optional[Any] = None,
        on_save: Optional[Callable[[Dict[str, Any]], None]] = None,
        app: Optional[Any] = None,
        **kwargs,
    ):
        initial_data = {}
        if data:
            initial_data = dict(data)
        elif investigador is not None:
            if hasattr(investigador, 'to_dict'):
                initial_data = investigador.to_dict()
            elif hasattr(investigador, '__dict__'):
                initial_data = dict(investigador.__dict__)

        is_edit = bool(initial_data)
        title_text = "Editar investigador" if is_edit else "Crear investigador"
        sub_text = (
            "Modifica los datos personales y de vinculación del investigador"
            if is_edit
            else "Registra un nuevo investigador adscrito a un grupo académico"
        )

        super().__init__(
            master=master,
            title=title_text,
            subtitle=sub_text,
            width=520,
            height=660,
            on_save=on_save,
            data=initial_data,
            app=app,
            **kwargs,
        )

        self._build_fields()

    def _build_fields(self):
        """Construye las secciones y campos del formulario."""
        d = self._initial_data

        # --- Sección 1: Datos Personales ---
        self.add_section("Datos personales")

        ced_val = d.get('cedula') or d.get('id', '')
        self.add_text_field(
            key='cedula',
            label_text="Cédula / Identificación",
            placeholder="Ej. 1098765432 (solo números)",
            required=True,
            validator=self.validator_cedula,
            initial_value=str(ced_val) if ced_val else "",
        )

        name_val = d.get('nombres') or d.get('name', '')
        self.add_text_field(
            key='nombres',
            label_text="Nombres y apellidos completos",
            placeholder="Ej. Dra. María González Pérez",
            required=True,
            initial_value=str(name_val),
        )

        email_val = d.get('email', '') or d.get('correo', '')
        self.add_text_field(
            key='email',
            label_text="Correo electrónico institucional",
            placeholder="usuario@institucion.edu.co",
            required=True,
            validator=self.validator_email,
            initial_value=str(email_val),
        )

        # --- Sección 2: Vinculación Académica ---
        self.add_section("Vinculación académica")

        # Combo de Grupo asociado ("código - nombre")
        options, mapping, reverse_mapping = self.get_grupos_combo_data()
        current_group_val = d.get('grupo_id') or d.get('group', None)
        initial_combo_val = None
        if current_group_val is not None:
            initial_combo_val = reverse_mapping.get(current_group_val) or reverse_mapping.get(str(current_group_val))

        self.add_combo_field(
            key='grupo_id',
            label_text="Grupo de investigación adscrito",
            options=options,
            required=True,
            initial_value=initial_combo_val,
            mapping=mapping,
            reverse_mapping=reverse_mapping,
        )

        horas_val = d.get('horas_dedicacion', 0)
        self.add_text_field(
            key='horas_dedicacion',
            label_text="Horas de dedicación semanal",
            placeholder="Ej. 20 o 40 (opcional)",
            required=False,
            validator=self.validator_numerico,
            initial_value=str(horas_val) if horas_val else "",
        )

        active_val = d.get('active', d.get('activo', True))
        self.add_checkbox_field(
            key='active',
            label_text="Investigador activo en el sistema",
            initial_value=bool(active_val),
        )

    def get_data(self) -> Dict[str, Any]:
        """Extrae el diccionario normalizado con alias para el CRUD."""
        raw = super().get_data()
        cedula = raw.get('cedula', '').strip()
        nombres = raw.get('nombres', '').strip()
        email = raw.get('email', '').strip()
        grupo_id = raw.get('grupo_id')
        active = bool(raw.get('active', True))
        try:
            horas = int(raw.get('horas_dedicacion', 0) or 0)
        except (ValueError, TypeError):
            horas = 0

        return {
            'id': cedula,
            'cedula': cedula,
            'name': nombres,
            'nombres': nombres,
            'email': email,
            'group': grupo_id,
            'grupo_id': grupo_id,
            'horas_dedicacion': horas,
            'active': active,
            'activo': active,
        }