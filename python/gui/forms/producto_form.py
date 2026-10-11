# -*- coding: utf-8 -*-
"""Formulario modal para creación y edición de Producto de Investigación."""

from typing import Optional, Dict, Any, Callable
from gui.forms.base_form import FormularioBase


class ProductoForm(FormularioBase):
    """Modal para captura y modificación de atributos de Producto de Investigación."""

    TIPOS_PRODUCTO_COMUNES = [
        "Artículo en revista indexada",
        "Libro resultado de investigación",
        "Capítulo de libro",
        "Ponencia en evento científico",
        "Software / Desarrollo tecnológico",
        "Patente o modelo de utilidad",
        "Trabajo de grado / Tesis",
        "Otro tipo de producto",
    ]

    def __init__(
        self,
        master,
        data: Optional[Dict[str, Any]] = None,
        producto: Optional[Any] = None,
        on_save: Optional[Callable[[Dict[str, Any]], None]] = None,
        app: Optional[Any] = None,
        **kwargs,
    ):
        initial_data = {}
        if data:
            initial_data = dict(data)
        elif producto is not None:
            if hasattr(producto, 'to_dict'):
                initial_data = producto.to_dict()
            elif hasattr(producto, '__dict__'):
                initial_data = dict(producto.__dict__)

        is_edit = bool(initial_data)
        title_text = "Editar producto de investigación" if is_edit else "Crear producto de investigación"
        sub_text = (
            "Modifica los datos de la producción científica seleccionada"
            if is_edit
            else "Registra un nuevo producto, publicación o desarrollo científico"
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

        # --- Sección 1: Detalles del Producto ---
        self.add_section("Detalles del producto")

        title_val = d.get('titulo') or d.get('title', '')
        self.add_text_field(
            key='titulo',
            label_text="Título de la publicación o desarrollo",
            placeholder="Título completo del artículo, libro o desarrollo",
            required=True,
            initial_value=str(title_val),
        )

        type_val = d.get('tipo') or d.get('type', '')
        # Si el tipo preexistente no está en la lista estándar, agregarlo
        tipo_options = list(self.TIPOS_PRODUCTO_COMUNES)
        if type_val and type_val not in tipo_options:
            tipo_options.insert(0, str(type_val))

        self.add_combo_field(
            key='tipo',
            label_text="Tipo de producto científico",
            options=tipo_options,
            required=True,
            initial_value=str(type_val) if type_val else tipo_options[0],
        )

        year_val = d.get('anio') or d.get('year', '')
        self.add_text_field(
            key='anio',
            label_text="Año de publicación",
            placeholder="Ej. 2024 (4 dígitos)",
            required=True,
            validator=self.validator_anio,
            initial_value=str(year_val) if year_val else "",
        )

        # --- Sección 2: Afiliación y Validación ---
        self.add_section("Afiliación y validación")

        # Combo de Grupo asociado ("código - nombre")
        options, mapping, reverse_mapping = self.get_grupos_combo_data()
        current_group_val = d.get('grupo_id') or d.get('group', None)
        initial_combo_val = None
        if current_group_val is not None:
            initial_combo_val = reverse_mapping.get(current_group_val) or reverse_mapping.get(str(current_group_val))

        self.add_combo_field(
            key='grupo_id',
            label_text="Grupo de investigación asociado",
            options=options,
            required=True,
            initial_value=initial_combo_val,
            mapping=mapping,
            reverse_mapping=reverse_mapping,
        )

        cat_val = d.get('categoria') or d.get('category', '')
        self.add_text_field(
            key='categoria',
            label_text="Categoría o indexación",
            placeholder="Ej. A1, B, C, Software registrado (opcional)",
            required=False,
            initial_value=str(cat_val),
        )

        active_val = d.get('validado', d.get('active', True))
        self.add_checkbox_field(
            key='validado',
            label_text="Producto validado y activo",
            initial_value=bool(active_val),
        )

    def get_data(self) -> Dict[str, Any]:
        """Extrae el diccionario normalizado con alias para el CRUD."""
        raw = super().get_data()
        titulo = raw.get('titulo', '').strip()
        tipo = raw.get('tipo', '').strip()
        grupo_id = raw.get('grupo_id')
        categoria = raw.get('categoria', '').strip()
        validado = bool(raw.get('validado', True))

        try:
            anio = int(raw.get('anio', 0) or 0)
        except (ValueError, TypeError):
            anio = 0

        return {
            'title': titulo,
            'titulo': titulo,
            'type': tipo,
            'tipo': tipo,
            'year': anio,
            'anio': anio,
            'group': grupo_id,
            'grupo_id': grupo_id,
            'category': categoria,
            'categoria': categoria,
            'active': validado,
            'validado': validado,
        }