class PersistenciaBase:
    """Interfaz base para persistencia de datos."""

    def save(self, data):
        """Guarda los datos en el medio de almacenamiento."""
        raise NotImplementedError

    def load(self):
        """Carga los datos desde el medio de almacenamiento."""
        raise NotImplementedError

    def exists(self):
        """Verifica si existe el archivo o medio de almacenamiento."""
        raise NotImplementedError