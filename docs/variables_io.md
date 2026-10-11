# Variables de Entrada y Salida

Documento generado a partir de los modelos `Grupo`, `Investigador`, `Producto` y la pantalla `Estadísticas`. No se incluyen campos que no existan como atributos del modelo o variables calculadas reales de la vista.

## Grupo

| Variable | Tipo | Entrada/Salida/Calculada | Obligatoria | Descripción | Validación |
|---|---|---|---|---|---|
| `id` | `Any` | Entrada/Salida | No | Identificador interno del grupo. | Sin validación explícita en el modelo. |
| `codigo_gruplac` | `str` | Entrada/Salida | No | Código GrupLAC del grupo. | Valor por defecto `""`; `from_dict()` puede leerlo desde `codigo_gruplac` o `code`. |
| `nombre` | `str` | Entrada/Salida | No | Nombre del grupo de investigación. | Valor por defecto `""`; `from_dict()` puede leerlo desde `nombre` o `name`. |
| `categoria` | `str` | Entrada/Salida | No | Categoría del grupo. | Valor por defecto `""`; `from_dict()` puede leerlo desde `categoria` o `category`. |
| `lider` | `str` | Entrada/Salida | No | Líder del grupo. | Valor por defecto `""`; `from_dict()` puede leerlo desde `lider` o `leader`. |
| `activo` | `bool` | Entrada/Salida | No | Estado activo/inactivo del grupo. | Valor por defecto `True`; `from_dict()` puede leerlo desde `activo` o `active`. |
| `fecha_creacion` | `str` | Entrada/Salida | No | Fecha de creación registrada para el grupo. | Valor por defecto `""`. |
| `plan` | `str` | Entrada/Salida | No | Plan de trabajo o descripción del plan del grupo. | Si llega vacío o `None`, se guarda como `""`. |

## Investigador

| Variable | Tipo | Entrada/Salida/Calculada | Obligatoria | Descripción | Validación |
|---|---|---|---|---|---|
| `id` | `Any` | Entrada/Salida | No | Identificador interno del investigador. | Sin validación explícita en el modelo. |
| `cedula` | `str` | Entrada/Salida | No | Identificación o cédula del investigador. | Valor por defecto `""`. |
| `nombres` | `str` | Entrada/Salida | No | Nombres del investigador. | Valor por defecto `""`. |
| `apellidos` | `str` | Entrada/Salida | No | Apellidos del investigador. | Valor por defecto `""`. |
| `email` | `str` | Entrada/Salida | No | Correo electrónico del investigador. | Valor por defecto `""`; sin validación de formato en el modelo. |
| `activo` | `bool` | Entrada/Salida | No | Estado activo/inactivo del investigador. | Valor por defecto `True`. |
| `grupo_id` | `Any` | Entrada/Salida | No | Identificador del grupo al que pertenece el investigador. | Valor por defecto `None`; sin validación de existencia en el modelo. |

## Producto

| Variable | Tipo | Entrada/Salida/Calculada | Obligatoria | Descripción | Validación |
|---|---|---|---|---|---|
| `id` | `Any` | Entrada/Salida | No | Identificador interno del producto. | Sin validación explícita en el modelo. |
| `titulo` | `str` | Entrada/Salida | No | Título del producto de investigación. | Valor por defecto `""`; `from_dict()` puede leerlo desde `titulo` o `title`. |
| `tipo` | `str` | Entrada/Salida | No | Tipo o subcategoría del producto. | Valor por defecto `""`; `from_dict()` puede leerlo desde `tipo` o `type`. |
| `categoria` | `str` | Entrada/Salida | No | Categoría de producto normalizada. | Debe pertenecer a `Producto.CATEGORIAS`; si no, se usa `"Nuevo conocimiento"`. |
| `validado` | `bool` | Entrada/Salida | No | Bandera booleana de validación/actividad del producto. | Valor por defecto `False`; `from_dict()` puede leerlo desde `validado` o `active`. |
| `anio` | `int` | Entrada/Salida | No | Año asociado al producto. | Valor por defecto `0`; `from_dict()` puede leerlo desde `anio` o `year`. |
| `investigador_id` | `Any` | Entrada/Salida | No | Identificador del investigador asociado. | Valor por defecto `None`; sin validación de existencia en el modelo. |
| `grupo_id` | `Any` | Entrada/Salida | No | Identificador del grupo asociado. | Valor por defecto `None`; `from_dict()` puede leerlo desde `grupo_id` o `group`. |
| `raw` | `Any` | Entrada/Salida | No | Datos crudos asociados al producto. | Valor por defecto `None`; sin transformación en el modelo. |
| `gran_categoria` | `str` | Entrada/Salida | No | Gran categoría MinCiencias del producto. | Si llega vacío o `None`, se guarda como `"Sin clasificar"`. |
| `codigo_minciencias` | `str` | Entrada/Salida | No | Código MinCiencias del producto. | Si llega vacío o `None`, se guarda como `""`. |
| `categoria_producto` | `str` | Entrada/Salida | No | Alias de salida para la misma categoría normalizada guardada en `categoria`. | Se guarda con el mismo valor final de `categoria`; debe pertenecer a `Producto.CATEGORIAS` o cae en `"Nuevo conocimiento"`. |
| `validacion` | `str` | Entrada/Salida | No | Estado textual de validación del producto. | Debe pertenecer a `["Validado", "No validado", "En revisión"]`; si no, se usa `"No validado"`. |

