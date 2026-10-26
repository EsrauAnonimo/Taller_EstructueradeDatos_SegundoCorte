# Registro de Cambios e Incremento Funcional — Parcial 2 vs Taller 2

**Institución:** Universidad Popular del Cesar (UPC), Valledupar, Colombia  
**Facultad:** Facultad de Ingenierías y Tecnologías  
**Programa:** Ingeniería de Sistemas  
**Asignatura:** Estructura de Datos (Grupo 05) — Segundo Corte  
**Fecha:** Octubre de 2026  
**Autores / Estudiantes:**  
- **Esteban Raúl Vergara Jaime** — C.C. 1065595117 — `ervergara@unicesar.edu.co`  
- **Luis Eduardo Gómez Rosales** — C.C. 1118821800 — `luiseduardogomez@unicesar.edu.co`  

---

## 1. Resumen Ejecutivo

El presente documento detalla formalmente todas las adiciones, modificaciones y extensiones arquitectónicas implementadas en el **Parcial 2** con respecto a la solución base desarrollada previamente en el **Taller 2**.

El sistema **PEA-i (Plataforma para la Evaluación y Analítica de la Investigación)** gestiona en memoria dinámica una estructura jerárquica de tipo **Multilista** (`Grupo` $\rightarrow$ `Investigador` $\rightarrow$ `Producto`), complementada con una **Pila (LIFO)** para historial de operaciones y reversión (*Undo*), y una **Cola (FIFO)** para la atención secuencial de productos pendientes de validación.

Para el Parcial 2, se integró el modelo oficial de **MinCiencias Colombia** para el **Cálculo del Indicador de Producción Científica**, tanto en la implementación de interfaz gráfica (**Python / CustomTkinter**) como en la implementación de consola de alto rendimiento (**C++**), respaldado por especificación técnica formal bajo el estándar **IEEE 830** y diagramas **UML**.

---

## 2. Nuevos Campos en el Modelo de Datos (Entidad Producto)

En el Taller 2, la entidad `Producto` gestionaba atributos descriptivos básicos (identificador, título, año, tipo, categoría textual y estado booleano de validación). 

Para dar cumplimiento a los requerimientos del Parcial 2, se ampliaron las clases y estructuras en ambos lenguajes:

### 2.1 Campos Incorporados
1. **`peso_relativo` (`float` en Python / `double` en C++):**
   - Representa la ponderación o factor de peso asignado individualmente al producto científico, según la taxonomía y variable MinCiencias a la que pertenece (por ejemplo: `3.7` para artículos *Top / A1*, `2.3` para artículos *A / A2*, `1.0` para tesis doctorales, etc.).
2. **`puntaje` (`float` en Python / `double` en C++):**
   - Representa la calificación neta o aporte del producto al indicador final. 
   - **Regla de negocio:** Si el producto se encuentra validado (`validado == True`), `puntaje = peso_relativo`; en caso contrario (producto en cola o rechazado), `puntaje = 0.0`.

### 2.2 Impacto en el Código
- **Python (`Parcial_2/python/entidades/producto.py`):**
  - Constructor `__init__`: Parámetros `peso_relativo=0.0` y `puntaje=0.0`.
  - Serialización `to_dict()` y deserialización `from_dict()`: Se persisten ambos campos en `datos.json` manteniendo compatibilidad hacia atrás mediante valores por defecto.
- **C++ (`cpp/estructuras.hpp`):**
  - Estructura `struct Producto`: Incorporación de `double peso_relativo = 0.0;` y `double puntaje = 0.0;`.
  - Sobrecarga del operador `operator<<` y persistencia en `datos.csv` para incluir los nuevos atributos.

---

## 3. Fórmula del Indicador de Producción Científica (MinCiencias)

La lógica de evaluación adopta la formulación paramétrica oficial establecida en el *Modelo de Medición de Grupos de Investigación, Desarrollo Tecnológico o de Innovación y de Reconocimiento de Investigadores* de MinCiencias Colombia:

$$\text{Indicador} = 3.7 \cdot Nc\_Top + 2.3 \cdot Nc\_A + 0.4 \cdot Nc\_B + 1.5 \cdot AP + 0.5 \cdot DPC + 1.0 \cdot Fr\_A + 0.2 \cdot Fr\_B + 0.1 \cdot Cohe + 0.3 \cdot Coop$$

### 3.1 Desglose de Variables y Coeficientes

