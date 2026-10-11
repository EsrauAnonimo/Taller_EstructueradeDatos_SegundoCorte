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

    # Nuevos campos
    from entidades.producto import Producto as _P
    CATEGORIAS_PRODUCTO_OPCIONES = _P.CATEGORIAS_PRODUCTO
    VALIDACION_OPCIONES = _P.VALIDACIONES

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

        # --- Sección 2: Afiliación institucional ---
        self.add_section("Afiliación institucional")

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

        # Combo de Investigador asociado ("cédula - nombres apellidos")
        inv_options, inv_mapping, inv_reverse = self.get_investigadores_combo_data()
        current_inv_val = d.get('investigador_id') or d.get('investigador_cedula', None)
        initial_inv_combo_val = None
        if current_inv_val is not None:
            initial_inv_combo_val = inv_reverse.get(current_inv_val) or inv_reverse.get(str(current_inv_val))

        self.add_combo_field(
            key='investigador_id',
            label_text="Investigador asociado",
            options=inv_options,
            required=True,
            initial_value=initial_inv_combo_val,
            mapping=inv_mapping,
            reverse_mapping=inv_reverse,
        )

        active_val = d.get('validado', d.get('active', True))
        self.add_checkbox_field(
            key='validado',
            label_text="Producto validado y activo",
            initial_value=bool(active_val),
        )

        # --- Sección 3: Categoría y Validación ---
        self.add_section("Categoría y validación")

        from entidades.producto import Producto as _P
        cat_val = d.get('categoria') or d.get('categoria_producto', 'Nuevo conocimiento')
        if cat_val not in _P.CATEGORIAS:
            cat_val = 'Nuevo conocimiento'
        self.add_combo_field(
            key='categoria',
            label_text="Categoría del producto",
            options=_P.CATEGORIAS,
            required=True,
            initial_value=cat_val,
        )

        val_val = d.get('validacion', 'No validado')
        if val_val not in _P.VALIDACIONES:
            val_val = 'No validado'
        self.add_combo_field(
            key='validacion',
            label_text="Estado de validación",
            options=_P.VALIDACIONES,
            required=True,
            initial_value=val_val,
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

    def validate_all(self) -> bool:
        """Valida todos los campos. Muestra errores en rojo dentro del formulario sin cerrarlo."""
        import datetime
        current_year = datetime.datetime.now().year

        # Ejecutar validación base (required + validators por campo)
        base_ok = super().validate_all()

        # Reglas adicionales de negocio
        extra_ok = True
        app = self.resolve_app()

        # 1. Título no vacío
        titulo_info = self._fields.get('titulo')
        if titulo_info:
            titulo_val = titulo_info['widget'].get().strip()
            if not titulo_val:
                self.set_error('titulo', "El título no puede estar vacío.")
                extra_ok = False

        # 2. Año entre 1900 y año actual
        anio_info = self._fields.get('anio')
        if anio_info:
            anio_val = anio_info['widget'].get().strip()
            if not anio_val:
                self.set_error('anio', "El año de publicación es obligatorio.")
                extra_ok = False
            elif not anio_val.isdigit():
                self.set_error('anio', "El año debe contener únicamente dígitos numéricos.")
                extra_ok = False
            else:
                year_int = int(anio_val)
                if year_int < 1900 or year_int > current_year:
                    self.set_error('anio', f"El año debe estar entre 1900 y {current_year}.")
                    extra_ok = False

        # 3. Tipo obligatorio (subcategoría)
        tipo_info = self._fields.get('tipo')
        if tipo_info:
            tipo_val = tipo_info['var'].get().strip()
            if not tipo_val or tipo_val.startswith('(Sin'):
                self.set_error('tipo', "El tipo de producto es obligatorio.")
                extra_ok = False

        # 4. Categoría obligatoria
        cat_info = self._fields.get('categoria')
        if cat_info:
            cval = cat_info['var'].get().strip()
            from entidades.producto import Producto as _P
            if not cval or cval not in _P.CATEGORIAS:
                self.set_error('categoria', "La categoría es obligatoria.")
                extra_ok = False

        # 5. Validación obligatoria
        val_info = self._fields.get('validacion')
        if val_info:
            vval = val_info['var'].get().strip()
            from entidades.producto import Producto as _P
            if not vval or vval not in _P.VALIDACIONES:
                self.set_error('validacion', "El estado de validación es obligatorio.")
                extra_ok = False

        # 6. Grupo existente (no placeholder)
        grupo_info = self._fields.get('grupo_id')
        if grupo_info:
            gval = grupo_info['var'].get().strip()
            gmapping = grupo_info.get('mapping', {})
            gid = gmapping.get(gval)
            if gid is None or gval.startswith('(Sin'):
                self.set_error('grupo_id', "Selecciona un grupo de investigación existente.")
                extra_ok = False
            elif app and hasattr(app, 'grupo_crud'):
                try:
                    found = app.grupo_crud.get_by_id(gid)
                    if found is None:
                        self.set_error('grupo_id', "El grupo seleccionado no existe en el sistema.")
                        extra_ok = False
                except Exception:
                    pass

        # 7. Investigador existente (no placeholder)
        inv_info = self._fields.get('investigador_id')
        if inv_info:
            ival = inv_info['var'].get().strip()
            imapping = inv_info.get('mapping', {})
            iid = imapping.get(ival)
            if iid is None or ival.startswith('(Sin'):
                self.set_error('investigador_id', "Selecciona un investigador existente.")
                extra_ok = False
            elif app and hasattr(app, 'inv_crud'):
                try:
                    found = app.inv_crud.get_by_cedula(str(iid))
                    if found is None:
                        self.set_error('investigador_id', "El investigador seleccionado no existe en el sistema.")
                        extra_ok = False
                except Exception:
                    pass

        return base_ok and extra_ok

    def get_data(self) -> dict:
        """Extrae el diccionario normalizado con alias para el CRUD."""
        raw = super().get_data()
        titulo = raw.get('titulo', '').strip()
        tipo = raw.get('tipo', '').strip()
        gran_cat_raw = raw.get('gran_categoria', '').strip()
        gran_categoria = self.GRAN_CAT_MAPPING.get(gran_cat_raw, gran_cat_raw) or "Sin clasificar"
        grupo_id = raw.get('grupo_id')
        investigador_id = raw.get('investigador_id')
        categoria = raw.get('categoria', 'Nuevo conocimiento')
        validacion = raw.get('validacion', 'No validado')
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
            'investigador_id': investigador_id,
            'investigador_cedula': investigador_id,
            'category': categoria,
            'categoria': categoria,
            'categoria_producto': categoria,
            'validacion': validacion,
            'active': validado,
            'validado': validado,
        }