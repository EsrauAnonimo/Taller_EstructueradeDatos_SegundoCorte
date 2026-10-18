# Manual de Usuario — PEA-i (Programa Estadístico de Análisis de Investigación)

> **Universidad Popular del Cesar (UPC)**  
> **Facultad de Ingeniería y Tecnologías — Programa de Ingeniería de Sistemas**  
> **Asignatura:** Estructura de Datos (Grupo 05)  
> **Plataforma:** Aplicación de Escritorio con Interfaz Gráfica (Python 3.10+ / CustomTkinter)

---

## Tabla de Contenido
1. [Introducción y Propósito](#1-introducción-y-propósito)
2. [Requisitos Previos del Sistema](#2-requisitos-previos-del-sistema)
3. [Guía de Instalación Paso a Paso](#3-guía-de-instalación-paso-a-paso)
4. [Guía de Ejecución del Sistema](#4-guía-de-ejecución-del-sistema)
5. [Estructura del Repositorio](#5-estructura-del-repositorio)
6. [Guía de Uso de la Aplicación](#6-guía-de-uso-de-la-aplicación)
   - [Navegación General y Menú de Opciones](#navegación-general-y-menú-de-opciones)
   - [Pestaña: Grupos de Investigación](#pestaña-grupos-de-investigación)
   - [Pestaña: Investigadores](#pestaña-investigadores)
   - [Pestaña: Productos Académicos](#pestaña-productos-académicos)
   - [Pestaña: Estadísticas y Analítica](#pestaña-estadísticas-y-analítica)
   - [Módulo de Descarga y Scraping SCIENTI (MinCiencias)](#módulo-de-descarga-y-scraping-scienti-minciencias)
   - [Cola de Importación y Carga CSV](#cola-de-importación-y-carga-csv)
7. [Solución de Problemas Comunes (FAQ / Troubleshooting)](#7-solución-de-problemas-comunes-faq--troubleshooting)
8. [Créditos y Autores](#8-créditos-y-autores)

---

## 1. Introducción y Propósito

**PEA-i** (*Programa Estadístico de Análisis de Investigación*) es un sistema de escritorio integral concebido para gestionar, consolidar y auditar la producción científica y académica de grupos de investigación e investigadores institucionales.

### Principales Objetivos:
- **Gestión Jerárquica en Memoria:** Modela las relaciones `Grupo ➔ Investigadores ➔ Productos` empleando una **Multilista** enlazada manualmente, optimizada para búsquedas y recorridos continuos sin necesidad de motores de bases de datos relacionales tradicionales.
- **Estructuras de Datos Implementadas a Mano:** Incorpora **Listas doblemente enlazadas**, **Multilistas**, **Pilas (Stack)** para operaciones de reversión (*Deshacer / Undo* de eliminaciones) y **Colas (Queue)** para la gestión asíncrona de lotes de importación.
- **Integración con MinCiencias / SCIENTI:** Realiza extracción y raspado web (*web scraping*) directo desde plataformas oficiales como **GrupLAC** mediante HTTP y análisis sintáctico de HTML, así como compatibilidad de carga mediante archivos CSV.
- **Persistencia Ligera en JSON:** Almacena el estado completo de las entidades en un archivo estructurado local (`python/datos/datos.json`), garantizando portabilidad inmediata.
- **Visualización y Analítica:** Tableros interactivos construidos con **CustomTkinter**, **Matplotlib** y **Pandas** para generar métricas descriptivas (media, mediana, máximos, mínimos) y cuatro gráficos dinámicos de distribución temporal y taxonómica.

---

## 2. Requisitos Previos del Sistema

Antes de iniciar la instalación, verifique que su entorno cumpla con las siguientes especificaciones:

| Componente | Requisito Mínimo | Versión Recomendada | Notas |
| :--- | :--- | :--- | :--- |
| **Sistema Operativo** | Windows 10/11 (64-bit), macOS 12+ o Linux (Ubuntu 20.04+) | Windows 11 / Linux Ubuntu 22.04 LTS | Soporte multiplataforma garantizado. |
| **Python** | Python 3.10 | Python 3.11 o 3.12 | Asegúrese de marcar *"Add Python to PATH"* durante la instalación. |
| **Gestor de Paquetes** | pip 22.0+ | pip actualizado (`python -m pip install --upgrade pip`) | Incluido por defecto con Python. |
| **Entorno de Desarrollo** | Visual Studio Code | VS Code con extensión oficial de Python | Opcional, pero recomendado para depurar con **F5**. |
| **Conectividad** | Conexión a Internet | Banda ancha estándar | Necesaria para instalar librerías y descargar datos desde SCIENTI. |
| **Soporte GUI (Linux)** | Tkinter (`python3-tk`) | Instalado a nivel de sistema (`sudo apt install python3-tk`) | En Windows y macOS se instala automáticamente con Python. |

---

## 3. Guía de Instalación Paso a Paso

Siga estos pasos desde su terminal (PowerShell, Git Bash, CMD o consola Linux):

### Paso 1: Clonar el Repositorio
Abra su terminal y clone el repositorio en la carpeta deseada:
```bash
git clone https://github.com/EsrauAnonimo/Taller_EstructueradeDatos_SegundoCorte.git
cd Taller_EstructueradeDatos_SegundoCorte
```

### Paso 2: Crear el Entorno Virtual de Python
Aislar las dependencias del proyecto previene conflictos con librerías globales del sistema:

- **En Windows (PowerShell / CMD):**
  ```powershell
  python -m venv .venv
  ```
- **En Linux / macOS:**
  ```bash
  python3 -m venv .venv
  ```

### Paso 3: Activar el Entorno Virtual

- **En Windows (PowerShell):**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
  > *Nota para PowerShell:* Si aparece un mensaje indicando que la ejecución de scripts está deshabilitada en su sistema, ejecute previamente:
  > ```powershell
  > Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  > ```

- **En Windows (Símbolo del sistema / CMD):**
  ```cmd
  .\.venv\Scripts\activate.bat
  ```

- **En Linux / macOS:**
  ```bash
  source .venv/bin/activate
  ```

*Sabrá que el entorno está activo porque verá el prefijo `(.venv)` al inicio de su línea de comandos.*

### Paso 4: Actualizar pip e Instalar Dependencias
Con el entorno virtual activo, actualice el gestor de paquetes e instale las dependencias estrictamente necesarias desde el archivo `python/requirements.txt`:

```bash
python -m pip install --upgrade pip
pip install -r python/requirements.txt
```

### Detalle de las Dependencias Estrictas:
El archivo `python/requirements.txt` contiene únicamente los paquetes esenciales organizados alfabéticamente:
1. `beautifulsoup4`: Parser HTML/XML para procesar y estructurar las páginas de GrupLAC.
2. `customtkinter`: Biblioteca moderna de componentes gráficos con estilos oscuros/claros nativos.
3. `matplotlib`: Motor de renderizado para los gráficos de dispersión, barras e histogramas en la pestaña de estadísticas.
4. `pandas`: Estructuración tabular y cálculo eficiente de métricas estadísticas (media, mediana, cuartiles).
5. `requests`: Cliente HTTP para realizar peticiones web directas a los servidores de MinCiencias.

---

## 4. Guía de Ejecución del Sistema

El sistema puede iniciarse indistintamente mediante la interfaz gráfica de Visual Studio Code o directamente a través de la terminal.

### Opción A: Ejecución desde Visual Studio Code (Recomendada con F5)

El repositorio incluye la configuración de depuración en `.vscode/launch.json`. Para iniciar:
1. Abra la carpeta raíz del proyecto en Visual Studio Code: `Archivo > Abrir carpeta...` (o `code .`).
2. Compruebe que el intérprete de Python seleccionado corresponda al entorno virtual recién creado:
   - Presione `Ctrl + Shift + P` (o `Cmd + Shift + P` en Mac).
   - Escriba y seleccione: `Python: Select Interpreter`.
   - Elija el intérprete ubicado en `./.venv/Scripts/python.exe` (o `./.venv/bin/python`).
3. Presione la tecla **F5** (o vaya al panel lateral de *Run and Debug* `Ctrl + Shift + D` y haga clic en el botón de reproducción verde **PEA-i GUI**).
4. La ventana principal de PEA-i se abrirá automáticamente en su escritorio.

### Opción B: Ejecución desde la Terminal

Con el entorno virtual activado, ejecute cualquiera de las dos alternativas:

- **Desde la raíz del repositorio:**
  ```bash
  python python/gui/app.py
  ```

- **O ingresando a la subcarpeta `python/`:**
  ```bash
  cd python
  python gui/app.py
  ```

---

## 5. Estructura del Repositorio

A continuación se detalla la organización arquitectónica del proyecto:

```text
Taller_EstructuraDeDatos_2corte/
│
├── .vscode/
│   └── launch.json                  # Configuración de inicio rápido y depuración con F5 en VS Code
│
├── docs/
│   ├── ENTREGABLE.md                # Bitácora técnica del estado del entregable para evaluación
│   └── variables_io.md              # Diccionario detallado de variables de entrada, salida y cálculo
│
├── python/                          # NÚCLEO DEL SISTEMA EN PYTHON (GUI y Negocio)
│   ├── crud/                        # Capa lógica de operaciones CRUD
│   │   ├── crud_grupos.py           # Inserción, consulta, actualización y borrado de grupos
│   │   ├── crud_investigadores.py   # Gestión de investigadores asociados a grupos
│   │   └── crud_productos.py        # Gestión de productos académicos y categorizaciones
│   │
│   ├── datos/                       # Persistencia local de datos
│   │   ├── datos.json               # Base de datos en formato JSON (datos por defecto)
│   │   └── test.json                # Conjunto auxiliar de pruebas y validaciones
│   │
│   ├── entidades/                   # Clases de dominio del modelo
│   │   ├── grupo.py                 # Entidad Grupo de Investigación
│   │   ├── investigador.py          # Entidad Investigador
│   │   ├── producto.py              # Entidad Producto Académico (con taxonomía MinCiencias)
│   │   └── taxonomia_minciencias.py # Mapeo de categorías oficiales (GNC, DTI, ASC, FRH)
│   │
│   ├── gui/                         # Capa de presentación visual (CustomTkinter)
│   │   ├── app.py                   # Ventana principal, navegación, menús e integrador global
│   │   ├── styles.py                # Paleta de colores, tipografías, tarjetas y estilos reutilizables
│   │   ├── dialogs/                 # Modales interactivos de apoyo
│   │   │   ├── url_modal.py         # Cuadro para ingresar URLs directas de GrupLAC
│   │   │   └── cola_importacion_modal.py # Gestión visual de la Cola (Queue) de importaciones
│   │   ├── forms/                   # Formularios modales para captura y edición de datos
│   │   │   ├── grupo_form.py        # Formulario de alta y edición de grupos
│   │   │   ├── investigador_form.py # Formulario de investigadores
│   │   │   └── producto_form.py     # Formulario de productos académicos
│   │   ├── tabs/                    # Pestañas principales del panel de trabajo
│   │   │   ├── grupos_tab.py        # Tabla, búsqueda, detalle, activación y borrado de grupos
│   │   │   ├── investigadores_tab.py # Gestión y filtros de investigadores
│   │   │   ├── productos_tab.py     # Tabla y filtros avanzados de producción académica
│   │   │   └── estadisticas_tab.py  # KPIs, resumen estadístico y 4 gráficos interactivos Matplotlib
│   │   └── widgets/                 # Componentes gráficos modulares
│   │       ├── tabla_crud.py        # Tabla genérica con paginación, filtros y selección múltiple
│   │       └── ...
│   │
│   ├── modelos/                     # ESTRUCTURAS DE DATOS HECHAS A MANO (Sin librerías externas)
│   │   ├── nodo.py                  # Nodo genérico para estructuras enlazadas simples y dobles
│   │   ├── lista.py                 # Lista doblemente enlazada con punteros cabeza y cola
│   │   ├── multilista.py            # Multilista jerárquica (Grupos ➔ Investigadores ➔ Productos)
│   │   ├── pila.py                  # Pila LIFO implementada para operaciones de Deshacer (Undo)
│   │   └── cola.py                  # Cola FIFO implementada para procesamiento de importaciones
│   │
│   ├── persistencia/                # Serialización y deserialización
│   │   ├── persistencia.py          # Interfaz abstracta de persistencia
│   │   └── persistencia_json.py     # Conversión bidireccional entre JSON y la Multilista en memoria
│   │
│   ├── scraping/                    # Extracción de datos externos
│   │   └── scienti.py               # Web scraper para páginas GrupLAC de MinCiencias y parser CSV
│   │
│   └── requirements.txt             # Dependencias estrictamente necesarias (ordenadas alfabéticamente)
│
├── cpp/                             # Módulos de referencia académica implementados en C++
│   ├── estructuras.hpp              # Estructuras de datos manuales en C++
│   ├── grupos.hpp                   # Modelos de grupos en C++
│   ├── investigador.hpp             # Modelos de investigadores en C++
│   └── main.cpp                     # Ejecutable de prueba en consola C++
│
├── rust/                            # Módulo complementario CLI implementado en Rust
│   └── pea_i/                       # Proyecto Cargo de consola 100% autónomo
│
├── integrantes.md                   # Identificación de los autores del proyecto
├── README.md                        # Documento descriptivo básico del proyecto
└── MANUAL_DE_USUARIO.md             # Este manual de usuario completo
```

---

## 6. Guía de Uso de la Aplicación

La aplicación cuenta con una interfaz gráfica moderna, oscura e intuitiva, estructurada en encabezado, barra de navegación superior y área de trabajo central dinámica.

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  PEA-i — Programa Estadístico de Análisis de Investigación              [⚙ Menú] │
├──────────────────────────────────────────────────────────────────────────────────┤
│  [ 🏛 Grupos ]    [ 👤 Investigadores ]    [ 📄 Productos ]    [ 📊 Estadísticas ]│
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│                        ÁREA DE TRABAJO DE LA PESTAÑA ACTIVA                      │
│                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

### Navegación General y Menú de Opciones

En la esquina superior derecha encontrará el botón con el ícono de **Ajustes / Tuerca (⚙)**. Al pulsarlo se despliega un menú contextual con opciones globales:

- **Sección ARCHIVO:**
  - `Cargar datos (Ctrl + O)`: Permite cargar un archivo JSON externo que sustituya o alimente la multilista activa.
  - `Guardar datos (Ctrl + S)`: Vuelca el estado actual de la multilista al archivo `python/datos/datos.json`.
- **Sección DATOS:**
  - `Descargar del SCIENTI`: Dispara la extracción en segundo plano del grupo oficial preconfigurado (UPC).
  - `Cargar desde CSV`: Abre un selector de archivos para cargar lotes estructurados en formato CSV.
  - `Cola de importación`: Abre el panel de la **Cola (Queue)** para gestionar múltiples URLs por lotes.
- **Sección AYUDA:**
  - `Acerca de`: Muestra la ficha técnica del proyecto, créditos institucionales y versión.
- **Salir:** Cierra la aplicación de manera segura tras confirmar los cambios.

---

### Pestaña: Grupos de Investigación

Esta vista administra las entidades principales en la cabecera de la multilista.

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  Buscar: [ 🔍 Escriba nombre o código... ]    [+ Nuevo Grupo]  [🔄 Deshacer Borrado]│
├──────────────────────────────────────────────────────────────────────────────────┤
│ Cód. GrupLAC │ Nombre del Grupo         │ Categoría │ Líder        │ Estado      │
├──────────────┼──────────────────────────┼───────────┼──────────────┼─────────────┤
│ COL00000001  │ Grupo de Inv. GIDSE      │ A1        │ Dr. Pérez    │ [Activo]    │
│ COL00000002  │ Semillero de Software    │ B         │ Ing. Gómez   │ [Activo]    │
└──────────────────────────────────────────────────────────────────────────────────┘
```

#### Funcionalidades Disponibles:
1. **Visualización y Búsqueda:** La tabla lista todos los grupos cargados en memoria. El campo de búsqueda filtra instantáneamente por nombre o código GrupLAC sin necesidad de presionar enter.
2. **Crear Grupo (`+ Nuevo Grupo`):** Abre un formulario modal que solicita:
   - *Código GrupLAC*: Identificador único asignado por MinCiencias.
   - *Nombre del Grupo*: Denominación institucional.
   - *Categoría*: Clasificación MinCiencias (A1, A, B, C, Reconocido).
   - *Líder*: Nombre del investigador principal a cargo.
   - *Plan de Trabajo*: Descripción de objetivos y líneas de acción.
3. **Editar Grupo:** Seleccione un registro de la tabla y presione *Editar* (o haga doble clic sobre la fila) para modificar sus campos.
4. **Ver Detalle del Grupo:** Abre un modal con el plan de trabajo completo y la relación de integrantes y productos asociados a la entidad seleccionada.
5. **Activar / Desactivar:** Permite cambiar el estado lógico del grupo sin eliminar su historial.
6. **Eliminar Grupo con Pila de Deshacer (Undo):**
   - Al eliminar uno o más grupos seleccionados, el sistema almacena automáticamente los nodos eliminados en una **Pila (Stack)** propia en memoria.
   - Si cometió un error, simplemente presione el botón **Deshacer (Undo)** para restaurar de inmediato el último grupo borrado con todos sus datos intactos.

---

### Pestaña: Investigadores

Permite gestionar el talento humano perteneciente a cada grupo de investigación.

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  Buscar: [ 🔍 Cédula, nombre... ]    Filtrar por Grupo: [ Todos ▼ ]              │
├──────────────────────────────────────────────────────────────────────────────────┤
│ Cédula       │ Nombres        │ Apellidos       │ Correo             │ Grupo     │
├──────────────┼────────────────┼─────────────────┼────────────────────┼───────────┤
│ 1065595117   │ Esteban Raúl   │ Vergara Jaime   │ ervergara@...      │ GIDSE     │
│ 1118821800   │ Luis Eduardo   │ Gomes Rosales   │ luiseduardogomez@..│ GIDSE     │
└──────────────────────────────────────────────────────────────────────────────────┘
```

#### Funcionalidades Disponibles:
1. **Asociación en Multilista:** Cada investigador está estrictamente vinculado a un nodo de `Grupo`. En la estructura interna, el grupo contiene un puntero hacia su sublista enlazada de investigadores.
2. **Filtrado Dinámico:** Además de la barra de búsqueda general, dispone de un menú desplegable para aislar rápidamente a los miembros de un grupo determinado.
3. **Formulario de Registro:** Solicita número de cédula, nombres, apellidos, correo institucional y el grupo de asignación.
4. **Deshacer Borrado:** Al igual que en grupos, las eliminaciones accidentales de investigadores se apilan en la estructura LIFO para su restauración instantánea.

---

### Pestaña: Productos Académicos

Centraliza toda la producción científica generada (artículos, libros, ponencias, desarrollos de software, patentes, etc.).

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│ Filtro Rápido: (•) Todos  ( ) Últimos 2  ( ) Últimos 5  ( ) Personalizado        │
│ Gran Categoría: [ Todas ▼ ]    Validación: [ Todos ▼ ]                           │
├──────────────────────────────────────────────────────────────────────────────────┤
│ Título del Producto                │ Tipo          │ Categoría MinCiencias │ Año │
├────────────────────────────────────┼───────────────┼───────────────────────┼─────┤
│ Sistema Inteligente de Monitoreo   │ Software      │ Des. Tecnológico      │ 2024│
│ Algoritmos Eficientes en Redes     │ Artículo      │ Nuevo Conocimiento    │ 2023│
└──────────────────────────────────────────────────────────────────────────────────┘
```

#### Funcionalidades Disponibles:
1. **Taxonomía Oficial MinCiencias:** Los productos se normalizan bajo las cuatro grandes categorías del modelo de medición nacional:
   - *GNC — Generación de Nuevo Conocimiento* (artículos indexados, libros de investigación, capítulos).
   - *DTI — Desarrollo Tecnológico e Innovación* (software registrado, prototipos industriales, patentes, secretos empresariales).
   - *ASC — Apropiación Social del Conocimiento* (estrategias pedagógicas, eventos científicos, informes técnicos).
   - *FRH — Formación de Recurso Humano* (tesis de maestría/doctorado dirigidas, proyectos de grado tutorados).
2. **Filtros Temporales Segmentados:** Filtre con un solo clic los productos de los últimos 2 años, 5 años, o defina un intervalo numérico personalizado (`Año Desde` - `Año Hasta`).
3. **Filtros por Estado de Validación:** Clasifique entre productos *Validados*, *En revisión* o *No validados*.
4. **Operaciones CRUD Completas:** Adición de productos vinculados a un investigador y grupo, edición y soporte de deshacer eliminaciones.

---

### Pestaña: Estadísticas y Analítica

Proporciona un centro de mando visual y cuantitativo para auditoría académica y toma de decisiones, combinando el motor de cálculo de Pandas con gráficos de Matplotlib incrustados de forma nativa en CustomTkinter.

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│  [ 🏛 3 Grupos ]          [ 👤 18 Investigadores ]          [ 📄 45 Productos ]  │
├──────────────────────────────────────────────────────────────────────────────────┤
│  Vista: [ (•) Global  ( ) Por Grupo  ( ) Por Investigador ]  Periodo: [ Todos ▼ ]│
├──────────────────────────────────────────────────────────────────────────────────┤
│  RESUMEN DESCRIPTIVO: Total: 45 | Promedio: 2.50 | Mediana: 2.0 | Mín: 1 | Máx: 8│
├────────────────────────────────────────┬─────────────────────────────────────────┤
│ [ Gráfico 1: Productos por Año ]       │ [ Gráfico 2: Gran Categoría MinCiencias]│
├────────────────────────────────────────┼─────────────────────────────────────────┤
│ [ Gráfico 3: Top Tipos de Producto ]   │ [ Gráfico 4: Histograma de Rendimiento ]│
└──────────────────────────────────────────────────────────────────────────────────┘
```

#### Elementos Principales del Tablero:
1. **Tarjetas de Métricas Rápidas (KPIs):**
   - Muestra el total de grupos registrados y la cantidad en estado activo.
   - Total de investigadores activos vs. inactivos.
   - Total de productos científicos y porcentaje de producción validada.
2. **Selector de Perspectiva (Vista):**
   - **Vista Global:** Analiza toda la base de datos institucional en conjunto.
   - **Vista Por Grupo:** Habilita un menú para seleccionar un grupo específico y examinar su producción aislada.
   - **Vista Por Investigador:** Permite seleccionar un autor particular para auditar su trayectoria individual.
3. **Resumen Estadístico Descriptivo:**
   - Calcula métricas formales en tiempo real:
     - **Total:** Muestra poblacional evaluada.
     - **Promedio (Media aritmética):** Producción promedio por integrante.
     - **Mediana:** Punto medio de distribución de productos.
     - **Mínimo y Máximo:** Rango de dispersión de la productividad científica.
4. **Cuadrícula de 4 Gráficos Analíticos:**
   - **Gráfico 1 — Productos por Año:** Muestra la evolución histórica y tendencias de publicación a lo largo de las décadas.
   - **Gráfico 2 — Distribución por Gran Categoría:** Gráfico de barras horizontales comparando el peso relativo de *GNC*, *DTI*, *ASC* y *FRH*.
   - **Gráfico 3 — Top Tipos de Productos:** Identifica las tipologías más frecuentes (artículos, ponencias, software, consultorías).
   - **Gráfico 4 — Histograma de Productividad:** Distribución de frecuencia que ilustra cuántos investigadores producen determinado volumen de productos.
5. **Botón "Exportar PNG":**
   - Ubicado en la barra de controles de estadísticas.
   - Permite guardar una instantánea del panel en formato de imagen de alta resolución para adjuntar en informes institucionales.

---

### Módulo de Descarga y Scraping SCIENTI (MinCiencias)

El sistema cuenta con un motor autónomo de raspado web diseñado específicamente para procesar páginas públicas de **GrupLAC** de MinCiencias.

#### Procedimiento de Descarga Directa (1 Clic):
1. Haga clic en el ícono de **Ajustes (⚙)** en la parte superior derecha de la ventana.
2. Seleccione la opción **"Descargar del SCIENTI"** (o use el botón de importación directa en la pestaña Grupos).
3. La aplicación se conectará automáticamente a la URL oficial por defecto de MinCiencias (`https://scienti.minciencias.gov.co/gruplac/jsp/visualiza/visualizagr.jsp?nro=00000000002099` correspondiente al grupo de la UPC).
4. Mientras la descarga se ejecuta en un **hilo asíncrono en segundo plano (`threading.Thread`)**, la interfaz continuará respondiendo de forma fluida y se mostrará un mensaje emergente (*Toast*) amarillo indicando: *"Descargando desde SCIENTI..."*.
5. Una vez finalizada la extracción, el sistema:
   - Parsea el nombre del grupo, código, líder y plan de trabajo.
   - Extrae el listado completo de investigadores integrantes y sus cédulas.
   - Extrae los artículos, libros, software y demás productos clasificados con sus respectivos años y autores.
   - Poblará la Multilista en memoria y persistirá los cambios automáticamente en `python/datos/datos.json`.
   - Se mostrará un mensaje confirmando la cantidad de registros incorporados.

#### Descarga desde una URL Personalizada de GrupLAC:
Si desea importar cualquier otro grupo de investigación nacional registrado en MinCiencias:
1. Abra el menú de opciones o haga clic en el botón de importación personalizada.
2. Ingrese la URL completa de GrupLAC, asegurándose de que cumpla con el formato:
   ```text
   https://scienti.minciencias.gov.co/gruplac/jsp/visualiza/visualizagr.jsp?nro=XXXXXXXXXXXXXX
   ```
3. Haga clic en **Descargar**. El sistema validará la URL y procesará la página del grupo correspondiente.

---

### Cola de Importación y Carga CSV

#### Uso de la Cola de Importación (Estructura FIFO):
Para descargar múltiples grupos de investigación sin esperar manualmente por cada uno:
1. Abra el menú de ajustes **(⚙)** y seleccione **"Cola de importación"**.
2. Escriba las URLs deseadas y presione **"Encolar"**.
3. Las URLs se agregarán a una **Cola (Queue)** implementada manualmente según la disciplina *First-In, First-Out (FIFO)*.
4. Presione **"Procesar Cola"**; el sistema irá desencolando secuencialmente cada grupo e integrando la información a la multilista sin duplicar registros.

#### Carga Alternativa mediante Archivos CSV:
En caso de operar en entornos sin conexión a internet:
1. Despliegue el menú **(⚙)** y elija **"Cargar desde CSV"**.
2. Seleccione un archivo `.csv` estructurado con los campos de grupos, investigadores o productos.
3. El sistema normalizará las columnas y las insertará ordenadamente en la Multilista.

---

## 7. Solución de Problemas Comunes (FAQ / Troubleshooting)

### 1. Mensaje de error: `"No module named 'customtkinter'"` (o `'pandas'`, `'bs4'`, etc.)
- **Causa:** Las dependencias se instalaron fuera del entorno virtual, o el entorno virtual no está activado en su terminal.
- **Solución:**
  1. Verifique que al inicio de la terminal aparezca `(.venv)`.
  2. Si no aparece, actívelo ejecutando:
     - En Windows PowerShell: `.\.venv\Scripts\Activate.ps1`
     - En Linux / macOS: `source .venv/bin/activate`
  3. Ejecute nuevamente la instalación:
     ```bash
     pip install -r python/requirements.txt
     ```

### 2. Error de PowerShell: `"activate.ps1 no se puede cargar porque la ejecución de scripts está deshabilitada en este sistema"`
- **Causa:** La política de ejecución de scripts de Windows restringe scripts no firmados por seguridad.
- **Solución:** Abra PowerShell y ejecute la siguiente instrucción (aplica únicamente para la sesión actual de la terminal):
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  ```
  Luego intente activar el entorno nuevamente: `.\.venv\Scripts\Activate.ps1`.

### 3. En Linux la aplicación falla con: `ModuleNotFoundError: No module named '_tkinter'`
- **Causa:** En algunas distribuciones de Linux (como Ubuntu o Debian), Tkinter no viene preinstalado con el paquete estándar de Python.
- **Solución:** Instale el soporte de Tkinter desde el gestor de paquetes de su distribución:
  ```bash
  sudo apt-get update
  sudo apt-get install python3-tk
  ```

### 4. Al presionar F5 en Visual Studio Code no ocurre nada o falla la importación
- **Causa:** VS Code puede estar utilizando el intérprete de Python global en lugar del entorno virtual `.venv`.
- **Solución:**
  1. En VS Code, presione `Ctrl + Shift + P`.
  2. Escriba `Python: Select Interpreter`.
  3. Seleccione el intérprete correspondiente a la ruta de su entorno virtual (`./.venv/Scripts/python.exe`).
  4. Presione nuevamente **F5**.

### 5. Error al descargar desde SCIENTI: `"Error de conexión"` o `"No se pudo obtener respuesta"`
- **Causa:** El portal de MinCiencias (`scienti.minciencias.gov.co`) suele experimentar ventanas de mantenimiento o caídas temporales del servidor, o bien la conexión a internet local fue interrumpida.
- **Solución:**
  1. Verifique su acceso a internet abriendo la URL en un navegador web.
  2. Si el portal oficial está fuera de servicio temporalmente, utilice el archivo de datos precargado (`python/datos/datos.json`) o la opción de **"Cargar desde CSV"**.

### 6. La ventana de la aplicación abre pero se ve borrosa o desproporcionada
- **Causa:** En monitores de alta resolución con escalado DPI de Windows (por ejemplo, 125% o 150%), CustomTkinter ajusta automáticamente el factor de escala.
- **Solución:** Puede ajustar la escala visual desde las opciones de pantalla de Windows o maximizar la ventana para una distribución óptima de los paneles.

### 7. ¿Dónde se guardan los datos si cierro el programa?
- Toda la información ingresada o descargada se almacena en el archivo `python/datos/datos.json`. Para forzar el guardado manual en cualquier instante, presione `Ctrl + S` o use la opción **"Guardar datos"** en el menú de ajustes **(⚙)**.

---

## 8. Créditos y Autores

Proyecto académico desarrollado en el marco del programa de **Ingeniería de Sistemas** de la **Universidad Popular del Cesar (UPC)** para la asignatura de **Estructura de Datos**.

### Información Institucional:
- **Institución:** Universidad Popular del Cesar (UPC) — Valledupar, Cesar, Colombia
- **Facultad:** Facultad de Ingeniería y Tecnologías
- **Programa Académico:** Ingeniería de Sistemas
- **Asignatura:** Estructura de Datos
- **Grupo Académico:** Grupo 05

### Desarrolladores del Proyecto:
| Nombre Completo | Cédula de Ciudadanía | Correo Institucional | Rol en el Proyecto |
| :--- | :--- | :--- | :--- |
| **Esteban Raúl Vergara Jaime** | CC: 1065595117 | `ervergara@unicesar.edu.co` | Desarrollo e Integración |
| **Luis Eduardo Gomes Rosales** | CC: 1118821800 | `luiseduardogomez@unicesar.edu.co` | Desarrollo e Integración |

---
*© 2026 PEA-i — Programa Estadístico de Análisis de Investigación. Universidad Popular del Cesar.*
