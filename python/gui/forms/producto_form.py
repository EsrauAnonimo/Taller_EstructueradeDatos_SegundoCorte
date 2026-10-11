# -*- coding: utf-8 -*-
"""Formulario modal para creación y edición de Producto de Investigación."""

from typing import Optional, Dict, Any, Callable
from gui.forms.base_form import FormularioBase
from entidades.taxonomia_minciencias import (
    get_gran_categorias,
    get_subcategorias,
    get_by_nombre,
    GRAN_CATEGORIAS_INFO,
)


class ProductoForm(FormularioBase):
    """Modal para captura y modificación de atributos de Producto de Investigación."""

    GRAN_CAT_OPCIONES = [
        "GNC - Generación de Nuevo Conocimiento",
        "DTI - Desarrollo Tecnológico e Innovación",
        "ASC - Apropiación Social del Conocimiento y Divulgación Pública",
        "FRH - Formación de Recurso Humano para la CTeI",
    ]

    GRAN_CAT_MAPPING = {
        "GNC - Generación de Nuevo Conocimiento": "GNC",
        "DTI - Desarrollo Tecnológico e Innovación": "DTI",
        "ASC - Apropiación Social del Conocimiento y Divulgación Pública": "ASC",
        "FRH - Formación de Recurso Humano para la CTeI": "FRH",
        "GNC": "GNC",
        "DTI": "DTI",
        "ASC": "ASC",
        "FRH": "FRH",
    }

    GRAN_CAT_REVERSE = {
        "GNC": "GNC - Generación de Nuevo Conocimiento",
        "DTI": "DTI - Desarrollo Tecnológico e Innovación",
        "ASC": "ASC - Apropiación Social del Conocimiento y Divulgación Pública",
        "FRH": "FRH - Formación de Recurso Humano para la CTeI",
    }

    CATEGORIAS_OPCIONES = [
        "Sin categoría",
        "A1",
        "A2",
        "B",
        "C",
        "D",
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
            width=540,
            height=700,
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

        # 1. Gran Categoría (GNC, DTI, ASC, FRH)
        gran_val = d.get('gran_categoria') or d.get('gran_cat', '')
        type_val = d.get('tipo') or d.get('type', '')

        # Si no tiene gran categoría o está sin clasificar, inferir si el tipo coincide con taxonomía
        if (not gran_val or gran_val == "Sin clasificar") and type_val:
            sub_match = get_by_nombre(type_val)
            if sub_match:
                gran_val = sub_match.get('gran_categoria', '')

        gc_options = list(self.GRAN_CAT_OPCIONES)
        gc_mapping = dict(self.GRAN_CAT_MAPPING)
        gc_reverse = dict(self.GRAN_CAT_REVERSE)

        if gran_val == "Sin clasificar":
            gc_options.insert(0, "Sin clasificar")
            gc_mapping["Sin clasificar"] = "Sin clasificar"
            gc_reverse["Sin clasificar"] = "Sin clasificar"
            initial_gc_display = "Sin clasificar"
        elif gran_val in self.GRAN_CAT_REVERSE:
            initial_gc_display = self.GRAN_CAT_REVERSE[gran_val]
        else:
            initial_gc_display = self.GRAN_CAT_OPCIONES[0]
            gran_val = "GNC"

        gc_widget = self.add_combo_field(
            key='gran_categoria',
            label_text="Gran categoría (MinCiencias)",
            options=gc_options,
            required=True,
            initial_value=initial_gc_display,
            mapping=gc_mapping,
            reverse_mapping=gc_reverse,
        )

        # 2. Subcategoría dinámica dependiente de Gran Categoría
        actual_gc = gc_mapping.get(initial_gc_display, "GNC")
        subcategorias = get_subcategorias(actual_gc)
        subcat_options = [s["nombre"] for s in subcategorias] if subcategorias else []

        if type_val and type_val not in subcat_options:
            subcat_options.insert(0, str(type_val))

        initial_subcat = str(type_val) if type_val else (subcat_options[0] if subcat_options else "")

        self.add_combo_field(
            key='tipo',
            label_text="Subcategoría de producto",
            options=subcat_options,
            required=True,
            initial_value=initial_subcat,
        )

        # Conectar callback para actualización dinámica al cambiar Gran Categoría
        gc_widget.configure(command=self._on_gran_categoria_changed)

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

        # Combo de Categoría (A1, A2, B, C, D)
        cat_val = d.get('categoria') or d.get('category', '')
        cat_options = list(self.CATEGORIAS_OPCIONES)
        if cat_val and cat_val not in cat_options:
            cat_options.append(str(cat_val))

        cat_mapping = {"Sin categoría": ""}
        for c in ["A1", "A2", "B", "C", "D"]:
            cat_mapping[c] = c
        if cat_val and cat_val not in cat_mapping:
            cat_mapping[cat_val] = cat_val

        initial_cat = str(cat_val) if cat_val in cat_options else ("Sin categoría" if not cat_val else cat_val)

        self.add_combo_field(
            key='categoria',
            label_text="Categoría o indexación (A1, A2, B, C, D)",
            options=cat_options,
            required=False,
            initial_value=initial_cat,
            mapping=cat_mapping,
        )

        active_val = d.get('validado', d.get('active', True))
        self.add_checkbox_field(
            key='validado',
            label_text="Producto validado y activo",
            initial_value=bool(active_val),
        )

    def _on_gran_categoria_changed(self, selected_display: str):
        """Actualiza dinámicamente las opciones de subcategoría al cambiar la gran categoría."""
        self.clear_error('gran_categoria')
        gc_key = self.GRAN_CAT_MAPPING.get(selected_display, selected_display)
        subs = get_subcategorias(gc_key)
        new_options = [s["nombre"] for s in subs] if subs else ["(Sin subcategorías)"]

        tipo_field = self._fields.get('tipo')
        if tipo_field:
            tipo_widget = tipo_field['widget']
            tipo_var = tipo_field['var']
            tipo_widget.configure(values=new_options)
            tipo_var.set(new_options[0])
            self.clear_error('tipo')

    def get_data(self) -> Dict[str, Any]:
        """Extrae el diccionario normalizado con alias para el CRUD."""
        raw = super().get_data()
        titulo = raw.get('titulo', '').strip()
        tipo = raw.get('tipo', '').strip()
        gran_cat_raw = raw.get('gran_categoria', '').strip()
        gran_categoria = self.GRAN_CAT_MAPPING.get(gran_cat_raw, gran_cat_raw) or "Sin clasificar"
        grupo_id = raw.get('grupo_id')
        categoria = raw.get('categoria', '').strip()
        validado = bool(raw.get('validado', True))

        # Determinar el código MinCiencias a partir de la subcategoría seleccionada
        sub_info = get_by_nombre(tipo)
        if sub_info:
            codigo_minciencias = sub_info.get('codigo', '')
            if not gran_categoria or gran_categoria == "Sin clasificar":
                gran_categoria = sub_info.get('gran_categoria', 'Sin clasificar')
        else:
            codigo_minciencias = self._initial_data.get('codigo_minciencias', '')

        try:
            anio = int(raw.get('anio', 0) or 0)
        except (ValueError, TypeError):
            anio = 0

        return {
            'title': titulo,
            'titulo': titulo,
            'type': tipo,
            'tipo': tipo,
            'gran_categoria': gran_categoria,
            'codigo_minciencias': codigo_minciencias,
            'year': anio,
            'anio': anio,
            'group': grupo_id,
            'grupo_id': grupo_id,
            'category': categoria,
            'categoria': categoria,
            'active': validado,
            'validado': validado,
        }