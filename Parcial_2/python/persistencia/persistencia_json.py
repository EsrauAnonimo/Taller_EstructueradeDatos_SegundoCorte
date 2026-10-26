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
            # Prioriza la carpeta unica centralizada /datos en la raiz del proyecto
            py_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            root_dir = os.path.dirname(py_dir)
            cand_root = os.path.join(root_dir, "datos", "datos.json")
            cand_local = os.path.join(py_dir, "datos", "datos.json")
            if os.path.exists(cand_root):
                filepath = cand_root
            elif os.path.exists(cand_local):
                filepath = cand_local
            else:
                filepath = cand_root
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
        """Convierte una multilista a un diccionario plano garantizando enlaces formales."""
        grupos = []
        current_group = multilist.head_group
        while current_group is not None:
            gid = getattr(current_group.data, 'id', None)
            grupo_data = current_group.data.to_dict() if hasattr(current_group.data, 'to_dict') else dict(current_group.data.__dict__)
            investigadores = []
            current_inv = current_group.sublist
            while current_inv is not None:
                inv_data = current_inv.data.to_dict() if hasattr(current_inv.data, 'to_dict') else dict(current_inv.data.__dict__)
                if gid is not None and not inv_data.get("grupo_id"):
                    inv_data["grupo_id"] = gid
                inv_ced = inv_data.get("cedula") or inv_data.get("id")
                productos = []
                current_prod = current_inv.sublist
                while current_prod is not None:
                    prod_data = current_prod.data.to_dict() if hasattr(current_prod.data, 'to_dict') else dict(current_prod.data.__dict__)
                    if gid is not None and not prod_data.get("grupo_id"):
                        prod_data["grupo_id"] = gid
                    if inv_ced and not prod_data.get("investigador_id"):
                        prod_data["investigador_id"] = str(inv_ced)
                    if inv_ced and not prod_data.get("investigador_cedula"):
                        prod_data["investigador_cedula"] = str(inv_ced)
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
        """Reconstruye una multilista a partir de un diccionario asegurando enlaces jerárquicos."""
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
            gid = getattr(grupo, 'id', None)
            for inv_info in grupo_info.get("investigadores", []):
                inv_dict = inv_info.get("investigador", {})
                investigador = Investigador.from_dict(inv_dict) if hasattr(Investigador, 'from_dict') else Investigador(**inv_dict)
                if gid is not None and not getattr(investigador, 'grupo_id', None):
                    investigador.grupo_id = gid
                inv_node = multilist.add_investigador(gid, investigador)
                if inv_node is None:
                    continue
                inv_ced = getattr(investigador, 'cedula', None) or getattr(investigador, 'id', None)
                for prod_dict in inv_info.get("productos", []):
                    producto = Producto.from_dict(prod_dict) if hasattr(Producto, 'from_dict') else Producto(**prod_dict)
                    if gid is not None and not getattr(producto, 'grupo_id', None):
                        producto.grupo_id = gid
                    if inv_ced and not getattr(producto, 'investigador_id', None):
                        producto.investigador_id = str(inv_ced)
                    if inv_ced and not getattr(producto, 'investigador_cedula', None):
                        producto.investigador_cedula = str(inv_ced)
                    multilist.add_producto(getattr(investigador, 'cedula', None) or getattr(producto, 'investigador_cedula', None), producto)
        return multilist