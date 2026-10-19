# PEA-i — Programa Estadístico de Análisis de Investigación

> **Universidad Popular del Cesar (UPC)**  
> **Facultad de Ingenierías y Tecnológicas — Ingeniería de Sistemas**  
> **Asignatura:** Estructura de Datos (Grupo 05)  
> **Evaluación:** Taller 2 — Segundo Corte  
> **Docente Titular:** Ing. Adith Pérez

---

## 📌 Descripción General

**PEA-i** es un sistema integral para la gestión, estructuración, análisis y auditoría de información científica institucional (Grupos de Investigación, Investigadores y Productos Académicos) bajo la taxonomía oficial de **MinCiencias** (GrupLAC / Scienti).

El núcleo del proyecto gira en torno a la implementación **desde cero y a mano** de estructuras de datos no lineales y lineales (sin depender de bases de datos relacionales ni colecciones de alto nivel para el modelo), aplicadas de forma consistente en **tres ecosistemas tecnológicos**:

1. 🐍 **Python:** Aplicación de escritorio moderna con interfaz gráfica rica en CustomTkinter, analítica visual con Matplotlib/Pandas, Web Scraping automatizado en vivo y persistencia JSON.
2. ⚡ **C++ (C++17):** Sistema en terminal interactiva de alto rendimiento con menús formateados, tablas de estadísticas con `<iomanip>`, auditoría de historial en Pila y cola de validación FIFO, con persistencia CSV.
3. 🦀 **Rust (Edición 2021):** Solución de consola orientada a seguridad de memoria, concurrencia y cero fugas (*zero leaks*) mediante punteros inteligentes (`Rc<RefCell<...>>` y `Weak`), scraping con `reqwest`/`scraper` y gráficos en arte ASCII.

---

## 🏗️ Estructuras de Datos Implementadas (Requisitos del Taller)

Todas las estructuras fueron implementadas a nivel de punteros y referencias en cada lenguaje:

| Estructura | Propósito en el Sistema | Python | C++ | Rust |
| :--- | :--- | :--- | :--- | :--- |
| **Multilista Jerárquica** | Modelo central en memoria: `Grupo ➔ Investigadores ➔ Productos` con relaciones de pertenencia. | `python/modelos/multilista.py` | `cpp/grupos.hpp` | `rust/pea_i/src/modelos/multilista.rs` |
| **Lista Enlazada** | Almacenamiento dinámico bidireccional / simple de entidades y nodos. | `python/modelos/lista.py` | `cpp/estructuras.hpp` | `rust/pea_i/src/modelos/lista.rs` |
| **Pila (Stack — LIFO)** | Mecanismo de **Deshacer (Undo)** y auditoría histórica de operaciones. | `python/modelos/pila.py` | `cpp/grupos.hpp` | `rust/pea_i/src/modelos/pila.rs` |
| **Cola (Queue — FIFO)** | **Cola de Importación** masiva desde URLs de MinCiencias y validación secuencial. | `python/modelos/cola.py` | `cpp/grupos.hpp` | `rust/pea_i/src/modelos/cola.rs` |

---

## 📁 Estructura del Repositorio

```text
Taller_EstructuraDeDatos_2corte/
│
├── python/                     # Solución principal con GUI (CustomTkinter)
│   ├── EV_LG.py                # Lanzador principal y ventana de la app
│   ├── MANUAL_DE_USUARIO.md    # Manual detallado de usuario (Python)
│   ├── crud/                   # Capa CRUD (Grupos, Investigadores, Productos)
│   ├── datos/                  # Base de datos persistente (datos.json)
│   ├── entidades/              # Clases de dominio y taxonomía MinCiencias
│   ├── gui/                    # Interfaz gráfica (tabs, forms, dialogs, styles)
│   ├── modelos/                # Multilista, Lista, Pila, Cola y Nodo
│   ├── persistencia/           # Serializador y cargador JSON
│   └── scraping/               # Extractor web de GrupLAC (Scienti)
│
├── cpp/                        # Solución interactiva de consola en C++17
│   ├── main.cpp                # Programa principal y menú interactivo de 19 opciones
│   ├── estructuras.hpp         # Nodos, Producto y ListaEnlazada genérica
│   ├── grupos.hpp              # Multilista Grupo, Pila y Cola
│   ├── investigador.hpp        # Entidad Investigador
│   ├── datos.csv               # Archivo plano de persistencia
│   ├── programa.exe            # Binario precompilado listo para ejecutar
│   └── MANUAL_DE_USUARIO.md    # Manual con diagramas Mermaid (C++)
│
├── rust/                       # Solución de consola en Rust
│   ├── pea_i/                  # Proyecto Cargo completo
│   ├── ejecutar.ps1            # Script de ejecución rápida para PowerShell
│   ├── ejecutar.bat            # Script de ejecución rápida para CMD
│   └── MANUAL_DE_USUARIO.md    # Manual de usuario (Rust)
│
├── docs/                       # Documentación académica formal
│   └── Taller2_PEAi_EV_LG_Completo.docx  # Informe técnico final con anexos
│
├── integrantes.md              # Identificación formal del grupo y entrega
└── README.md                   # Esta guía general
```

