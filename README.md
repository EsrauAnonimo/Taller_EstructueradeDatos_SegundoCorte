# Estructura de Datos — Segundo Corte (UPC)

**Estudiantes:** Esteban Raúl Vergara Jaime y Luis Eduardo Gómez Rosales.  
**Video Explicativo:** https://youtu.be/AXiJqifF1NA  
**Docente Titular:** Ing. Adith Pérez  
**Asignatura:** Estructura de Datos (Grupo 05)

Este repositorio contiene la entrega académica completa dividida en:
- `Taller_2/`: Solución base del taller (sin el indicador de MinCiencias).
- `Parcial_2/`: Solución completa del parcial (incluye cálculo de Indicador Científico MinCiencias, filtros temporales, exclusión de no validados/inactivos, dataset de verificación y arranque modal).

⚠️ **Consulta el archivo [CAMBIOS_PARCIAL.md](CAMBIOS_PARCIAL.md) para ver el desglose detallado de los cambios aplicados entre el Taller 2 y el Parcial 2.**

---

# PEA-i — Programa Estadístico de Análisis de Investigación

> **Universidad Popular del Cesar (UPC)**  
> **Facultad de Ingenierías y Tecnológicas — Ingeniería de Sistemas**  
> **Asignatura:** Estructura de Datos (Grupo 05)  
> **Docente Titular:** Ing. Adith Pérez

---

## 📌 Descripción General

**PEA-i** es un sistema integral para la gestión, estructuración, análisis y auditoría de información científica institucional (Grupos de Investigación, Investigadores y Productos Académicos) bajo la taxonomía oficial de **MinCiencias** (GrupLAC / Scienti).

El núcleo del proyecto gira en torno a la implementación **desde cero y a mano** de estructuras de datos no lineales y lineales (sin depender de bases de datos relacionales ni colecciones de alto nivel para el modelo), aplicadas de forma consistente en **tres ecosistemas tecnológicos**:

1. 🐍 **Python:** Aplicación de escritorio moderna con interfaz gráfica en CustomTkinter, analítica visual con Matplotlib/Pandas, Web Scraping automatizado en vivo y persistencia JSON.
2. ⚡ **C++ (C++17):** Sistema en terminal interactiva de alto rendimiento con menús formateados, tablas de estadísticas con `<iomanip>`, auditoría de historial en Pila y cola de validación FIFO, con persistencia CSV.
3. 🦀 **Rust (Edición 2021):** Solución de consola orientada a seguridad de memoria, concurrencia y cero fugas (*zero leaks*) mediante punteros inteligentes (`Rc<RefCell<...>>` y `Weak`), scraping con `reqwest`/`scraper` y gráficos en arte ASCII.

---

## 🏗️ Estructuras de Datos Implementadas

Todas las estructuras fueron implementadas a nivel de punteros y referencias en cada lenguaje:

| Estructura | Propósito en el Sistema | Python | C++ | Rust |
| :--- | :--- | :--- | :--- | :--- |
| **Multilista Jerárquica** | Modelo central en memoria: `Grupo ➔ Investigadores ➔ Productos` con relaciones de pertenencia. | `Parcial_2/python/modelos/multilista.py` | `cpp/grupos.hpp` | `rust/pea_i/src/modelos/multilista.rs` |
| **Lista Enlazada** | Almacenamiento dinámico bidireccional / simple de entidades y nodos. | `Parcial_2/python/modelos/lista.py` | `cpp/estructuras.hpp` | `rust/pea_i/src/modelos/lista.rs` |
| **Pila (Stack — LIFO)** | Mecanismo de **Deshacer (Undo)** y auditoría histórica de operaciones. | `Parcial_2/python/modelos/pila.py` | `cpp/grupos.hpp` | `rust/pea_i/src/modelos/pila.rs` |
| **Cola (Queue — FIFO)** | **Cola de Importación** masiva desde URLs de MinCiencias y validación secuencial. | `Parcial_2/python/modelos/cola.py` | `cpp/grupos.hpp` | `rust/pea_i/src/modelos/cola.rs` |

---

## 📁 Estructura del Repositorio

