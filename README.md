# Taller 2 — Estructura de Datos — PEA-i

## Universidad
Universidad Popular del Cesar

## Facultad
Facultad de Ingeniería y Tecnologías

## Asignatura
Estructura de Datos

## Integrantes del grupo (Grupo 05)
- **Esteban Raúl Vergara Jaime** — CC: 1065595117 — ervergara@unicesar.edu.co
- **Luis Eduardo Gomes Rosales** — CC: 1118821800 — luiseduardogomez@unicesar.edu.co

## Requisitos
- Python 3.11+
- pip

## Instalación
```bash
pip install -r python/requirements.txt
```

## Cómo ejecutar

### 1. Interfaz Gráfica (Recomendada)
- **Desde VS Code:** Presionar **F5** y seleccionar la configuración **"PEA-i GUI"**.
- **Desde la Terminal:**
  ```bash
  python python/gui/app.py
  ```
  *(o ingresar a la carpeta `cd python` y ejecutar `python gui/app.py`)*

### 2. Versión Consola
- **Desde la Terminal:**
  ```bash
  python main.py
  ```

## Funcionalidades Principales
- **Estructura Multilista:** Gestión jerárquica en memoria (Grupos $\rightarrow$ Investigadores $\rightarrow$ Productos) con pilas y colas de apoyo.
- **Persistencia JSON:** Almacenamiento continuo en `python/datos/datos.json` sin necesidad de base de datos externa.
- **Importación SCIENTI / MinCiencias:**
  - Descarga directa con un clic de la URL oficial de GrupLAC.
  - Modal interactivo para ingresar cualquier URL de GrupLAC con barra de progreso en segundo plano.
  - Carga alternativa mediante archivo CSV.
- **Estadísticas y Análisis:** Visualización de métricas, productos por categoría y distribución temporal.

## Estructura del proyecto
- `main.py` — Menú interactivo por consola.
- `python/` — Código fuente del proyecto:
  - `entidades/` — Modelos de datos (`Grupo`, `Investigador`, `Producto`).
  - `modelos/` — Estructura `Multilist`, `Lista`, `Pila`, `Cola`, `Nodo`.
  - `crud/` — Operaciones CRUD para grupos, investigadores y productos.
  - `persistencia/` — Serialización y deserialización JSON.
  - `scraping/` — Extracción y procesamiento de datos MinCiencias / SCIENTI y CSV.
  - `gui/` — Interfaz gráfica moderna con CustomTkinter (tabs, formularios, widgets y modales).
  - `datos/` — Archivo de persistencia de datos (`datos.json`).
- `.vscode/launch.json` — Configuración para depuración con F5 en VS Code.
- `python/requirements.txt` — Dependencias del proyecto.

