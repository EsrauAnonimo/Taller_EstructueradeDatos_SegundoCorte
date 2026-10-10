import json
import os

from persistencia import PersistenciaBase
from modelos.multilista import Multilist
from entidades.grupo import Grupo
from entidades.investigador import Investigador
from entidades.producto import Producto


class PersistenciaJSON(PersistenciaBase):
    """Persistencia de datos en formato JSON."""

    def __init__(self, filepath=None):
        """Inicializa la persistencia con la ruta del archivo JSON."""
        if filepath is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            filepath = os.path.join(base_dir, "datos", "datos.json")
        self.filepath = filepath
        self._ensure_dir()

    def _ensure_dir(self):
        """Asegura que el directorio de destino exista."""
        directory = os.path.dirname(self.filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

    def exists(self):
        """Verifica si el archivo JSON existe."""
        return os.path.exists(self.filepath)

    def save(self, multilist):
        """Serializa la multilista y guarda en el archivo JSON."""
        data = self.from_multilist(multilist)
        with open(self.filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        return True

    def load(self):
        """Carga y retorna los datos desde el archivo JSON."""
        if not self.exists():
            return {"grupos": []}
        try:
            with open(self.filepath, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"grupos": []}

    @classmethod
    def from_multilist(cls, multilist):
        """Convierte una multilista a un diccionario plano."""
        grupos = []
        current_group = multilist.head_group
        while current_group is not None:
            grupo_data = current_group.data.to_dict() if hasattr(current_group.data, 'to_dict') else current_group.data
            investigadores = []
            current_inv = current_group.sublist
            while current_inv is not None:
                inv_data = current_inv.data.to_dict() if hasattr(current_inv.data, 'to_dict') else current_inv.data
                productos = []
                current_prod = current_inv.sublist
                while current_prod is not None:
                    prod_data = current_prod.data.to_dict() if hasattr(current_prod.data, 'to_dict') else current_prod.data
                    productos.append(prod_data)
                    current_prod = current_prod.next
                investigadores.append({
                    "investigador": inv_data,
                    "productos": productos
                })
                current_inv = current_inv.next
            grupos.append({
                "grupo": grupo_data,
                "investigadores": investigadores
            })
            current_group = current_group.next
        return {"grupos": grupos}

    @classmethod
    def to_multilist(cls, data):
        """Reconstruye una multilista a partir de un diccionario."""
        multilist = Multilist()
        if not data or not isinstance(data, dict):
            return multilist
        grupos_list = data.get("grupos", [])
        for grupo_info in grupos_list:
            grupo_dict = grupo_info.get("grupo", {})
            grupo = Grupo.from_dict(grupo_dict) if hasattr(Grupo, 'from_dict') else Grupo(**grupo_dict)
            group_node = multilist.add_group(grupo)
            if group_node is None:
                continue
            for inv_info in grupo_info.get("investigadores", []):
                inv_dict = inv_info.get("investigador", {})
                investigador = Investigador.from_dict(inv_dict) if hasattr(Investigador, 'from_dict') else Investigador(**inv_dict)
                inv_node = multilist.add_investigador(getattr(grupo, 'id', None), investigador)
                if inv_node is None:
                    continue
                for prod_dict in inv_info.get("productos", []):
                    producto = Producto.from_dict(prod_dict) if hasattr(Producto, 'from_dict') else Producto(**prod_dict)
                    multilist.add_producto(getattr(investigador, 'cedula', None) or getattr(producto, 'investigador_cedula', None), producto)
        return multilist