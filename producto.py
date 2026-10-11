# -*- coding: utf-8 -*-
"""Entidad Producto de investigaciÃ³n con categorizaciÃ³n MinCiencias y validaciÃ³n."""

class Producto:
    """Clase para representar un producto de investigaciÃ³n."""

    CATEGORIAS = [
        "Nuevo conocimiento",
        "Desarrollo tecnolÃ³gico",
        "ApropiaciÃ³n social del conocimiento",
        "FormaciÃ³n de recurso humano",
    ]
    CATEGORIAS_PRODUCTO = CATEGORIAS
    VALIDACIONES = ["Validado", "No validado", "En revisiÃ³n"]

    def __init__(
        self,
        id=None,
        titulo="",
        tipo="",
        categoria="Nuevo conocimiento",
        
        anio=0,
        investigador_id=None,
        grupo_id=None,
        raw=None,
        gran_categoria="Sin clasificar",
        codigo_minciencias="",
        categoria_producto=None,
        validacion="No validado",
    ):
        """Inicializa un objeto Producto."""
        self.id = id
        self.titulo = titulo
        self.tipo = tipo
                self.anio = anio
        self.investigador_id = investigador_id
        self.grupo_id = grupo_id
        self.raw = raw
        self.gran_categoria = gran_categoria if gran_categoria else "Sin clasificar"
        self.codigo_minciencias = codigo_minciencias or ""

        # Determinar categorÃ­a con valor por defecto garantizado
        cat = categoria_producto if categoria_producto in self.CATEGORIAS else (
            categoria if categoria in self.CATEGORIAS else "Nuevo conocimiento"
        )
        self.categoria = cat
        self.categoria_producto = cat

        # Determinar estado de validaciÃ³n con valor por defecto garantizado
        val = validacion if validacion in self.VALIDACIONES else "No validado"
        self.validacion = val

    def __repr__(self):
        """RepresentaciÃ³n en cadena del objeto Producto."""
        return (
            f"Producto(id={self.id}, titulo={self.titulo}, tipo={self.tipo}, "
            f"categoria={self.categoria}, validacion={self.validacion})"
        )

    def to_dict(self):
        """Convierte el objeto Producto a un diccionario."""
        return {
            "id": self.id,
            "titulo": self.titulo,
            "tipo": self.tipo,
            "categoria": self.categoria,

            "anio": self.anio,
            "investigador_id": self.investigador_id,
            "grupo_id": self.grupo_id,
            "raw": self.raw,
            "gran_categoria": self.gran_categoria,
            "codigo_minciencias": self.codigo_minciencias,
            "categoria_producto": self.categoria,
            "validacion": self.validacion,
        }

    @classmethod
    def from_dict(cls, data):
        """Crea un objeto Producto a partir de un diccionario.

        Los datos antiguos sin los campos 'categoria' o 'validacion' cargan con
        valores por defecto ('Nuevo conocimiento' y 'No validado').
        """
        if data is None:
            return None

        # Resolver categorÃ­a con valor por defecto
        cat = data.get("categoria_producto") if data.get("categoria_producto") in cls.CATEGORIAS else (
            data.get("categoria") if data.get("categoria") in cls.CATEGORIAS else "Nuevo conocimiento"
        )

        # Resolver validaciÃ³n con valor por defecto
        val = data.get("validacion") if data.get("validacion") in cls.VALIDACIONES else "No validado"

        return cls(
            id=data.get("id"),
            titulo=data.get("titulo", "") or data.get("title", ""),
            tipo=data.get("tipo", "") or data.get("type", ""),
            categoria=cat,
            validado=data.get("validado", data.get("active", False)),
            anio=data.get("anio", data.get("year", 0)),
            investigador_id=data.get("investigador_id"),
            grupo_id=data.get("grupo_id") or data.get("group"),
            raw=data.get("raw"),
            gran_categoria=data.get("gran_categoria") or "Sin clasificar",
            codigo_minciencias=data.get("codigo_minciencias", ""),
            categoria_producto=cat,
            validacion=val,
        )