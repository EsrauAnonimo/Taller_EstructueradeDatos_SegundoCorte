# -*- coding: utf-8 -*-
"""Entidad Producto de investigación con categorización MinCiencias y validación."""

class Producto:
    """Clase para representar un producto de investigación."""

    CATEGORIAS = [
        "Nuevo conocimiento",
        "Desarrollo tecnológico",
        "Apropiación social del conocimiento",
        "Formación de recurso humano",
        "A1", "A2", "A", "B", "C", "Top", "DPC", "Fr_A", "Fr_B",
    ]
    CATEGORIAS_PRODUCTO = CATEGORIAS
    VALIDACIONES = ["Validado", "No validado", "En revisión"]

    def __init__(
        self,
        id=None,
        titulo="",
        tipo="",
        categoria="Nuevo conocimiento",
        validado=False,
        anio=0,
        investigador_id=None,
        grupo_id=None,
        raw=None,
        gran_categoria="Sin clasificar",
        codigo_minciencias="",
        categoria_producto=None,
        validacion="No validado",
        peso_relativo=0.0,
        puntaje=0.0,
        activo=True,
    ):
        """Inicializa un objeto Producto."""
        self.id = id
        self.titulo = titulo
        self.tipo = tipo
        self.validado = validado
        self.activo = bool(activo)
        self.anio = anio
        self.investigador_id = investigador_id
        self.grupo_id = grupo_id
        self.raw = raw
        self.gran_categoria = gran_categoria if gran_categoria else "Sin clasificar"
        self.codigo_minciencias = codigo_minciencias or ""
        self.peso_relativo = float(peso_relativo if peso_relativo is not None else 0.0)
        self.puntaje = float(puntaje if puntaje is not None else 0.0)

        # Determinar categoría respetando categorías estándar MinCiencias
        cat = categoria_producto if (categoria_producto and categoria_producto in self.CATEGORIAS) else (
            categoria if (categoria and (categoria in self.CATEGORIAS or len(categoria) <= 6)) else "Nuevo conocimiento"
        )
        self.categoria = cat
        self.categoria_producto = cat

        # Determinar estado de validación con valor por defecto garantizado
        val = validacion if validacion in self.VALIDACIONES else ("Validado" if validado else "No validado")
        self.validacion = val
        self.validacion = val

    def __repr__(self):
        """Representación en cadena del objeto Producto."""
        return (
            f"Producto(id={self.id}, titulo={self.titulo}, tipo={self.tipo}, "
            f"categoria={self.categoria}, validacion={self.validacion}, "
            f"peso_relativo={self.peso_relativo}, puntaje={self.puntaje})"
        )

    def to_dict(self):
        """Convierte el objeto Producto a un diccionario."""
        return {
            "id": self.id,
            "titulo": self.titulo,
            "tipo": self.tipo,
            "categoria": self.categoria,
            "validado": self.validado,
            "anio": self.anio,
            "investigador_id": self.investigador_id,
            "grupo_id": self.grupo_id,
            "raw": self.raw,
            "gran_categoria": self.gran_categoria,
            "codigo_minciencias": self.codigo_minciencias,
            "categoria_producto": self.categoria,
            "validacion": self.validacion,
            "peso_relativo": self.peso_relativo,
            "puntaje": self.puntaje,
        }

    @classmethod
    def from_dict(cls, data):
        """Crea un objeto Producto a partir de un diccionario.

        Los datos antiguos sin los campos 'categoria' o 'validacion' cargan con
        valores por defecto ('Nuevo conocimiento' y 'No validado').
        """
        if data is None:
            return None

        # Resolver categoría con valor por defecto
        cat = data.get("categoria_producto") if data.get("categoria_producto") in cls.CATEGORIAS else (
            data.get("categoria") if data.get("categoria") in cls.CATEGORIAS else "Nuevo conocimiento"
        )

        # Resolver validación con valor por defecto
        val = data.get("validacion") if data.get("validacion") in cls.VALIDACIONES else "No validado"

        try:
            rel_weight = float(data.get("peso_relativo", 0.0) or 0.0)
        except (ValueError, TypeError):
            rel_weight = 0.0

        try:
            score = float(data.get("puntaje", 0.0) or 0.0)
        except (ValueError, TypeError):
            score = 0.0

        return cls(
            id=data.get("id"),
            titulo=data.get("titulo", "") or data.get("title", ""),
            tipo=data.get("tipo", "") or data.get("type", ""),
            categoria=cat,
            validado=bool(data.get("validado", False)),
            anio=data.get("anio", data.get("year", 0)),
            investigador_id=data.get("investigador_id"),
            grupo_id=data.get("grupo_id") or data.get("group"),
            raw=data.get("raw"),
            gran_categoria=data.get("gran_categoria") or "Sin clasificar",
            codigo_minciencias=data.get("codigo_minciencias", ""),
            categoria_producto=cat,
            validacion=val,
            peso_relativo=rel_weight,
            puntaje=score,
            activo=bool(data.get("activo", data.get("active", True))),
        )