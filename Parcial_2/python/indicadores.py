# -*- coding: utf-8 -*-
"""Módulo de cálculo de Indicadores de Producción Científica (Modelo MinCiencias - Parcial 2).

Implementa la fórmula institucional y de MinCiencias:
    Indicador = 3.7*Nc_Top + 2.3*Nc_A + 0.4*Nc_B + 1.5*AP + 0.5*DPC + 1*Fr_A + 0.2*Fr_B + 0.1*Cohe + 0.3*Coop

Mapeo de categorías estándar MinCiencias:
    - A1 / Top -> Nc_Top (peso: 3.7)
    - A2 / A   -> Nc_A   (peso: 2.3)
    - B        -> Nc_B   (peso: 0.4)
    - C        -> AP     (peso: 1.5)
    - Divulgación / DTI -> DPC (peso: 0.5)
    - Formación Posgrado (Doctorado/Maestría) -> Fr_A (peso: 1.0)
    - Formación Pregrado -> Fr_B (peso: 0.2)
"""

from typing import List, Dict, Any, Tuple, Optional
import re

# Pesos oficiales de la fórmula del parcial
COEFFICIENTS: Dict[str, float] = {
    "Nc_Top": 3.7,
    "Nc_A": 2.3,
    "Nc_B": 0.4,
    "AP": 1.5,
    "DPC": 0.5,
    "Fr_A": 1.0,
    "Fr_B": 0.2,
    "Cohe": 0.1,
    "Coop": 0.3,
}

# Descripciones en español para interfaz y reportes
VARIABLE_DESCRIPTIONS: Dict[str, str] = {
    "Nc_Top": "Nuevo Conocimiento Top (A1 / Patentes / Libros Q1)",
    "Nc_A": "Nuevo Conocimiento Tipo A (A2 / Artículos A)",
    "Nc_B": "Nuevo Conocimiento Tipo B (Artículos B)",
    "AP": "Apropiación Social / Artículos C / Creación",
    "DPC": "Divulgación Pública de la Ciencia / Desarrollo Tecnológico",
    "Fr_A": "Formación Posgrado (Doctorado / Maestría)",
    "Fr_B": "Formación Pregrado (Trabajos de grado)",
    "Cohe": "Cohesión interna (Coautoría grupal)",
    "Coop": "Cooperación externa (Redes e interinstitucional)",
}


def mapear_categoria_variable(categoria: str = "", tipo: str = "", gran_categoria: str = "") -> Tuple[str, float]:
    """Mapea una categoría o tipo de producto a su variable correspondiente en la fórmula.

    Args:
        categoria: Categoría asignada (ej. 'A1', 'A2', 'B', 'C', 'Nuevo conocimiento').
        tipo: Tipo específico o subcategoría MinCiencias.
        gran_categoria: Código de gran categoría ('GNC', 'DTI', 'ASC', 'FRH').

    Returns:
        Tuple[str, float]: (nombre_variable, peso_relativo).
    """
    text = f"{categoria} {tipo} {gran_categoria}".upper()

    # 1. Detección de Artículos / Productos A1 o Top
    if re.search(r'\b(A1|TOP|Q1)\b', text):
        return ("Nc_Top", COEFFICIENTS["Nc_Top"])

    # 2. Detección de Artículos / Productos A2 o A
    if re.search(r'\b(A2|A)\b', text) or "ARTICULO A" in text or "NUEVO CONOCIMIENTO" in text:
        return ("Nc_A", COEFFICIENTS["Nc_A"])

    # 3. Detección de Artículos / Productos B
    if re.search(r'\b(B)\b', text) or "ARTICULO B" in text or "CATEGORIA B" in text:
        return ("Nc_B", COEFFICIENTS["Nc_B"])

    # 4. Detección de Artículos / Productos C
    if re.search(r'\b(C)\b', text) or "ARTICULO C" in text or "CATEGORIA C" in text:
        return ("AP", COEFFICIENTS["AP"])

    # 5. Formación de Recurso Humano (FRH)
    if "DOCTORADO" in text or "MAESTR" in text or "FR_A" in text:
        return ("Fr_A", COEFFICIENTS["Fr_A"])
    if "PREGRADO" in text or "FR_B" in text:
        return ("Fr_B", COEFFICIENTS["Fr_B"])
    if "FRH" in text:
        return ("Fr_B", COEFFICIENTS["Fr_B"])

    # 6. Apropiación Social del Conocimiento (ASC)
    if "APROPIACI" in text or "ASC" in text or "CREACI" in text:
        return ("AP", COEFFICIENTS["AP"])

    # 7. Desarrollo Tecnológico e Innovación (DTI) o Divulgación (DPC)
    if "DIVULGACI" in text or "DTI" in text or "DPC" in text or "CONCEPTO" in text or "SOFTWARE" in text:
        return ("DPC", COEFFICIENTS["DPC"])

    # 8. Generación de Nuevo Conocimiento sin categoría específica
    if "GNC" in text or "NUEVO CONOCIMIENTO" in text or "LIBRO" in text:
        return ("Nc_A", COEFFICIENTS["Nc_A"])

    # Por defecto
    return ("AP", COEFFICIENTS["AP"])