| Variable | Coeficiente | Componente MinCiencias | Tipos de Productos Asociados |
| :---: | :---: | :--- | :--- |
| **$Nc\_Top$** | **3.7** | Generación de Nuevo Conocimiento (Top) | Artículos en revistas indexadas A1, libros resultado de investigación de alta calidad. |
| **$Nc\_A$** | **2.3** | Generación de Nuevo Conocimiento (Tipo A) | Artículos en revistas indexadas A2 y categoría A, capítulos de libro de investigación. |
| **$Nc\_B$** | **0.4** | Generación de Nuevo Conocimiento (Tipo B) | Artículos en revistas indexadas categoría B. |
| **$AP$** | **1.5** | Apropiación Social del Conocimiento | Artículos en revistas C, procesos de apropiación social, informes técnicos finales. |
| **$DPC$** | **0.5** | Divulgación Pública y Desarrollo Tecnológico | Obras de divulgación, consultorías científico-tecnológicas, prototipos y patentes. |
| **$Fr\_A$** | **1.0** | Formación de Talento Humano (Posgrado) | Dirección de tesis de Doctorado y trabajos de grado de Maestría. |
| **$Fr\_B$** | **0.2** | Formación de Talento Humano (Pregrado) | Dirección de trabajos de grado de Pregrado y tutorías de semillero. |
| **$Cohe$** | **0.1** | Cohesión Interna | Indicador de articulación y colaboración entre los investigadores del mismo grupo. |
| **$Coop$** | **0.3** | Cooperación Internacional e Interinstitucional | Alianzas y coautorías con entidades externas y redes de investigación global. |

---

## 4. Nueva Funcionalidad en Python (GUI y Lógica)

En la solución de Python (`Parcial_2/python/`):

### 4.1 Módulo Motor de Cálculo (`indicadores.py`)
Se construyó un nuevo módulo modular e independiente que contiene:
- `mapear_categoria_variable(categoria, tipo)`: Determina la variable MinCiencias y el peso relativo aplicable.
- `asignar_puntaje_producto(producto)`: Asigna `peso_relativo` y `puntaje` al producto según su validez.
- `calcular_indicador_grupo(multilista, grupo_id, anio_min, anio_max)`: Recorre los investigadores del grupo y todos sus productos a través de los nodos de la multilista, acumulando conteos, subtotales y total general.
- `calcular_indicador_investigador(multilista, inv_id, anio_min, anio_max)`: Evalúa la sublista de productos del investigador especificado.
- `calcular_formula_indicador(...)`: Aplica la suma ponderada de la fórmula MinCiencias.
- Soporte para **filtros temporales por año** (todos los años, últimos 3 años, últimos 5 años, rango personalizado).

### 4.2 Nueva Pestaña Interactiva en GUI (`gui/tabs/indicadores_tab.py`)
Se incorporó la pestaña **"Indicadores"** a la navegación lateral del sistema con los siguientes componentes:
1. **Tarjeta de Selección y Control:**
   - Selector tipo *SegmentedButton* para conmutar entre **"Grupo"** e **"Investigador"**.
   - Menú desplegable (*ComboBox*) dinámico que lista las entidades cargadas en la multilista activa (`[ID] Nombre`).
   - Botón de cálculo (*Calcular Indicador*) y botón de refresco en caliente (*⟳ Actualizar*).
   - Barra de filtro por año (selector de ventana temporal y campos numéricos *Desde / Hasta*).
2. **Fila de 4 Tarjetas KPI Dinámicas:**
   - **Indicador Total:** Puntaje final acumulado calculado con precisión flotante.
   - **Total Productos:** Cantidad global y subtotal de productos validados para la medición.
   - **Nuevo Conocimiento Top / A:** Conteo consolidado de productos de máxima categorización ($Nc\_Top + Nc\_A$).
   - **Entidad Evaluada:** Nombre, tipo y estado de la entidad analizada.
3. **Panel de Desglose de la Fórmula MinCiencias:**
   - Tabla interactiva con columnas: *Variable*, *Componente MinCiencias*, *Peso*, *Conteo / Valor* y *Subtotal*.
4. **Tabla de Productos Detallados:**
   - Lista tabular de todos los productos de la entidad con *ID*, *Título*, *Tipo*, *Categoría*, *Peso Relativo*, *Puntaje* y *Estado de Validación*.

### 4.3 Integración en la Aplicación Principal (`Parcial2_ERV_LGR.py`)
- Se agregó `"Indicadores"` al listado de secciones `_TAB_NAMES` y al diccionario `SECTION_METADATA`.
- Integración en `_build_views()` e instanciación con inyección de la referencia de la aplicación (`IndicadoresTab(..., app=self)`).

