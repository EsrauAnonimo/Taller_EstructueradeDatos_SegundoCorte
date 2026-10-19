from modelos.multilista import Multilist
from entidades.producto import Producto


class ProductoCRUD:
    """Operaciones CRUD para productos de investigación."""

    def __init__(self, multilist: Multilist):
        """Inicializa el CRUD con una multilista compartida."""
        self.multilist = multilist

    def create(self, producto: Producto):
        """Inserta un nuevo producto."""
        cedula = getattr(producto, 'investigador_cedula', None) or getattr(producto, 'cedula', None)
        if cedula is None and hasattr(producto, 'investigador_id'):
            cedula = getattr(producto, 'investigador_id', None)
        result = self.multilist.add_producto(cedula, producto)
        return result is not None

    def list_all(self):
        """Retorna lista de productos activos."""
        return list(self.multilist.iterate_productos())

    def list_by_group(self, group_id):
        """Retorna lista de productos activos por grupo."""
        return list(self.multilist.iterate_productos(group_id=group_id))

    def list_by_investigador(self, cedula):
        """Retorna lista de productos activos por investigador."""
        return list(self.multilist.iterate_productos(cedula=cedula))

    def list_by_anio(self, anio):
        """Retorna lista de productos activos por año."""
        return list(self.multilist.iterate_productos(anio=anio))

    def list_by_anio_range(self, anio_inicio, anio_fin):
        """Retorna lista de productos activos por rango de años."""
        return self.multilist.get_productos_by_anio_range(anio_inicio, anio_fin)

    def get_by_id(self, producto_id):
        """Retorna el producto por id, o None si no existe."""
        result = self.multilist._find_producto_node(producto_id)
        if result is None:
            return None
        prod_node, _ = result
        return prod_node.data

    def update(self, producto_id, **fields):
        """Actualiza campos del producto."""
        prod = self.get_by_id(producto_id)
        if prod is None:
            return False
        for key, value in fields.items():
            if hasattr(prod, key):
                setattr(prod, key, value)
        return True

    def deactivate(self, producto_id):
        """Desactiva el producto."""
        return self.multilist.deactivate_producto(producto_id)

    def activate(self, producto_id):
        """Activa el producto."""
        result = self.multilist._find_producto_node(producto_id)
        if result is None:
            return False
        prod_node, _ = result
        prod_node.active = True
        return True

    def delete(self, producto_id):
        """Elimina físicamente el producto."""
        return self.multilist.remove_producto(producto_id)