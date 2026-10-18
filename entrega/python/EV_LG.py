# -*- coding: utf-8 -*-
"""Lanzador oficial del Taller 2 de Estructura de Datos (UPC) — Parte Python.

Iniciales de los integrantes:
- EV: Esteban Raúl Vergara Jaime (CC: 1065595117, ervergara@unicesar.edu.co)
- LG: Luis Eduardo Gomes Rosales (CC: 1118821800, luiseduardogomez@unicesar.edu.co)

Asignatura: Estructura de Datos (Grupo 05)
Docente: Ing. Adith Pérez
Universidad Popular del Cesar (Valledupar, Cesar, 2026)
"""

import sys
import os
from pathlib import Path

# Resolver la ruta hacia la carpeta python/ del repositorio
BASE_DIR = Path(__file__).resolve().parent.parent.parent
PYTHON_DIR = BASE_DIR / "python"

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

# Importar y lanzar la aplicación existente sin duplicar código
try:
    from gui.app import App
except ImportError as err:
    print(f"Error al importar el módulo principal de la aplicación: {err}")
    print(f"Directorio de búsqueda verificado: {PYTHON_DIR}")
    sys.exit(1)


def main():
    """Punto de entrada de la aplicación PEA-i."""
    print("=" * 65)
    print("  PEA-i · Programa Estadístico de Análisis de Investigación")
    print("  Universidad Popular del Cesar — Estructura de Datos")
    print("  Autores: Esteban Raúl Vergara Jaime & Luis Eduardo Gomes Rosales")
    print("=" * 65)
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
