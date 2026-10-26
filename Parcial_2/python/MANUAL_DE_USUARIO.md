# Manual de Usuario — PEA-i (Programa Estadístico de Análisis de Investigación)

> **Universidad Popular del Cesar (UPC)**  
> **Facultad de Ingeniería y Tecnologías — Ingeniería de Sistemas**  
> **Asignatura:** Estructura de Datos (Grupo 05)

---

## 1. Requisitos del Sistema
- **Python:** 3.10 o superior ([python.org](https://www.python.org/downloads/)).
- **pip:** Gestor de paquetes de Python (incluido por defecto).
- **Librerías principales:**
  - `customtkinter` (interfaz gráfica moderna)
  - `matplotlib` (gráficos estadísticos)
  - `pandas` (procesamiento de métricas)
  - `beautifulsoup4` y `requests` (descarga y web scraping de MinCiencias)

---

## 2. Instalación Rápida

Abre una terminal en la carpeta del proyecto y ejecuta:

### Paso 1: Crear y activar entorno virtual
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

> **Nota Windows:** Si PowerShell bloquea la activación, ejecuta antes:  
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

### Paso 2: Instalar dependencias
```bash
pip install customtkinter matplotlib pandas requests beautifulsoup4
```

---

## 3. Cómo Ejecutar

Tienes dos formas directas de arrancar la aplicación:

### Opción A: Desde la Terminal
```bash
# Estando dentro de la carpeta python/
cd python && python ERV-LGR.py

# O desde la raíz del repositorio
python python/ERV-LGR.py
```

### Opción B: Desde Visual Studio Code (Tecla F5)
1. Abre el proyecto en VS Code.
2. Selecciona el intérprete del entorno virtual (`.venv`).
3. Presiona **F5** (configuración **PEA-i GUI**).

---

## 4. ¿Qué hace la aplicación? (Uso Breve)

El sistema gestiona la información académica mediante una **Multilista jerárquica en memoria** (`Grupo ➔ Investigadores ➔ Productos`) con persistencia local en `python/datos/datos.json`.

### 🏛 Pestaña Grupos
- **Listar y Buscar:** Consulta todos los grupos y filtra por nombre o código en tiempo real.
- **Crear / Editar:** Registra nuevos grupos con su código GrupLAC, categoría y líder.
- **Ver Detalle:** Muestra el plan de trabajo completo y la información institucional.
- **Deshacer (Undo):** Si eliminas un grupo por error, usa el botón **Deshacer** para restaurarlo inmediatamente (usando una **Pila** en memoria).

### 👤 Pestaña Investigadores
- **Gestión de Miembros:** Asocia investigadores a cada grupo registrado (cédula, nombres, correo).
- **Filtro por Grupo:** Permite ver únicamente los integrantes del grupo seleccionado.
- **Deshacer:** Restaura eliminaciones accidentales con la Pila.

### 📄 Pestaña Productos
- **Producción Científica:** Registra artículos, software, libros, patentes, etc.
- **Categorías MinCiencias:** Clasifica en *Nuevo Conocimiento (GNC)*, *Desarrollo Tecnológico (DTI)*, *Apropiación Social (ASC)* y *Formación de Recurso Humano (FRH)*.
- **Filtros:** Filtra por últimos 2 años, 5 años o rango personalizado.

### 📊 Pestaña Estadísticas
- **Indicadores Rápidos (KPIs):** Cantidad total de grupos, investigadores activos y productos validados.
- **Vistas:** Alterna entre análisis **Global**, **Por Grupo** o **Por Investigador**.
- **Resumen:** Calcula promedio, mediana, mínimo y máximo de productos.
- **4 Gráficos Interactivos:**
  1. *Productos por año* (evolución histórica).
  2. *Gran categoría MinCiencias* (GNC, DTI, ASC, FRH).
  3. *Tipos de productos más frecuentes*.
  4. *Histograma de productividad por investigador*.
- **Exportar PNG:** Guarda una imagen del panel estadístico completo con un clic.

### 🌐 Descarga desde el SCIENTI (MinCiencias)
- **1 Clic:** Desde el menú de ajustes **(⚙)**, haz clic en **"Descargar del SCIENTI"**. Extrae en segundo plano los datos reales del grupo GrupLAC oficial (UPC) e inserta automáticamente grupo, investigadores y productos en la multilista.
- **Otra URL:** Permite ingresar cualquier enlace público de GrupLAC para descargarlo.
- **Cola de Importación:** Encola varias URLs para procesarlas por lotes mediante una estructura de **Cola (FIFO)**.
- **Carga CSV:** Permite importar datos desde archivos CSV locales.

---

## 5. Estructuras de Datos Utilizadas (Requisitos del Proyecto)

Todas las estructuras fueron implementadas **a mano** en la carpeta `modelos/` (sin usar librerías de alto nivel para el modelo):

| Estructura | Archivo | ¿Dónde y cómo se usa en el programa? |
| :--- | :--- | :--- |
| **Lista Doblemente Enlazada** | `modelos/lista.py` | Estructura base con punteros anterior y siguiente (`Nodo`) para almacenar, recorrer e iterar elementos en ambos sentidos de forma eficiente. |
| **Multilista** | `modelos/multilista.py` | Núcleo del modelo en memoria. Conecta jerárquicamente las entidades: cada **Grupo** contiene su sublista de **Investigadores**, y estos a su vez sus **Productos**, permitiendo relaciones cruzadas sin base de datos SQL. |
| **Pila (Stack - LIFO)** | `modelos/pila.py` | Mecanismo de **Deshacer (Undo)** en Grupos, Investigadores y Productos. Al borrar un registro se apila (`push`), y al pulsar el botón "Deshacer" se desapila (`pop`) restaurándolo al instante. |
| **Cola (Queue - FIFO)** | `modelos/cola.py` | **Cola de Importación** de MinCiencias (`ColaImportacionModal`). Encola (`enqueue`) URLs de GrupLAC para descargarlas y procesarlas secuencialmente una por una (`dequeue`) en segundo plano sin congelar la app. |

---

## 6. Solución de Problemas Frecuentes

| Problema | Solución |
| :--- | :--- |
| `No module named 'customtkinter'` o similar | El entorno virtual no está activo. Ejecuta `.\.venv\Scripts\activate` y luego `pip install customtkinter matplotlib pandas requests beautifulsoup4`. |
| Script bloqueado en PowerShell al activar `.venv` | Ejecuta en la terminal: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`. |
| Error en Linux: `No module named '_tkinter'` | Falta Tkinter en el sistema operativo. Ejecuta: `sudo apt install python3-tk`. |
| Error al descargar desde SCIENTI | Revisa tu conexión a internet o verifica que la página de MinCiencias no esté en mantenimiento temporal. |
| ¿Dónde se guardan los cambios? | Los datos se guardan automáticamente en `python/datos/datos.json` (o manual con `Ctrl + S`). |

---

## 7. Autores

Proyecto desarrollado para la asignatura **Estructura de Datos (Grupo 05)** — **Universidad Popular del Cesar (UPC)**:

- **Esteban Raúl Vergara Jaime** — CC: 1065595117 — `ervergara@unicesar.edu.co`
- **Luis Eduardo Gomes Rosales** — CC: 1118821800 — `luiseduardogomez@unicesar.edu.co`
