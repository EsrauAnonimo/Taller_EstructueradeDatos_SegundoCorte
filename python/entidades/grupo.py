# -*- coding: utf-8 -*-
"""Entidad Grupo de investigación con plan de trabajo y atributos académicos."""

class Grupo:
    """Clase para representar un grupo de investigación."""

    def __init__(
        self,
        id=None,
        codigo_gruplac="",
        nombre="",
        categoria="",
        lider="",
        activo=True,
        fecha_creacion="",
        plan="",
    ):
        """Inicializa un objeto Grupo."""
        self.id = id
        self.codigo_gruplac = codigo_gruplac
        self.nombre = nombre
        self.categoria = categoria
        self.lider = lider
        self.activo = activo
        self.fecha_creacion = fecha_creacion
        self.plan = plan or ""

    def __repr__(self):
        """Representación en cadena del objeto Grupo."""
        return f"Grupo(id={self.id}, codigo_gruplac={self.codigo_gruplac}, nombre={self.nombre})"

    def to_dict(self):
        """Convierte el objeto Grupo a un diccionario."""
        return {
            "id": self.id,
            "codigo_gruplac": self.codigo_gruplac,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "lider": self.lider,
            "activo": self.activo,
            "fecha_creacion": self.fecha_creacion,
            "plan": self.plan,
        }

    @classmethod
    def from_dict(cls, data):
        """Crea un objeto Grupo a partir de un diccionario."""
        if data is None:
            return None
        return cls(
            id=data.get("id"),
            codigo_gruplac=data.get("codigo_gruplac", "") or data.get("code", ""),
            nombre=data.get("nombre", "") or data.get("name", ""),
            categoria=data.get("categoria", "") or data.get("category", ""),
            lider=data.get("lider", "") or data.get("leader", ""),
            activo=data.get("activo", data.get("active", True)),
            fecha_creacion=data.get("fecha_creacion", ""),
            plan=data.get("plan", ""),
        )