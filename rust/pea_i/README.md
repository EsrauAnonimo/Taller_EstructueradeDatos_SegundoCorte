# PEA-i — Plataforma de Investigación (Versión Rust)

Versión 100% por consola (terminal) del sistema PEA-i, desarrollada en **Rust** con la misma funcionalidad, campos y reglas de negocio que la versión de Python, pero utilizando **estructuras de datos propias en memoria**.

---

## 📌 ¿Qué hace el programa?

El programa gestiona de manera jerárquica grupos de investigación, sus investigadores adscritos y los productos científicos categorizados según el modelo de **MinCiencias Colombia (GrupLAC / Scienti)**:

1. **CRUD Completo de Grupos:** Creación, consulta por código/ID, edición, activación/desactivación lógica y eliminación física.
2. **CRUD Completo de Investigadores:** Validación de cédula única, adscripción a grupos, listados filtrados y vinculación de autoría.
3. **CRUD Completo de Productos:** Clasificación por tipología, gran categoría MinCiencias (`GNC`, `DTI`, `ASC`, `FRH`), gestión de estados (`Validado`, `No validado`, `En revisión`) y filtros por año/rango.
4. **Pila de Deshacer (Undo Stack - LIFO):** Permite deshacer eliminaciones físicas de grupos, investigadores y productos, reinsertándolos intactos en la jerarquía.
5. **Cola de Importación (FIFO Queue):** Procesamiento por lotes de enlaces web de GrupLAC (scraping automatizado con `reqwest` y `scraper`) y archivos CSV locales.
6. **Dashboard de Analítica y Estadísticas:** KPIs de grupos/investigadores/productos, cálculo descriptivo (media, mediana, mínimo, máximo), histograma de productividad y gráficos de barras horizontales en ASCII por consola.
7. **Persistencia e Interoperabilidad:** Compatible con el archivo `datos.json` de la versión Python y exportación de toda la base a CSV.

---

## 🧠 Estructuras de Datos Propias

El modelo principal **no utiliza** `Vec`, `VecDeque` ni `HashMap` como almacenamiento:
- **Multilista en 3 Niveles:**
  - Nivel 1: `GrupoNode` (Grupos enlazados doblemente).
  - Nivel 2: `InvestigatorNode` (Sublista de integrantes por grupo).
  - Nivel 3: `ProductNode` (Sublista de productos por investigador).
  - Se utilizan punteros `Rc<RefCell<...>>` hacia adelante y `Weak<RefCell<...>>` hacia atrás para evitar **ciclos de referencia y fugas de memoria (memory leaks)** en Rust.
- **Pila (`Stack<T>`):** Implementación enlazada dinámica mediante `Box<StackNode<T>>` para el historial de operaciones de eliminación.
- **Cola (`Queue<T>`):** Implementación con punteros `front` y `rear` mediante `Rc<RefCell<...>>` para el procesamiento secuencial FIFO.
- **Lista doble (`DoublyLinkedList<T>`):** Implementación canónica doblemente enlazada con `Rc`/`Weak`.

---

## 🚀 Cómo Correr el Programa

### Opción 1: Con Cargo (Recomendada)

Desde la terminal (PowerShell o CMD), ingresa a la carpeta del proyecto y ejecuta:

```powershell
cd rust/pea_i
cargo run
```

### Opción 2: Ejecutar directamente el binario compilado

El ejecutable ya se encuentra compilado en la carpeta `target/debug/`:

```powershell
cd rust/pea_i
.\target\debug\pea_i.exe
```

---

## 📂 Estructura del Código Modular

```text
rust/pea_i/
├── Cargo.toml                  # Configuración y crates permitidos
├── src/
│   ├── main.rs                 # Punto de entrada y carga automática de datos.json
│   ├── modelos/
│   │   ├── entidades.rs        # Structs Grupo, Investigador, Producto y Taxonomía
│   │   ├── nodo.rs             # Nodo genérico doblemente enlazado
│   │   ├── lista.rs            # DoublyLinkedList propia
│   │   ├── pila.rs             # Stack propia para Deshacer
│   │   ├── cola.rs             # Queue propia para Cola de Importación
│   │   └── multilista.rs       # Multilista jerárquica Grupo -> Investigador -> Producto
│   ├── crud/
│   │   ├── crud_grupos.rs
│   │   ├── crud_investigadores.rs
│   │   └── crud_productos.rs
│   ├── importacion/
│   │   ├── scienti.rs          # Scraper HTTP de GrupLAC (reqwest + scraper)
│   │   ├── csv_import.rs       # Parser CSV
│   │   └── cola_trabajo.rs     # Despachador de tareas FIFO
│   ├── estadisticas/
│   │   ├── analitica.rs        # KPIs, descriptivas, conteos y filtros
│   │   └── ascii_charts.rs     # Renderizado de gráficos de barras y tablas en consola
│   ├── persistencia/
│   │   ├── persistencia_json.rs# Lectura/escritura JSON compatible con Python
│   │   └── persistencia_csv.rs # Exportación tabular CSV
│   └── menu/
│       └── consola.rs          # Menú interactivo por consola (opciones 1 a 8)
```