def asignar_puntaje_producto(producto: Any) -> float:
    """Calcula y asigna peso_relativo y puntaje a un objeto Producto.

    Args:
        producto: Instancia de Producto.

    Returns:
        float: Puntaje calculado del producto.
    """
    cat = getattr(producto, "categoria", "")
    tipo = getattr(producto, "tipo", "")
    gran_cat = getattr(producto, "gran_categoria", "")

    var_name, weight = mapear_categoria_variable(cat, tipo, gran_cat)
    producto.peso_relativo = float(weight)

    # El puntaje refleja el peso relativo multiplicado por el estado de validación si aplica
    # Para MinCiencias, los productos validados computan al 100% de su peso
    is_valid = getattr(producto, "validado", True)
    producto.puntaje = float(weight) if is_valid else 0.0

    return producto.puntaje


def calcular_formula_indicador(
    nc_top: float = 0.0,
    nc_a: float = 0.0,
    nc_b: float = 0.0,
    ap: float = 0.0,
    dpc: float = 0.0,
    fr_a: float = 0.0,
    fr_b: float = 0.0,
    cohe: float = 0.0,
    coop: float = 0.0,
) -> float:
    """Aplica la fórmula matemática oficial:
    Indicador = 3.7*Nc_Top + 2.3*Nc_A + 0.4*Nc_B + 1.5*AP + 0.5*DPC + 1*Fr_A + 0.2*Fr_B + 0.1*Cohe + 0.3*Coop
    """
    total = (
        COEFFICIENTS["Nc_Top"] * nc_top
        + COEFFICIENTS["Nc_A"] * nc_a
        + COEFFICIENTS["Nc_B"] * nc_b
        + COEFFICIENTS["AP"] * ap
        + COEFFICIENTS["DPC"] * dpc
        + COEFFICIENTS["Fr_A"] * fr_a
        + COEFFICIENTS["Fr_B"] * fr_b
        + COEFFICIENTS["Cohe"] * cohe
        + COEFFICIENTS["Coop"] * coop
    )
    return round(total, 4)


def calcular_indicador_productos(productos: List[Any], cohe: float = 0.0, coop: float = 0.0) -> Dict[str, Any]:
    """Calcula el indicador y el desglose de métricas para una lista de productos.

    Args:
        productos: Lista de objetos Producto o diccionarios de productos.
        cohe: Valor de cohesión (default 0.0).
        coop: Valor de cooperación (default 0.0).

    Returns:
        Dict con indicador total, conteos, subtotales y detalle de la fórmula.
    """
    counts = {var: 0 for var in COEFFICIENTS.keys()}
    counts["Cohe"] = float(cohe)
    counts["Coop"] = float(coop)

    subtotals = {var: 0.0 for var in COEFFICIENTS.keys()}
    total_validados = 0

    for prod in productos:
        # Extraer atributos compatibles con objetos o dicts
        cat = getattr(prod, "categoria", "") if hasattr(prod, "categoria") else prod.get("categoria", "")
        tipo = getattr(prod, "tipo", "") if hasattr(prod, "tipo") else prod.get("tipo", "")
        gran_cat = getattr(prod, "gran_categoria", "") if hasattr(prod, "gran_categoria") else prod.get("gran_categoria", "")
        is_valid = getattr(prod, "validado", True) if hasattr(prod, "validado") else prod.get("validado", True)

        var_name, weight = mapear_categoria_variable(cat, tipo, gran_cat)

        if hasattr(prod, "peso_relativo"):
            prod.peso_relativo = float(weight)
            prod.puntaje = float(weight) if is_valid else 0.0

        if is_valid:
            total_validados += 1
            counts[var_name] += 1
            subtotals[var_name] += float(weight)

    subtotals["Cohe"] = round(counts["Cohe"] * COEFFICIENTS["Cohe"], 4)
    subtotals["Coop"] = round(counts["Coop"] * COEFFICIENTS["Coop"], 4)

    total_indicador = calcular_formula_indicador(
        nc_top=counts["Nc_Top"],
        nc_a=counts["Nc_A"],
        nc_b=counts["Nc_B"],
        ap=counts["AP"],
        dpc=counts["DPC"],
        fr_a=counts["Fr_A"],
        fr_b=counts["Fr_B"],
        cohe=counts["Cohe"],
        coop=counts["Coop"],
    )

    return {
        "indicador": total_indicador,
        "total_productos": len(productos),
        "total_validados": total_validados,
        "counts": counts,
        "subtotals": subtotals,
        "coefficients": COEFFICIENTS,
        "descriptions": VARIABLE_DESCRIPTIONS,
    }