---

## 5. Nueva Funcionalidad en C++ (Consola de Alto Rendimiento)

En la solución de C++ (`cpp/`):

### 5.1 Nueva Opción de Menú Principal
Se añadió en el menú interactivo de consola la opción:
```text
19) Calcular indicador (Parcial 2)
```

### 5.2 Modos de Evaluación Disponibles
Al ingresar a la opción 19, el sistema despliega un submenú con tres posibilidades:
1. **Calcular indicador de un Grupo:**
   - Solicita el ID del grupo y opcionalmente el filtro de años (todos, últimos 3, últimos 5 o rango personalizado).
   - Recorre la multilista (`GrupoNode` $\rightarrow$ `InvestigadorNode` $\rightarrow$ `ProductoNode`).
   - Muestra una tabla ANSI formateada con `std::setw` que desglosa cada variable, su peso, cantidad de productos, subtotal aportado y el total general.
2. **Calcular indicador de un Investigador:**
   - Permite seleccionar un investigador individual y analiza su sublista directa de productos.
3. **Comparativa de Indicadores de Grupos Activos:**
   - Genera una tabla comparativa consolidada que lista todos los grupos activos con su líder, número de investigadores, total de productos y su indicador global ordenable.

---

## 6. Nueva Documentación y Especificación Formal

Se elaboró y anexó el documento formal de ingeniería de software en `Parcial_2/docs/Requisitos_Parcial2.md`:

1. **Estándar IEEE 830-1998:**
   - Especificación formal de Requisitos Funcionales (**RF-01** a **RF-09**), cubriendo la multilista dinámica, los nuevos campos de producto, el mapeo de categorías, el cálculo del indicador, la GUI interactiva, la opción de consola C++, la pila LIFO, la cola FIFO y la persistencia dual.
   - Especificación de Requisitos No Funcionales (**RNF-01** a **RNF-05**), estableciendo límites de tiempo de cálculo ($O(1)$ en cabeza, $<50$ ms en cálculo), liberación rigurosa de memoria dinámica en C++, usabilidad y portabilidad.
2. **Diagramas UML Formales (Mermaid):**
   - **Diagrama de Casos de Uso:** Mapeo de actores (*Investigador / Evaluador*) con casos de uso clave (`Calcular Indicador`, `Mapear Categorías`, `Gestionar Multilista`, `Deshacer con Pila`, `Procesar Cola de Validación`).
   - **Diagrama de Secuencia:** Flujo paso a paso desde la interacción en la interfaz hasta la consulta en la multilista, la asignación de puntajes producto por producto, la ejecución matemática de la fórmula y el renderizado final de resultados.

---

## 7. Cuadro Comparativo: Taller 2 vs. Parcial 2

| Dimensión / Componente | Taller 2 (Solución Base) | Parcial 2 (Solución Extendida) |
| :--- | :--- | :--- |
| **Ubicación en el Repositorio** | Carpeta `Taller_2/python/` | Carpeta `Parcial_2/python/` y `Parcial_2/docs/` |
| **Archivo Principal (Python)** | `Taller2_ERV_LGR.py` (anteriormente `EV_LG.py`) | `Parcial2_ERV_LGR.py` |
| **Campos en `Producto`** | `id`, `titulo`, `anio`, `tipo`, `categoria`, `validacion`, `activo` | Se adicionan `peso_relativo` y `puntaje` |
| **Cálculo de Indicador** | No implementado | Fórmula MinCiencias ($3.7\cdot Nc\_Top + \dots$) totalmente funcional |
| **Interfaz Gráfica (Python)** | 4 pestañas (Grupos, Investigadores, Productos, Estadísticas) | **5 pestañas:** Pestaña dedicada **"Indicadores"** con KPIs, desglose y filtros |
| **Consola (C++)** | Menú con operaciones CRUD, importación y reportes básicos | Menú extendido con opción **`19) Calcular indicador (Parcial 2)`** y comparativa |
| **Filtros Temporales** | Filtros fijos básicos | Filtros dinámicos por años (Todos, últimos 3 años, últimos 5 años, rango) |
| **Especificación de Software** | Documento Word general | **IEEE 830 formal (`Requisitos_Parcial2.md`)** con requisitos RF/RNF y diagramas UML |

---

*Documento técnico elaborado y aprobado por el equipo de desarrollo para la sustentación del Parcial 2.*