Valores válidos de `Producto.CATEGORIAS`:

| Valor |
|---|
| `Nuevo conocimiento` |
| `Desarrollo tecnológico` |
| `Apropiación social del conocimiento` |
| `Formación de recurso humano` |

Valores válidos de `Producto.VALIDACIONES`:

| Valor |
|---|
| `Validado` |
| `No validado` |
| `En revisión` |

## Estadísticas: Entradas Comunes

| Variable | Tipo | Entrada/Salida/Calculada | Obligatoria | Descripción | Validación |
|---|---|---|---|---|---|
| `_view_mode` | `str` | Entrada | Sí | Vista activa de estadísticas. | Valores usados por la UI: `"Global"`, `"Por grupo"`, `"Por investigador"`. |
| `_selected_target_id` | `Optional[str]` | Entrada | No | Identificador de grupo o investigador seleccionado en el segundo combo. | `None` cuando la vista es global o cuando se elige el total de entidades. |
| `_target_choices` | `Dict[str, str]` | Calculada | No | Mapa interno entre etiqueta visible del combo de entidad e identificador real. | En vista por grupo se llena con grupos; en vista por investigador se llena con investigadores. |
| `_year_seg` | `str` | Entrada | Sí | Filtro de periodo seleccionado. | Valores usados por la UI: `"Todos"`, `"Últimos 2"`, `"Últimos 5"`, `"Personalizado"`. |
| `_from_entry` | `str` | Entrada | No | Año inicial del filtro personalizado. | Se intenta convertir a `int`; si no es válido, se ignora ese límite. |
| `_to_entry` | `str` | Entrada | No | Año final del filtro personalizado. | Se intenta convertir a `int`; si no es válido, se ignora ese límite. |
| `all_grupos` | `List[Grupo]` | Entrada | Sí | Grupos disponibles desde la aplicación. | Se obtiene desde multilista o CRUD. |
| `all_investigadores` | `List[Investigador]` | Entrada | Sí | Investigadores disponibles desde la aplicación. | Se obtiene desde multilista o CRUD. |
| `all_productos` | `List[Producto]` | Entrada | Sí | Productos disponibles desde la aplicación. | Se obtiene desde multilista o CRUD. |

## Estadísticas: Vista Global

