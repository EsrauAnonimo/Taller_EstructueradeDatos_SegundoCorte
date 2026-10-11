class Producto:
    """Clase para representar un producto de investigación."""

    def __init__(self, id=None, titulo="", tipo="", categoria="", validado=False, anio=0, investigador_id=None, grupo_id=None, raw=None, gran_categoria="Sin clasificar", codigo_minciencias=""):
        """Inicializa un objeto Producto."""
        self.id = id
        self.titulo = titulo
        self.tipo = tipo
        self.categoria = categoria
        self.validado = validado
        self.anio = anio
        self.investigador_id = investigador_id
        self.grupo_id = grupo_id
        self.raw = raw
        self.gran_categoria = gran_categoria if gran_categoria else "Sin clasificar"
        self.codigo_minciencias = codigo_minciencias or ""

    def __repr__(self):
        """Representación en cadena del objeto Producto."""
        return f"Producto(id={self.id}, titulo={self.titulo}, tipo={self.tipo}, gran_categoria={self.gran_categoria}, codigo_minciencias={self.codigo_minciencias})"

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
            "codigo_minciencias": self.codigo_minciencias
        }

    @classmethod
    def from_dict(cls, data):
        """Crea un objeto Producto a partir de un diccionario."""
        if data is None:
            return None
        return cls(
            id=data.get("id"),
            titulo=data.get("titulo", ""),
            tipo=data.get("tipo", ""),
            categoria=data.get("categoria", ""),
            validado=data.get("validado", False),
            anio=data.get("anio", 0),
            investigador_id=data.get("investigador_id"),
            grupo_id=data.get("grupo_id"),
            raw=data.get("raw"),
            gran_categoria=data.get("gran_categoria") or "Sin clasificar",
            codigo_minciencias=data.get("codigo_minciencias", "")
        )