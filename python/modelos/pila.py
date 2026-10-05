from .nodo import Node


class Stack:
    """Pila para almacenar el historial de acciones (funcionalidad undo)."""

    def __init__(self):
        """Inicializa una pila vacía."""
        self.top = None
        self.size = 0

    def is_empty(self):
        """Verifica si la pila está vacía."""
        return self.top is None

    def __len__(self):
        """Retorna el tamaño de la pila."""
        return self.size

    def __repr__(self):
        """Representación en cadena de la pila."""
        return f"Stack(size={self.size})"

    def push(self, data):
        """Agrega un elemento en la parte superior de la pila."""
        node = Node(data)
        node.next = self.top
        self.top = node
        self.size += 1
        return node

    def pop(self):
        """Elimina y retorna el elemento superior de la pila."""
        if self.is_empty():
            return None
        node = self.top
        self.top = node.next
        node.next = None
        self.size -= 1
        return node.data

    def peek(self):
        """Retorna el elemento superior sin eliminarlo."""
        if self.is_empty():
            return None
        return self.top.data

    def clear(self):
        """Vacía la pila."""
        self.top = None
        self.size = 0

    def __iter__(self):
        """Itera desde la cima hacia abajo."""
        current = self.top
        while current is not None:
            yield current.data
            current = current.next