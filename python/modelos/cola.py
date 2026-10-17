from .nodo import Node


class Queue:
    """Cola para almacenar URLs pendientes y operaciones por procesar."""

    def __init__(self):
        """Inicializa una cola vacía."""
        self.front = None
        self.rear = None
        self.size = 0

    def is_empty(self):
        """Verifica si la cola está vacía."""
        return self.size == 0

    def __len__(self):
        """Retorna el tamaño de la cola."""
        return self.size

    def __repr__(self):
        """Representación en cadena de la cola."""
        return f"Queue(size={self.size})"

    def enqueue(self, data):
        """Agrega un elemento al final de la cola."""
        node = Node(data)
        if self.is_empty():
            self.front = node
            self.rear = node
        else:
            self.rear.next = node
            self.rear = node
        self.size += 1
        return node

    def dequeue(self):
        """Elimina y retorna el elemento al frente de la cola."""
        if self.is_empty():
            return None
        node = self.front
        self.front = node.next
        if self.front is None:
            self.rear = None
        node.next = None
        self.size -= 1
        return node.data

    def peek(self):
        """Retorna el elemento al frente sin eliminarlo."""
        if self.is_empty():
            return None
        return self.front.data

    def clear(self):
        """Vacía la cola."""
        self.front = None
        self.rear = None
        self.size = 0

    def __iter__(self):
        """Itera desde el frente hacia atrás."""
        current = self.front
        while current is not None:
            yield current.data
            current = current.next