```text
Taller_EstructuraDeDatos_2corte/
│
├── Taller_2/                   # Entrega del Taller 2
│   └── python/                 # Código Python original (Taller2_ERV_LGR.py)
│
├── Parcial_2/                  # Entrega del Parcial 2
│   ├── python/                 # Código Python del Parcial (Parcial2_ERV_LGR.py, indicadores.py)
│   └── docs/                   # Requisitos y especificaciones del Parcial 2
│
├── cpp/                        # Solución interactiva de consola en C++17 (ERV-LGR.cpp)
│   ├── ERV-LGR.cpp             # Código fuente C++ (punto de entrada único)
│   ├── estructuras.hpp         # Nodos, Producto y ListaEnlazada genérica
│   ├── grupos.hpp              # Multilista Grupo, Pila y Cola
│   ├── investigador.hpp        # Entidad Investigador
│   ├── datos.csv               # Archivo plano de persistencia
│   └── MANUAL_DE_USUARIO.md    # Manual con diagramas Mermaid (C++)
│
├── rust/                       # Solución de consola en Rust
│   ├── pea_i/                  # Proyecto Cargo completo
│   ├── ejecutar.ps1            # Script de ejecución rápida para PowerShell
│   ├── ejecutar.bat            # Script de ejecución rápida para CMD
│   └── MANUAL_DE_USUARIO.md    # Manual de usuario (Rust)
│
├── datos/                      # Datasets de verificación cruzada (JSON y CSV para C++ y Python)
│   ├── dataset_verificacion.json
│   └── dataset_verificacion.csv
│
├── docs/                       # Documentación académica formal
│   └── Taller2_PEAi_EV_LG_Completo.docx  # Informe técnico final con anexos
│
├── CAMBIOS_PARCIAL.md          # Bitácora detallada de cambios para el Parcial 2
├── integrantes.md              # Identificación formal del grupo y entrega
└── README.md                   # Esta guía general
```

---

## 🚀 Guía de Inicio Rápido por Lenguaje

### 1. 🐍 Versión Python (Interfaz Gráfica de Escritorio)

#### Requisitos
- Python 3.10 o superior ([python.org](https://www.python.org/downloads/)).

#### Instalación de dependencias
```bash
pip install customtkinter matplotlib pandas requests beautifulsoup4 pillow
```

#### Ejecución
```bash
# Ejecutar Parcial 2
python Parcial_2/python/Parcial2_ERV_LGR.py

# O ejecutar Taller 2
python Taller_2/python/Taller2_ERV_LGR.py
```

---

### 2. ⚡ Versión C++ (Consola Interactiva)

#### Ejecución y compilación
```powershell
cd cpp
g++ -std=c++17 -Wall -Wextra -I . ERV-LGR.cpp -o programa.exe
.\programa.exe
```

---

### 3. 🦀 Versión Rust (Consola Interactiva)

#### Con Cargo
```powershell
cd rust/pea_i
cargo run
```

---

## 💾 Persistencia de Datos

- **Persistencia JSON (`Parcial_2/python/datos/datos.json` / `datos/`):** Almacena el árbol completo en formato estructurado JSON. Es compatible con operaciones de guardado automático y recuperación ante reinicios del sistema.
- **Persistencia CSV (`cpp/datos.csv` / `datos/`):** Almacena los registros con formato de texto plano tipificado (`GRUPO`, `INVESTIGADOR`, `PRODUCTO`) permitiendo portabilidad con suites como Excel.

---

## 👥 Autores

Trabajo realizado para la asignatura **Estructura de Datos (Grupo 05)** — **Universidad Popular del Cesar (UPC)**:

| Integrante | Documento (CC) | Correo Institucional | Rol Principal |
| :--- | :---: | :--- | :--- |
| **Esteban Raúl Vergara Jaime** | 1065595117 | `ervergara@unicesar.edu.co` | Arquitectura GUI Python, Multilista, Web Scraping, Persistencia JSON y Documentación |
| **Luis Eduardo Gómez Rosales** | 1118821800 | `luiseduardogomez@unicesar.edu.co` | Desarrollo C++, Estructuras de Datos (Pila, Cola, Listas), Persistencia CSV y Documentación |

- **Link del Video Explicativo:** https://youtu.be/AXiJqifF1NA  
- **Docente:** Ing. Adith Pérez  
- **Entrega Académica:** Octubre de 2026 — Valledupar, Cesar, Colombia
