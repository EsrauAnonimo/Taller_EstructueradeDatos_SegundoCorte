from .nodo import Node


class Multilist:
    """Multilista para modelar la jerarquía Grupo -> Investigadores -> Productos."""

    def __init__(self):
        """Inicializa la multilista vacía."""
        self.head_group = None
        self.size_groups = 0

    def is_empty(self):
        """Verifica si la multilista está vacía."""
        return self.head_group is None

    def __len__(self):
        """Retorna el número de grupos."""
        return self.size_groups

    def __repr__(self):
        """Representación en cadena de la multilista."""
        return f"Multilist(groups={self.size_groups})"

    def add_group(self, grupo):
        """Agrega un grupo al final de la lista principal."""
        node = Node(grupo)
        if self.head_group is None:
            self.head_group = node
        else:
            current = self.head_group
            while current.next is not None:
                current = current.next
            current.next = node
        self.size_groups += 1
        return node

    def get_group_by_id(self, group_id):
        """Retorna el nodo que contiene el grupo con el id dado."""
        current = self.head_group
        while current is not None:
            gid = getattr(current.data, 'id', None)
            if current.active and (gid == group_id or (gid is not None and str(gid) == str(group_id))):
                return current
            current = current.next
        return None

    def get_group_by_code(self, codigo_gruplac):
        """Retorna el nodo que contiene el grupo con el codigo dado."""
        current = self.head_group
        while current is not None:
            if current.active and getattr(current.data, 'codigo_gruplac', None) == codigo_gruplac:
                return current
            current = current.next
        return None

    def update_group(self, group_id, new_grupo):
        """Reemplaza los datos del grupo con el id dado."""
        node = self.get_group_by_id(group_id)
        if node is None:
            return False
        node.data = new_grupo
        return True

    def deactivate_group(self, group_id):
        """Desactiva el grupo con el id dado."""
        node = self.get_group_by_id(group_id)
        if node is None:
            return False
        node.active = False
        return True

    def remove_group(self, group_id):
        """Elimina el grupo y todas sus sublistas."""
        prev = None
        current = self.head_group
        while current is not None:
            if getattr(current.data, 'id', None) == group_id:
                if prev is None:
                    self.head_group = current.next
                else:
                    prev.next = current.next
                current.next = None
                current.sublist = None
                self.size_groups -= 1
                return True
            prev = current
            current = current.next
        return False

    def add_investigador(self, group_id, investigador):
        """Agrega un investigador a la sublista del grupo indicado."""
        group_node = self.get_group_by_id(group_id)
        if group_node is None:
            return None
        inv_node = Node(investigador)
        if group_node.sublist is None:
            group_node.sublist = inv_node
        else:
            current = group_node.sublist
            while current.next is not None:
                current = current.next
            current.next = inv_node
        return inv_node

    def get_investigador(self, cedula, only_active=True):
        """Busca un investigador por cedula en todas las sublistas."""
        group_current = self.head_group
        while group_current is not None:
            inv_current = group_current.sublist
            while inv_current is not None:
                matches = (str(getattr(inv_current.data, 'cedula', None) or '') == str(cedula) or
                           str(getattr(inv_current.data, 'id', None) or '') == str(cedula))
                if matches and (not only_active or inv_current.active):
                    return (inv_current, group_current)
                inv_current = inv_current.next
            group_current = group_current.next
        return None

    def update_investigador(self, cedula, new_investigador):
        """Actualiza los datos del investigador en todas sus apariciones en la Multilista."""
        updated = False
        group_current = self.head_group
        while group_current is not None:
            inv_current = group_current.sublist
            while inv_current is not None:
                if (str(getattr(inv_current.data, 'cedula', None) or '') == str(cedula) or
                        str(getattr(inv_current.data, 'id', None) or '') == str(cedula)):
                    inv_current.data = new_investigador
                    updated = True
                inv_current = inv_current.next
            group_current = group_current.next
        return updated

    def deactivate_investigador(self, cedula):
        """Desactiva el investigador en todas las relaciones de la Multilista y sus productos."""
        deactivated = False
        group_current = self.head_group
        while group_current is not None:
            inv_current = group_current.sublist
            while inv_current is not None:
                if (str(getattr(inv_current.data, 'cedula', None) or '') == str(cedula) or
                        str(getattr(inv_current.data, 'id', None) or '') == str(cedula)):
                    inv_current.active = False
                    if hasattr(inv_current.data, 'activo'):
                        inv_current.data.activo = False
                    # Desactivar también los productos del investigador en esta sublista
                    prod_current = inv_current.sublist
                    while prod_current is not None:
                        prod_current.active = False
                        prod_current = prod_current.next
                    deactivated = True
                inv_current = inv_current.next
            group_current = group_current.next
        return deactivated

    def activate_investigador(self, cedula):
        """Reactiva el investigador en todas las relaciones de la Multilista y sus productos."""
        activated = False
        group_current = self.head_group
        while group_current is not None:
            inv_current = group_current.sublist
            while inv_current is not None:
                if (str(getattr(inv_current.data, 'cedula', None) or '') == str(cedula) or
                        str(getattr(inv_current.data, 'id', None) or '') == str(cedula)):
                    inv_current.active = True
                    if hasattr(inv_current.data, 'activo'):
                        inv_current.data.activo = True
                    # Reactivar también los productos del investigador en esta sublista
                    prod_current = inv_current.sublist
                    while prod_current is not None:
                        prod_current.active = True
                        prod_current = prod_current.next
                    activated = True
                inv_current = inv_current.next
            group_current = group_current.next
        return activated

    def remove_investigador(self, cedula):
        """Elimina físicamente el investigador de todas las relaciones en la Multilista."""
        removed = False
        group_current = self.head_group
        while group_current is not None:
            prev_inv = None
            inv_current = group_current.sublist
            while inv_current is not None:
                if (str(getattr(inv_current.data, 'cedula', None) or '') == str(cedula) or
                        str(getattr(inv_current.data, 'id', None) or '') == str(cedula)):
                    if prev_inv is None:
                        group_current.sublist = inv_current.next
                    else:
                        prev_inv.next = inv_current.next
                    temp = inv_current
                    inv_current = inv_current.next
                    temp.next = None
                    temp.sublist = None
                    removed = True
                else:
                    prev_inv = inv_current
                    inv_current = inv_current.next
            group_current = group_current.next
        return removed

    def add_investigador_to_group(self, group_id, investigador):
        """Vincula un investigador a un grupo en la Multilista."""
        group_node = self.get_group_by_id(group_id)
        if group_node is None:
            return None
        ced = str(getattr(investigador, 'cedula', None) or getattr(investigador, 'id', None) or '')
        # Verificar si ya existe en este grupo
        current = group_node.sublist
        while current is not None:
            if str(getattr(current.data, 'cedula', None) or getattr(current.data, 'id', None) or '') == ced:
                current.active = True
                return current
            current = current.next

        # Si ya existe en la multilista en otro grupo, enlazar productos existentes
        existing_res = self.get_investigador(ced, only_active=False)
        inv_node = Node(investigador)
        if existing_res is not None:
            other_node, _ = existing_res
            inv_node.sublist = other_node.sublist

        if group_node.sublist is None:
            group_node.sublist = inv_node
        else:
            curr = group_node.sublist
            while curr.next is not None:
                curr = curr.next
            curr.next = inv_node
        return inv_node

    def remove_investigador_from_group(self, group_id, cedula):
        """Desvincula a un investigador de un grupo específico en la Multilista."""
        group_node = self.get_group_by_id(group_id)
        if group_node is None:
            return False
        prev = None
        current = group_node.sublist
        while current is not None:
            if (str(getattr(current.data, 'cedula', None) or '') == str(cedula) or
                    str(getattr(current.data, 'id', None) or '') == str(cedula)):
                if prev is None:
                    group_node.sublist = current.next
                else:
                    prev.next = current.next
                current.next = None
                return True
            prev = current
            current = current.next
        return False

    def get_grupos_by_investigador(self, cedula):
        """Retorna la lista de grupos activos a los que pertenece el investigador en la Multilista."""
        grupos = []
        group_current = self.head_group
        while group_current is not None:
            if group_current.active:
                inv_current = group_current.sublist
                while inv_current is not None:
                    if inv_current.active and (
                        str(getattr(inv_current.data, 'cedula', None) or '') == str(cedula) or
                        str(getattr(inv_current.data, 'id', None) or '') == str(cedula)
                    ):
                        grupos.append(group_current.data)
                        break
                    inv_current = inv_current.next
            group_current = group_current.next
        return grupos

    def get_investigadores_by_grupo(self, group_id):
        """Retorna lista de investigadores activos adscritos al grupo en la Multilista."""
        return list(self.iterate_investigadores(group_id=group_id))

    def add_producto(self, cedula, producto):
        """Agrega un producto a la sublista del investigador indicado."""
        result = self.get_investigador(cedula)
        if result is None:
            return None
        inv_node, _ = result
        prod_node = Node(producto)
        if inv_node.sublist is None:
            inv_node.sublist = prod_node
        else:
            current = inv_node.sublist
            while current.next is not None:
                current = current.next
            current.next = prod_node
        return prod_node

    def get_productos_by_investigador(self, cedula):
        """Retorna todos los productos activos del investigador en la Multilista (sin duplicados)."""
        productos = []
        seen_ids = set()
        group_current = self.head_group
        while group_current is not None:
            if group_current.active:
                inv_current = group_current.sublist
                while inv_current is not None:
                    if inv_current.active and (
                        str(getattr(inv_current.data, 'cedula', None) or '') == str(cedula) or
                        str(getattr(inv_current.data, 'id', None) or '') == str(cedula)
                    ):
                        prod_current = inv_current.sublist
                        while prod_current is not None:
                            if prod_current.active:
                                pid = getattr(prod_current.data, 'id', None)
                                if pid is None or pid not in seen_ids:
                                    if pid is not None:
                                        seen_ids.add(pid)
                                    productos.append(prod_current.data)
                            prod_current = prod_current.next
                    inv_current = inv_current.next
            group_current = group_current.next
        return productos

    def get_productos_by_grupo(self, group_id):
        """Retorna una lista de productos del grupo."""
        productos = []
        group_node = self.get_group_by_id(group_id)
        if group_node is None:
            return productos
        inv_current = group_node.sublist
        while inv_current is not None:
            if inv_current.active:
                prod_current = inv_current.sublist
                while prod_current is not None:
                    if prod_current.active:
                        productos.append(prod_current.data)
                    prod_current = prod_current.next
            inv_current = inv_current.next
        return productos

    def get_productos_by_anio(self, anio):
        """Retorna una lista de productos del anio indicado."""
        productos = []
        group_current = self.head_group
        while group_current is not None:
            if group_current.active:
                inv_current = group_current.sublist
                while inv_current is not None:
                    if inv_current.active:
                        prod_current = inv_current.sublist
                        while prod_current is not None:
                            if prod_current.active and getattr(prod_current.data, 'anio', None) == anio:
                                productos.append(prod_current.data)
                            prod_current = prod_current.next
                    inv_current = inv_current.next
            group_current = group_current.next
        return productos

    def get_productos_by_anio_range(self, anio_inicio, anio_fin):
        """Retorna una lista de productos dentro del rango de años."""
        productos = []
        group_current = self.head_group
        while group_current is not None:
            if group_current.active:
                inv_current = group_current.sublist
                while inv_current is not None:
                    if inv_current.active:
                        prod_current = inv_current.sublist
                        while prod_current is not None:
                            if prod_current.active:
                                prod_anio = getattr(prod_current.data, 'anio', None)
                                if prod_anio is not None and anio_inicio <= prod_anio <= anio_fin:
                                    productos.append(prod_current.data)
                            prod_current = prod_current.next
                    inv_current = inv_current.next
            group_current = group_current.next
        return productos
    def _find_producto_node(self, producto_id):
        """Busca el nodo de producto por id."""
        group_current = self.head_group
        while group_current is not None:
            inv_current = group_current.sublist
            while inv_current is not None:
                prod_current = inv_current.sublist
                while prod_current is not None:
                    if getattr(prod_current.data, 'id', None) == producto_id:
                        return (prod_current, inv_current)
                    prod_current = prod_current.next
                inv_current = inv_current.next
            group_current = group_current.next
        return None

    def update_producto(self, producto_id, new_producto):
        """Actualiza los datos de un producto por id."""
        result = self._find_producto_node(producto_id)
        if result is None:
            return False
        prod_node, _ = result
        prod_node.data = new_producto
        return True

    def deactivate_producto(self, producto_id):
        """Desactiva un producto por id."""
        result = self._find_producto_node(producto_id)
        if result is None:
            return False
        prod_node, _ = result
        prod_node.active = False
        return True

    def remove_producto(self, producto_id):
        """Elimina un producto de su sublista."""
        group_current = self.head_group
        while group_current is not None:
            inv_current = group_current.sublist
            while inv_current is not None:
                prev_prod = None
                prod_current = inv_current.sublist
                while prod_current is not None:
                    if getattr(prod_current.data, 'id', None) == producto_id:
                        if prev_prod is None:
                            inv_current.sublist = prod_current.next
                        else:
                            prev_prod.next = prod_current.next
                        prod_current.next = None
                        return True
                    prev_prod = prod_current
                    prod_current = prod_current.next
                inv_current = inv_current.next
            group_current = group_current.next
        return False

    def iterate_groups(self):
        """Generador de grupos activos."""
        current = self.head_group
        while current is not None:
            if current.active:
                yield current.data
            current = current.next

    def iterate_investigadores(self, group_id=None):
        """Generador de investigadores activos. Opcionalmente filtrado por grupo."""
        if group_id is not None:
            group_node = self.get_group_by_id(group_id)
            if group_node is None:
                return
            inv_current = group_node.sublist
            while inv_current is not None:
                if inv_current.active:
                    yield inv_current.data
                inv_current = inv_current.next
            return
        group_current = self.head_group
        while group_current is not None:
            if group_current.active:
                inv_current = group_current.sublist
                while inv_current is not None:
                    if inv_current.active:
                        yield inv_current.data
                    inv_current = inv_current.next
            group_current = group_current.next

    def iterate_productos(self, group_id=None, cedula=None, anio=None):
        """Generador de productos activos con filtros opcionales."""
        if cedula is not None:
            result = self.get_investigador(cedula)
            if result is None:
                return
            inv_node, _ = result
            prod_current = inv_node.sublist
            while prod_current is not None:
                if prod_current.active:
                    if anio is None or getattr(prod_current.data, 'anio', None) == anio:
                        yield prod_current.data
                prod_current = prod_current.next
            return
        if group_id is not None:
            group_node = self.get_group_by_id(group_id)
            if group_node is None:
                return
            inv_current = group_node.sublist
            while inv_current is not None:
                if inv_current.active:
                    prod_current = inv_current.sublist
                    while prod_current is not None:
                        if prod_current.active:
                            if anio is None or getattr(prod_current.data, 'anio', None) == anio:
                                yield prod_current.data
                        prod_current = prod_current.next
                inv_current = inv_current.next
            return
        group_current = self.head_group
        while group_current is not None:
            if group_current.active:
                inv_current = group_current.sublist
                while inv_current is not None:
                    if inv_current.active:
                        prod_current = inv_current.sublist
                        while prod_current is not None:
                            if prod_current.active:
                                if anio is None or getattr(prod_current.data, 'anio', None) == anio:
                                    yield prod_current.data
                            prod_current = prod_current.next
                    inv_current = inv_current.next
            group_current = group_current.next

    def count_productos_by_anio(self):
        """Retorna un diccionario con conteo de productos por anio."""
        counts = {}
        group_current = self.head_group
        while group_current is not None:
            if group_current.active:
                inv_current = group_current.sublist
                while inv_current is not None:
                    if inv_current.active:
                        prod_current = inv_current.sublist
                        while prod_current is not None:
                            if prod_current.active:
                                prod_anio = getattr(prod_current.data, 'anio', None)
                                if prod_anio is not None:
                                    counts[prod_anio] = counts.get(prod_anio, 0) + 1
                            prod_current = prod_current.next
                    inv_current = inv_current.next
            group_current = group_current.next
        return counts
