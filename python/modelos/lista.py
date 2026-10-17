from .nodo import Node


class DoublyLinkedList:
    """Lista doblemente enlazada para almacenar objetos en memoria."""

    def __init__(self):
        """Inicializa una lista vacía."""
        self.head = None
        self.tail = None
        self.size = 0

    def is_empty(self):
        """Verifica si la lista está vacía."""
        return self.size == 0

    def __len__(self):
        """Retorna el tamaño de la lista."""
        return self.size

    def __repr__(self):
        """Representación en cadena de la lista."""
        return f"DoublyLinkedList(size={self.size})"

    def append(self, data):
        """Agrega un nodo al final de la lista."""
        node = Node(data)
        if self.is_empty():
            self.head = node
            self.tail = node
        else:
            node.prev = self.tail
            self.tail.next = node
            self.tail = node
        self.size += 1
        return node

    def prepend(self, data):
        """Agrega un nodo al inicio de la lista."""
        node = Node(data)
        if self.is_empty():
            self.head = node
            self.tail = node
        else:
            node.next = self.head
            self.head.prev = node
            self.head = node
        self.size += 1
        return node

    def _get_node(self, index):
        """Obtiene el nodo en la posición indicada."""
        if index < 0 or index >= self.size:
            raise IndexError("Índice fuera de rango")
        current = self.head
        for _ in range(index):
            current = current.next
        return current

    def insert_at(self, index, data):
        """Inserta un nodo en la posición indicada."""
        if index < 0 or index > self.size:
            raise IndexError("Índice fuera de rango")
        if index == 0:
            return self.prepend(data)
        if index == self.size:
            return self.append(data)
        node = Node(data)
        current = self._get_node(index)
        node.prev = current.prev
        node.next = current
        current.prev.next = node
        current.prev = node
        self.size += 1
        return node

    def get(self, index):
        """Retorna el dato en la posición indicada."""
        try:
            node = self._get_node(index)
            return node.data
        except IndexError:
            return None

    def find(self, predicate):
        """Retorna el primer nodo que cumple con el predicado."""
        current = self.head
        while current is not None:
            if predicate(current.data):
                return current
            current = current.next
        return None

    def find_all(self, predicate):
        """Retorna una lista con todos los datos que cumplen con el predicado."""
        result = []
        current = self.head
        while current is not None:
            if predicate(current.data):
                result.append(current.data)
            current = current.next
        return result

    def to_list(self):
        """Retorna una lista con todos los datos de la lista."""
        result = []
        current = self.head
        while current is not None:
            result.append(current.data)
            current = current.next
        return result

    def update_at(self, index, new_data):
        """Reemplaza el dato en la posición indicada."""
        try:
            node = self._get_node(index)
            node.data = new_data
            return True
        except IndexError:
            return False

    def update_by(self, predicate, updater):
        """Aplica un actualizador a todos los nodos que cumplen con el predicado."""
        count = 0
        current = self.head
        while current is not None:
            if predicate(current.data):
                updater(current.data)
                count += 1
            current = current.next
        return count

    def deactivate_at(self, index):
        """Desactiva el nodo en la posición indicada."""
        try:
            node = self._get_node(index)
            node.active = False
            return True
        except IndexError:
            return False

    def deactivate_by(self, predicate):
        """Desactiva todos los nodos que cumplen con el predicado."""
        count = 0
        current = self.head
        while current is not None:
            if predicate(current.data):
                current.active = False
                count += 1
            current = current.next
        return count

    def _unlink(self, node):
        """Desvincula un nodo de la lista."""
        if node.prev is not None:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next is not None:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        node.prev = None
        node.next = None
        self.size -= 1

    def remove_at(self, index):
        """Elimina físicamente el nodo en la posición indicada."""
        try:
            node = self._get_node(index)
            self._unlink(node)
            return True
        except IndexError:
            return False

    def remove_by(self, predicate):
        """Elimina físicamente todos los nodos que cumplen con el predicado."""
        to_remove = []
        current = self.head
        while current is not None:
            if predicate(current.data):
                to_remove.append(current)
            current = current.next
        for node in to_remove:
            self._unlink(node)
        return len(to_remove)

    def clear(self):
        """Elimina todos los nodos de la lista."""
        self.head = None
        self.tail = None
        self.size = 0

    def __iter__(self):
        """Permite iterar sobre los datos de la lista."""
        current = self.head
        while current is not None:
            yield current.data
            current = current.next

    def iterate_active(self):
        """Generador que retorna solo nodos activos."""
        current = self.head
        while current is not None:
            if current.active:
                yield current
            current = current.next