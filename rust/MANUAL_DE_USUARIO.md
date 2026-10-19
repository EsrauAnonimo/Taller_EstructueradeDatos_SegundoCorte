# Manual de Usuario — PEA-i (Versión Consola en Rust)

> **Universidad Popular del Cesar (UPC)**  
> **Facultad de Ingeniería y Tecnologías — Ingeniería de Sistemas**  
> **Asignatura:** Estructura de Datos (Grupo 05)

---

## 1. Requisitos del Sistema
- **Sistema Operativo:** Windows 10/11, Linux o macOS.
- **Opción sin instalar nada:** Puedes ejecutar directamente el binario compilado `pea_i.exe` incluido en el proyecto sin necesidad de instalar Rust.
- **Para compilar desde el código fuente:**
  - **Rust y Cargo:** Versión 1.75 o superior ([rustup.rs](https://rustup.rs/)).
  - **Crates permitidos:** `serde`, `serde_json`, `csv`, `reqwest`, `scraper`, `chrono` (sin bases de datos externas).

---

## 2. Cómo Ejecutar

Elige la forma que te resulte más cómoda:

### Opción A: Desde la Terminal (PowerShell o CMD)
- **Inicio rápido en 1 comando (Recomendada en Windows):**
  - En **PowerShell**:
    ```powershell
    .\rust\ejecutar.ps1
    ```
  - En **CMD (Símbolo del sistema)** o doble clic:
    ```cmd
    .\rust\ejecutar.bat
    ```
- **Con Cargo (Compilar y ejecutar):**
  ```powershell
  cd rust/pea_i
  cargo run
  ```
- **O ejecutando directamente el binario compilado:**
  ```powershell
  cd rust/pea_i
  .\target\debug\pea_i.exe
  ```

### Opción B: Desde Visual Studio Code (o cualquier IDE)
1. Abre la carpeta del proyecto en VS Code.
2. Abre la terminal integrada con el atajo ``Ctrl + ` `` (o `Terminal > New Terminal`).
3. Ejecuta cualquiera de las dos alternativas:
   - Directo con el script:
     ```powershell
     .\rust\ejecutar.ps1
     ```
   - O con Cargo:
     ```powershell
     cd rust/pea_i
     cargo run
     ```
4. *(Opcional)* Si tienes instalada la extensión oficial **rust-analyzer**, abre [rust/pea_i/src/main.rs](file:///c:/Users/Esteb/OneDrive/Documentos/Taller_EstructuraDeDatos_2corte/rust/pea_i/src/main.rs) y haz clic en el botón interactivo **▶ Run** que aparece flotando encima de `fn main()`.

---

## 3. ¿Qué hace la aplicación? (Uso Breve)

El programa se ejecuta **100% en la terminal** mediante un menú interactivo numérico (opciones 1 a 8) y gestiona los datos en una **Multilista jerárquica en memoria** con persistencia en formato JSON (compatible con la versión Python).

### Menú Principal de Opciones:

- **`[1] Gestión de Grupos de Investigación`**
  - Listar grupos activos e inactivos.
  - Buscar por código GrupLAC o nombre.
  - Crear y editar información (código, líder, categoría A1-C, plan de trabajo).
  - Activar / desactivar lógicamente y eliminar con soporte de deshacer.

- **`[2] Gestión de Investigadores`**
  - Listar todos los investigadores o filtrar por grupo.
  - Registrar nuevos investigadores con validación de cédula única y asignación a un grupo existente.

- **`[3] Gestión de Productos Académicos`**
  - Registro de artículos, software, libros, ponencias, etc.
  - Categorización oficial MinCiencias (*GNC*, *DTI*, *ASC*, *FRH*).
  - Filtro por estados de validación y por años de publicación.

- **`[4] Estadísticas y Analítica en Consola`**
  - Tarjetas de KPIs globales (conteo de grupos, investigadores y productos).
  - Resumen estadístico descriptivo (promedio, mediana, mínimo y máximo).
  - **Gráficos en arte ASCII:** Renderiza gráficos de barras horizontales directamente en la terminal (evolución por años y distribución por gran categoría).

- **`[5] Deshacer Última Eliminación (Undo)`**
  - Si borraste accidentalmente un grupo, investigador o producto, esta opción desapila el último elemento borrado y lo restaura inmediatamente en la jerarquía.

- **`[6] Importar desde MinCiencias / SCIENTI`**
  - **Descarga directa:** Extrae en vivo la información pública del grupo oficial GrupLAC (MinCiencias) usando web scraping HTTP (`reqwest` + `scraper`).
  - **Descarga personalizada:** Permite ingresar cualquier URL de GrupLAC.
  - **Cola de Importación:** Procesa lotes de enlaces de forma secuencial mediante una Cola (FIFO).

- **`[7] Importar / Exportar CSV`**
  - Carga masiva y exportación de datos en formato tabular `.csv`.

- **`[8] Guardar Cambios y Salir`**
  - Guarda el estado completo en el archivo `python/datos/datos.json` (o archivo local) y finaliza la sesión.

---

## 4. Estructuras de Datos Utilizadas (Requisitos del Proyecto)

El modelo en memoria **no utiliza** colecciones estándar de alto nivel (`Vec`, `VecDeque`, `HashMap`) como almacenamiento principal. Todas las estructuras fueron implementadas **a mano** en `src/modelos/`:

| Estructura | Archivo | ¿Dónde y cómo se usa en el programa? |
| :--- | :--- | :--- |
| **Multilista en 3 Niveles** | `src/modelos/multilista.rs` | Núcleo del modelo: conecta `GrupoNode ➔ InvestigatorNode ➔ ProductNode`. Utiliza punteros inteligentes `Rc<RefCell<...>>` para enlace hacia adelante y `Weak<RefCell<...>>` para enlace hacia atrás, evitando fugas de memoria (*memory leaks*) por ciclos de referencia en Rust. |
| **Lista Doblemente Enlazada** | `src/modelos/lista.rs` | Estructura lineal genérica con punteros anterior y siguiente para recorridos bidireccionales eficientes. |
| **Pila (Stack - LIFO)** | `src/modelos/pila.rs` | Historial de **Deshacer (Undo)**. Al eliminar cualquier entidad se apila (`push`), y con la opción [5] se desapila (`pop`) restaurándola en la multilista. |
| **Cola (Queue - FIFO)** | `src/modelos/cola.rs` | **Cola de Importación** de URLs de MinCiencias. Encola enlaces (`enqueue`) y los procesa secuencialmente uno a uno (`dequeue`). |

---

## 5. Solución de Problemas Frecuentes

| Problema | Solución |
| :--- | :--- |
| En Windows CMD los caracteres con tildes o símbolos se ven extraños | Ejecuta en la consola el comando `chcp 65001` antes de iniciar para activar codificación UTF-8. |
| Error: `'cargo'` no se reconoce como comando ejecutable | Rust no está en el PATH de la terminal actual. Usa `.\rust\ejecutar.ps1` o ejecuta directamente `.\rust\pea_i\target\debug\pea_i.exe`. |
| PowerShell bloquea la ejecución de `ejecutar.ps1` | Ejecuta en la terminal: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`. |
| Error de conexión al descargar de SCIENTI | Verifica tu conexión a internet o comprueba si la plataforma de MinCiencias está en mantenimiento temporal. |
| ¿Dónde se guardan los datos? | Se guardan en formato JSON compatible con la versión gráfica de Python (`python/datos/datos.json`). |

---

## 6. Autores

Proyecto desarrollado para la asignatura **Estructura de Datos (Grupo 05)** — **Universidad Popular del Cesar (UPC)**:

- **Esteban Raúl Vergara Jaime** — CC: 1065595117 — `ervergara@unicesar.edu.co`
- **Luis Eduardo Gomes Rosales** — CC: 1118821800 — `luiseduardogomez@unicesar.edu.co`
