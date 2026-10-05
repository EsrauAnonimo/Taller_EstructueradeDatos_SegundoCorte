from modelos.multilista import Multilist
from entidades.investigador import Investigador


class InvestigadorCRUD:
    """Operaciones CRUD para investigadores."""

    def __init__(self, multilist: Multilist):
        """Inicializa el CRUD con una multilista compartida."""
        self.multilist = multilist

    def create(self, investigador: Investigador):
        """Inserta un nuevo investigador. Retorna False si hay duplicado de cedula."""
        if investigador.cedula and self.get_by_cedula(investigador.cedula) is not None:
            return False
        result = self.multilist.add_investigador(investigador.grupo_id, investigador)
        return result is not None

    def list_all(self):
        """Retorna lista de investigadores activos."""
        return list(self.multilist.iterate_investigadores())

    def list_by_group(self, group_id):
        """Retorna lista de investigadores activos por grupo."""
        return list(self.multilist.iterate_investigadores(group_id=group_id))

    def get_by_cedula(self, cedula):
        """Retorna el investigador por cedula, o None si no existe."""
        result = self.multilist.get_investigador(cedula)
        if result is None:
            return None
        inv_node, _ = result
        return inv_node.data

    def update(self, cedula, **fields):
        """Actualiza campos del investigador."""
        inv = self.get_by_cedula(cedula)
        if inv is None:
            return False
        for key, value in fields.items():
            if hasattr(inv, key):
                setattr(inv, key, value)
        return True

    def deactivate(self, cedula):
        """Desactiva el investigador."""
        return self.multilist.deactivate_investigador(cedula)

    def activate(self, cedula):
        """Activa el investigador."""
        result = self.multilist.get_investigador(cedula)
        if result is None:
            return False
        inv_node, _ = result
        inv_node.active = True
        return True

    def delete(self, cedula):
        """Elimina físicamente el investigador."""
        return self.multilist.remove_investigador(cedula)