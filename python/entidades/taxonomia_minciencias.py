# -*- coding: utf-8 -*-
"""Taxonomía de productos de investigación MinCiencias 2024.

Define las 4 grandes categorías y sus correspondientes subcategorías
según el modelo de medición y reconocimiento de MinCiencias Colombia.
"""

from typing import List, Dict, Any, Optional

# Nombres descriptivos de las 4 grandes categorías
GRAN_CATEGORIAS_INFO: Dict[str, str] = {
    "GNC": "Generación de Nuevo Conocimiento",
    "DTI": "Desarrollo Tecnológico e Innovación",
    "ASC": "Apropiación Social del Conocimiento y Divulgación Pública",
    "FRH": "Formación de Recurso Humano para la CTeI",
}

# Diccionario principal de taxonomía por gran categoría
TAXONOMIA: Dict[str, List[Dict[str, str]]] = {
    "GNC": [
        {
            "codigo": "2.2.1.1",
            "nombre": "Artículos de investigación (A1, A2, B y C)",
            "gran_categoria": "GNC",
        },
        {
            "codigo": "2.2.1.1",
            "nombre": "Artículos de investigación (D)",
            "gran_categoria": "GNC",
        },
        {
            "codigo": "2.2.1.2",
            "nombre": "Notas científicas",
            "gran_categoria": "GNC",
        },
        {
            "codigo": "2.2.1.3",
            "nombre": "Libros resultados de investigación",
            "gran_categoria": "GNC",
        },
        {
            "codigo": "2.2.1.4",
            "nombre": "Capítulos en libro resultado de investigación",
            "gran_categoria": "GNC",
        },
        {
            "codigo": "2.2.3.4.3.1",
            "nombre": "Libros de Formación Q1",
            "gran_categoria": "GNC",
        },
        {
            "codigo": "2.2.1.5",
            "nombre": "Productos tecnológicos patentados o en solicitud",
            "gran_categoria": "GNC",
        },
        {
            "codigo": "2.2.1.6",
            "nombre": "Variedades vegetales, nuevas razas animales y pecuarias",
            "gran_categoria": "GNC",
        },
        {
            "codigo": "2.2.1.7",
            "nombre": "Productos resultados de la creación / investigación-creación",
            "gran_categoria": "GNC",
        },
    ],
    "DTI": [
        {
            "codigo": "2.2.2.1",
            "nombre": "Productos tecnológicos certificados o validados",
            "gran_categoria": "DTI",
        },
        {
            "codigo": "2.2.2.2",
            "nombre": "Productos empresariales (Spin-off, Start-up, etc.)",
            "gran_categoria": "DTI",
        },
        {
            "codigo": "2.2.2.3",
            "nombre": "Regulaciones, normas, reglamentos o legislaciones",
            "gran_categoria": "DTI",
        },
        {
            "codigo": "2.2.2.4",
            "nombre": "Conceptos técnicos",
            "gran_categoria": "DTI",
        },
        {
            "codigo": "2.2.2.5",
            "nombre": "Registros de Licencias para explotación de obras",
            "gran_categoria": "DTI",
        },
    ],
    "ASC": [
        {
            "codigo": "2.2.3.3.1",
            "nombre": "Procesos de Apropiación Social del Conocimiento",
            "gran_categoria": "ASC",
        },
        {
            "codigo": "2.2.3.4.1",
            "nombre": "Circulación de conocimiento especializado",
            "gran_categoria": "ASC",
        },
        {
            "codigo": "2.2.3.4.2",
            "nombre": "Divulgación Pública de la CTeI (Transmedia, Web)",
            "gran_categoria": "ASC",
        },
        {
            "codigo": "2.2.3.4.3",
            "nombre": "Producción Bibliográfica (Libros divulgación, manuales, etc.)",
            "gran_categoria": "ASC",
        },
    ],
    "FRH": [
        {
            "codigo": "2.2.4.1",
            "nombre": "Direcciones de Tesis de doctorado",
            "gran_categoria": "FRH",
        },
        {
            "codigo": "2.2.4.2",
            "nombre": "Direcciones de Trabajo de grado de maestría",
            "gran_categoria": "FRH",
        },
        {
            "codigo": "2.2.4.3",
            "nombre": "Direcciones de Trabajo de grado de pregrado",
            "gran_categoria": "FRH",
        },
        {
            "codigo": "2.2.4.4",
            "nombre": "Proyectos de Investigación y Desarrollo",
            "gran_categoria": "FRH",
        },
        {
            "codigo": "2.2.4.4",
            "nombre": "Proyectos de Investigación-Creación",
            "gran_categoria": "FRH",
        },
        {
            "codigo": "2.2.4.4",
            "nombre": "Proyectos de Investigación, Desarrollo e Innovación (I+D+i)",
            "gran_categoria": "FRH",
        },
        {
            "codigo": "2.2.4.5",
            "nombre": "Proyectos de extensión y responsabilidad social en CTeI",
            "gran_categoria": "FRH",
        },
        {
            "codigo": "2.2.4.6",
            "nombre": "Apoyos a creación de programas/cursos de posgrado",
            "gran_categoria": "FRH",
        },
        {
            "codigo": "2.2.4.7",
            "nombre": "Asesorías de línea temática del Programa Ondas",
            "gran_categoria": "FRH",
        },
    ],
}


def get_gran_categorias() -> List[str]:
    """Retorna la lista de las 4 grandes categorías de MinCiencias (GNC, DTI, ASC, FRH)."""
    return list(TAXONOMIA.keys())


def get_subcategorias(gran_categoria: str) -> List[Dict[str, str]]:
    """Retorna la lista de subcategorías correspondientes a una gran categoría.

    Acepta tanto la sigla ('GNC', 'DTI', 'ASC', 'FRH') como nombres descriptivos.
    """
    if not gran_categoria:
        return []

    clean_key = str(gran_categoria).strip()
    if clean_key in TAXONOMIA:
        return [dict(item) for item in TAXONOMIA[clean_key]]

    # Búsqueda por coincidencia de sigla en el texto
    for key in TAXONOMIA:
        if key in clean_key:
            return [dict(item) for item in TAXONOMIA[key]]

    return []


def get_by_codigo(codigo: str) -> Optional[Dict[str, str]]:
    """Retorna el primer diccionario de subcategoría que coincida con el código indicado."""
    if not codigo:
        return None

    cod_clean = str(codigo).strip()
    for subcategorias in TAXONOMIA.values():
        for sub in subcategorias:
            if sub["codigo"] == cod_clean:
                return dict(sub)
    return None


def get_by_nombre(nombre: str) -> Optional[Dict[str, str]]:
    """Retorna el diccionario de subcategoría que coincida con el nombre indicado."""
    if not nombre:
        return None

    nom_clean = str(nombre).strip().lower()
    for subcategorias in TAXONOMIA.values():
        for sub in subcategorias:
            if sub["nombre"].strip().lower() == nom_clean:
                return dict(sub)
    return None


def get_gran_categoria_nombre(gran_categoria: str) -> str:
    """Retorna el nombre descriptivo completo para una gran categoría dada."""
    if not gran_categoria:
        return "Sin clasificar"
    clean_key = str(gran_categoria).strip().upper()
    return GRAN_CATEGORIAS_INFO.get(clean_key, clean_key)
