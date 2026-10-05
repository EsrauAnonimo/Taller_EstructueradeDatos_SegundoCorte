from modelos.multilista import Multilist
from entidades.grupo import Grupo


class GrupoCRUD:
    """Operaciones CRUD para grupos de investigación."""

    def __init__(self, multilist: Multilist):
        """Inicializa el CRUD con una multilista compartida."""
        self.multilist = multilist

    def create(self, grupo: Grupo):
        """Inserta un nuevo grupo. Retorna False si hay duplicado de codigo_gruplac."""
        if grupo.codigo_gruplac and self.get_by_code(grupo.codigo_gruplac) is not None:
            return False
        self.multilist.add_group(grupo)
        return True

    def list_all(self):
        """Retorna lista de grupos activos."""
        return list(self.multilist.iterate_groups())

    def get_by_id(self, group_id):
        """Retorna el grupo por id, o None si no existe."""
        node = self.multilist.get_group_by_id(group_id)
        if node is None:
            return None
        return node.data

    def get_by_code(self, codigo_gruplac):
        """Retorna el grupo por codigo, o None si no existe."""
        node = self.multilist.get_group_by_code(codigo_gruplac)
        if node is None:
            return None
        return node.data

    def update(self, group_id, **fields):
        """Actualiza campos del grupo."""
        grupo = self.get_by_id(group_id)
        if grupo is None:
            return False
        for key, value in fields.items():
            if hasattr(grupo, key):
                setattr(grupo, key, value)
        return True

    def deactivate(self, group_id):
        """Desactiva el grupo."""
        return self.multilist.deactivate_group(group_id)

    def activate(self, group_id):
        """Activa el grupo."""
        node = self.multilist.get_group_by_id(group_id)
        if node is None:
            return False
        node.active = True
        return True

    def delete(self, group_id):
        """Elimina físicamente el grupo."""
        return self.multilist.remove_group(group_id)