def _filtra_anio(prod_data: Any, anio_min: Optional[int], anio_max: Optional[int]) -> bool:
    """Retorna True si el producto pasa el filtro por año."""
    if anio_min is None and anio_max is None:
        return True
    raw_year = getattr(prod_data, "anio", 0) if hasattr(prod_data, "anio") else prod_data.get("anio", 0)
    try:
        y = int(raw_year)
    except (ValueError, TypeError):
        y = 0
    if y <= 0:
        return False
    if anio_min is not None and y < anio_min:
        return False
    if anio_max is not None and y > anio_max:
        return False
    return True


def calcular_indicador_grupo(
    multilista: Any,
    group_id: Any,
    anio_min: Optional[int] = None,
    anio_max: Optional[int] = None,
) -> Dict[str, Any]:
    """Calcula el indicador de producción científica para un grupo de investigación con filtro por año opcional.

    Args:
        multilista: Instancia de Multilist de la aplicación.
        group_id: ID o código del grupo.
        anio_min: Año mínimo inclusive (opcional).
        anio_max: Año máximo inclusive (opcional).

    Returns:
        Dict con los resultados del indicador y detalles del grupo.
    """
    productos = []
    total_integrantes = 0
    group_name = ""

    # Buscar nodo de grupo
    group_node = multilista.get_group_by_id(group_id)
    if group_node is None:
        group_node = multilista.get_group_by_code(str(group_id))

    if group_node is not None:
        group_name = getattr(group_node.data, "nombre", f"Grupo {group_id}")
        inv_curr = group_node.sublist
        while inv_curr is not None:
            if inv_curr.active:
                total_integrantes += 1
                prod_curr = inv_curr.sublist
                while prod_curr is not None:
                    if prod_curr.active and _filtra_anio(prod_curr.data, anio_min, anio_max):
                        productos.append(prod_curr.data)
                    prod_curr = prod_curr.next
            inv_curr = inv_curr.next

    # Estimación de cohesión y cooperación basada en datos disponibles
    cohe = round(min(5.0, len(productos) * 0.1), 2)
    coop = round(min(5.0, len(productos) * 0.05), 2)

    res = calcular_indicador_productos(productos, cohe=cohe, coop=coop)
    res["entidad_tipo"] = "Grupo"
    res["entidad_id"] = group_id
    res["entidad_nombre"] = group_name
    res["total_integrantes"] = total_integrantes
    res["anio_min"] = anio_min
    res["anio_max"] = anio_max
    return res


def calcular_indicador_investigador(
    multilista: Any,
    investigator_id: Any,
    anio_min: Optional[int] = None,
    anio_max: Optional[int] = None,
) -> Dict[str, Any]:
    """Calcula el indicador de producción científica para un investigador con filtro por año opcional.

    Args:
        multilista: Instancia de Multilist de la aplicación.
        investigator_id: ID o cédula del investigador.
        anio_min: Año mínimo inclusive (opcional).
        anio_max: Año máximo inclusive (opcional).

    Returns:
        Dict con los resultados del indicador y detalles del investigador.
    """
    productos = []
    inv_nombre = ""
    inv_categoria = ""
    found_group = ""

    g_curr = multilista.head_group
    while g_curr is not None:
        if g_curr.active:
            inv_curr = g_curr.sublist
            while inv_curr is not None:
                iid = getattr(inv_curr.data, "id", None)
                ced = getattr(inv_curr.data, "cedula", None)
                if inv_curr.active and (str(iid) == str(investigator_id) or str(ced) == str(investigator_id)):
                    inv_nombre = getattr(inv_curr.data, "nombre", f"Investigador {investigator_id}")
                    inv_categoria = getattr(inv_curr.data, "categoria", "")
                    found_group = getattr(g_curr.data, "nombre", "")
                    prod_curr = inv_curr.sublist
                    while prod_curr is not None:
                        if prod_curr.active and _filtra_anio(prod_curr.data, anio_min, anio_max):
                            productos.append(prod_curr.data)
                        prod_curr = prod_curr.next
                inv_curr = inv_curr.next
        g_curr = g_curr.next

    res = calcular_indicador_productos(productos, cohe=0.0, coop=0.0)
    res["entidad_tipo"] = "Investigador"
    res["entidad_id"] = investigator_id
    res["entidad_nombre"] = inv_nombre
    res["categoria_investigador"] = inv_categoria
    res["grupo_nombre"] = found_group
    res["anio_min"] = anio_min
    res["anio_max"] = anio_max
    return res