| Variable | Tipo | Entrada/Salida/Calculada | Obligatoria | Descripción | Validación |
|---|---|---|---|---|---|
| `_view_mode = "Global"` | `str` | Entrada | Sí | Activa estadísticas sobre el conjunto general. | No usa entidad seleccionada. |
| `_selected_target_id` | `None` | Entrada | No | No aplica entidad específica. | Se limpia al cambiar a vista global. |
| `filtered_prods` | `List[Producto]` | Calculada | Sí | Productos válidos después de aplicar validación y filtro de años. | Excluye productos donde `_is_validated(producto)` sea falso. |
| `scoped_grupos` | `List[Grupo]` | Calculada | Sí | Grupos considerados para las tarjetas. | Con periodo `"Todos"` conserva todos los grupos; con filtro de años conserva grupos con productos filtrados. |
| `scoped_investigadores` | `List[Investigador]` | Calculada | Sí | Investigadores considerados para las tarjetas. | Con periodo `"Todos"` conserva todos los investigadores; con filtro de años conserva investigadores con productos filtrados. |
| `tot_g` | `int` | Salida | Sí | Total de grupos mostrados en tarjeta. | `len(scoped_grupos)`. |
| `act_g` | `int` | Salida | Sí | Total de grupos activos mostrado como variación. | Cuenta grupos donde `_is_active(grupo)` sea verdadero. |
| `tot_i` | `int` | Salida | Sí | Total de investigadores mostrado en tarjeta. | `len(scoped_investigadores)`. |
| `act_i` | `int` | Salida | Sí | Total de investigadores activos mostrado como variación. | Cuenta investigadores donde `_is_active(investigador)` sea verdadero. |
| `tot_p` | `int` | Salida | Sí | Total de productos mostrado en tarjeta. | `len(filtered_prods)`. |
| `act_p` | `int` | Salida | Sí | Total de productos validados mostrado como variación. | Cuenta productos donde `_is_validated(producto)` sea verdadero. |
| `total` | `int` | Salida | Sí | Total de productos del resumen descriptivo. | `len(productos)` dentro de `_update_descriptive_summary()`. |
| `promedio` | `float` | Salida | Sí | Promedio de productos por clave de investigador/producto. | Se calcula con `pd.Series(...).value_counts().mean()`; si no hay datos, `0.0`. |
| `mediana` | `float` | Salida | Sí | Mediana de productos por clave de investigador/producto. | Se calcula con `median()`; si no hay datos, `0.0`. |
| `min` | `int` | Salida | Sí | Mínimo de productos por clave de investigador/producto. | Se calcula con `min()`; si no hay datos, `0`. |
| `max` | `int` | Salida | Sí | Máximo de productos por clave de investigador/producto. | Se calcula con `max()`; si no hay datos, `0`. |
| `years_cnt` | `Counter[int]` | Salida | No | Datos para barra `Productos por año`. | Cuenta `anio` mayor a `1900`. |
| `cat_cnt` de gran categoría | `Dict[str, int]` | Salida | No | Datos para barra `Productos por gran categoría`. | Claves fijas: `GNC`, `DTI`, `ASC`, `FRH`; puede inferirse desde taxonomía por `tipo`. |
| `sub_cnt` | `Counter[str]` | Salida | No | Datos para barra horizontal `Productos por subcategoría (top 10)`. | Cuenta `tipo` no vacío. |
| `cat_cnt` de categoría | `Counter[str]` | Salida | No | Datos para barra `Productos por categoría`. | Omite categorías vacías, `"sin categoría"`, `"sin categoria"` y `"ninguna"`. |
| `inv_cnt` / `values` | `Counter[str]` / `List[int]` | Salida | No | Datos para histograma `Productos por investigador`. | Agrupa por identificador de investigador; si falta usa `"Sin investigador"`. |

## Estadísticas: Vista Por Grupo