---

## 🚀 Guía de Inicio Rápido por Lenguaje

### 1. 🐍 Versión Python (Interfaz Gráfica de Escritorio)

#### Requisitos
- Python 3.10 o superior ([python.org](https://www.python.org/downloads/)).

#### Instalación de librerías
Abre una terminal en la raíz del proyecto o dentro de `python/`:

```bash
# Crear y activar entorno virtual (Recomendado)
python -m venv .venv
.\.venv\Scripts\activate      # En Windows PowerShell / CMD
# source .venv/bin/activate     # En Linux / macOS

# Instalar dependencias necesarias
pip install customtkinter matplotlib pandas requests beautifulsoup4 pillow
```

#### Ejecución
```bash
# Opción 1: Directo con Python
python python/EV_LG.py

# Opción 2: Desde VS Code
# Abre el proyecto y presiona la tecla F5 (configuración "PEA-i GUI")
```

📖 **Consulta la documentación completa en:** [python/MANUAL_DE_USUARIO.md](python/MANUAL_DE_USUARIO.md)

---

### 2. ⚡ Versión C++ (Consola Interactiva)

#### Opción Inmediata (Sin instalar nada en Windows)
Ejecuta directamente el archivo binario compilado incluido en la carpeta:

```powershell
cd cpp
.\programa.exe
```

#### Para recompilar desde el código fuente
Requiere un compilador con soporte C++17 (`g++` / MinGW, `clang++` o MSVC):

```bash
g++ -std=c++17 -Wall -Wextra -I cpp cpp/main.cpp -o cpp/programa.exe
.\cpp\programa.exe
```

📖 **Consulta la documentación completa en:** [cpp/MANUAL_DE_USUARIO.md](cpp/MANUAL_DE_USUARIO.md)

---

### 3. 🦀 Versión Rust (Consola Interactiva)

#### Opción Inmediata con Scripts
- **PowerShell:** `.\rust\ejecutar.ps1`
- **CMD:** `.\rust\ejecutar.bat`

#### Con Cargo
Requiere Rust 1.75+ instalado ([rustup.rs](https://rustup.rs/)):

```powershell
cd rust/pea_i
cargo run
```

📖 **Consulta la documentación completa en:** [rust/MANUAL_DE_USUARIO.md](rust/MANUAL_DE_USUARIO.md)

---

## 💾 Persistencia de Datos

- **Persistencia JSON (`python/datos/datos.json`):** Almacena el árbol completo en formato estructurado JSON. Es compatible con operaciones de guardado automático y recuperación ante reinicios del sistema.
- **Persistencia CSV (`cpp/datos.csv`):** Almacena los registros con formato de texto plano tipificado (`GRUPO`, `INVESTIGADOR`, `PRODUCTO`) permitiendo portabilidad con suites como Excel.

---

## 👥 Autores

Trabajo realizado para la asignatura **Estructura de Datos (Grupo 05)** — **Universidad Popular del Cesar (UPC)**:

| Integrante | Documento (CC) | Correo Institucional | Rol Principal |
| :--- | :---: | :--- | :--- |
| **Esteban Raúl Vergara Jaime** | 1065595117 | `ervergara@unicesar.edu.co` | Arquitectura GUI Python, Multilista, Web Scraping, Persistencia JSON y Documentación |
| **Luis Eduardo Gómez Rosales** | 1118821800 | `luiseduardogomez@unicesar.edu.co` | Desarrollo C++, Estructuras de Datos (Pila, Cola, Listas), Persistencia CSV y Documentación |
| **LINK DEL VIDEO :**           | https://youtu.be/AXiJqifF1NA|
- **Docente:** Ing. Adith Pérez  
- **Entrega Académica:** Octubre de 2026 — Valledupar, Cesar, Colombia