| Variable | Tipo | Entrada/Salida/Calculada | Obligatoria | Descripción | Validación |
|---|---|---|---|---|---|
| `_view_mode = "Por grupo"` | `str` | Entrada | Sí | Activa estadísticas por grupo. | Habilita el segundo combo con grupos. |
| `_selected_target_id` | `Optional[str]` | Entrada | No | Identificador del grupo seleccionado. | Si es `None`, se calculan todos los grupos bajo la vista por grupo. |
| `_target_choices` | `Dict[str, str]` | Calculada | Sí | Opciones visibles del combo de grupo. | Incluye `"Todos los grupos": ""`; cada grupo usa `_group_id(grupo)`. |
| `filtered_prods` | `List[Producto]` | Calculada | Sí | Productos validados y filtrados por grupo seleccionado y periodo. | Si hay grupo seleccionado, exige `_product_group_id(producto) == _selected_target_id`. |
| `scoped_grupos` | `List[Grupo]` | Calculada | Sí | Grupos considerados para las tarjetas. | Si hay grupo seleccionado, conserva solo el grupo con `_group_id(grupo) == _selected_target_id`; con filtro de años además exige productos filtrados. |
| `scoped_investigadores` | `List[Investigador]` | Calculada | Sí | Investigadores considerados para las tarjetas. | Si hay grupo seleccionado, conserva investigadores con `_investigator_group_id(investigador) == _selected_target_id`; con filtro de años además exige productos filtrados. |
| `tot_g`, `act_g`, `tot_i`, `act_i`, `tot_p`, `act_p` | `int` | Salida | Sí | Tarjetas de grupos, investigadores y producción para el grupo o conjunto seleccionado. | Se calculan igual que en vista global, pero sobre el alcance de grupo. |
| `total`, `promedio`, `mediana`, `min`, `max` | `int` / `float` | Salida | Sí | Resumen descriptivo de productividad del grupo o grupos seleccionados. | Se calcula con `value_counts()` sobre claves de investigador/producto; si no hay datos, usa ceros. |
| `years_cnt`, `cat_cnt`, `sub_cnt`, `inv_cnt` | `Counter` / `Dict` | Salida | No | Datos de gráficas después de aplicar grupo y periodo. | Misma validación que en vista global, con alcance filtrado por grupo. |

## Estadísticas: Vista Por Investigador

| Variable | Tipo | Entrada/Salida/Calculada | Obligatoria | Descripción | Validación |
|---|---|---|---|---|---|
| `_view_mode = "Por investigador"` | `str` | Entrada | Sí | Activa estadísticas por investigador. | Habilita el segundo combo con investigadores. |
| `_selected_target_id` | `Optional[str]` | Entrada | No | Identificador del investigador seleccionado. | Si es `None`, se calculan todos los investigadores bajo la vista por investigador. |
| `_target_choices` | `Dict[str, str]` | Calculada | Sí | Opciones visibles del combo de investigador. | Incluye `"Todos los investigadores": ""`; cada investigador usa `_investigator_id(investigador)`. |
| `filtered_prods` | `List[Producto]` | Calculada | Sí | Productos validados y filtrados por investigador seleccionado y periodo. | Si hay investigador seleccionado, exige `_product_investigator_id(producto) == _selected_target_id`. |
| `scoped_investigadores` | `List[Investigador]` | Calculada | Sí | Investigadores considerados para las tarjetas. | Si hay investigador seleccionado, conserva solo el investigador con `_investigator_id(investigador) == _selected_target_id`; con filtro de años además exige productos filtrados. |
| `scoped_grupos` | `List[Grupo]` | Calculada | Sí | Grupos relacionados con el investigador o sus productos filtrados. | Se toma desde `_investigator_group_id(investigador)` y `_product_group_id(producto)`. |
| `tot_g`, `act_g`, `tot_i`, `act_i`, `tot_p`, `act_p` | `int` | Salida | Sí | Tarjetas de grupos, investigadores y producción para el investigador o conjunto seleccionado. | Se calculan igual que en vista global, pero sobre el alcance de investigador. |
| `total`, `promedio`, `mediana`, `min`, `max` | `int` / `float` | Salida | Sí | Resumen descriptivo de productividad del investigador o investigadores seleccionados. | En esta vista `value_counts()` agrupa por `tipo` del producto; si no hay datos, usa ceros. |
| `years_cnt` | `Counter[int]` | Salida | No | Datos para barra `Productos por año`. | Cuenta `anio` mayor a `1900` en productos filtrados. |
| `cat_cnt` de gran categoría | `Dict[str, int]` | Salida | No | Datos para barra `Productos por gran categoría`. | Claves fijas: `GNC`, `DTI`, `ASC`, `FRH`. |
| `sub_cnt` | `Counter[str]` | Salida | No | Datos para barra horizontal `Productos por subcategoría (top 10)`. | Cuenta `tipo` no vacío. |
| `cat_cnt` de categoría | `Counter[str]` | Salida | No | Datos para barra `Productos por categoría`. | Omite categorías vacías o equivalentes a ninguna. |
| `inv_cnt` / `values` | `Counter[str]` / `List[int]` | Salida | No | Datos para histograma `Productos por investigador`. | En investigador único normalmente produce una lista con un conteo; en todos los investigadores agrupa por cada identificador. |

