# PEA-i — Plataforma para la Evaluación y Analítica de la Investigación

> **Universidad Popular del Cesar (UPC)**  
> **Facultad de Ingenierías y Tecnológicas — Ingeniería de Sistemas**  
> **Asignatura:** Estructura de Datos (Grupo 05)  
> **Docente Titular:** Ing. Adith Pérez  
> **Evaluación:** Parcial 2 — Segundo Corte  
> **Fecha:** Octubre de 2026 — Valledupar, Cesar, Colombia  
> **Video Explicativo:** [PEGAR ENLACE AQUÍ]

---

### Autores e Integrantes del Equipo

| Integrante | Documento (CC) | Código Estudiantil | Correo Institucional | Rol Principal |
| :--- | :---: | :---: | :--- | :--- |
| **Esteban Raúl Vergara Jaime** | 1065595117 | 1065595117 | `ervergara@unicesar.edu.co` | Arquitectura GUI Python, Multilista, Web Scraping, Motor de Indicadores MinCiencias, Documentación |
| **Luis Eduardo Gómez Rosales** | 1118821800 | 1118821800 | `luiseduardogomez@unicesar.edu.co` | Desarrollo C++, Estructuras de Datos (Pila, Cola, Listas), Persistencia CSV, Interoperabilidad, Documentación |

---

## 📌 Resumen del Proyecto

**PEA-i (Plataforma para la Evaluación y Analítica de la Investigación)** es un sistema integral para la gestión, estructuración, análisis métrico y auditoría de la producción científica institucional (Grupos de Investigación, Investigadores y Productos Académicos) bajo el modelo oficial de **MinCiencias Colombia** (GrupLAC / Scienti).

El núcleo del proyecto implementa **desde cero y a mano** estructuras de datos dinámicas lineales y no lineales (sin depender de bases de datos relacionales externas ni de colecciones de alto nivel para el modelo), aplicadas en un **ecosistema dual**:

1. 🐍 **Python:** Aplicación de escritorio moderna con interfaz gráfica en CustomTkinter, analítica con Matplotlib/Pandas, Web Scraping automatizado en vivo, motor de cálculo del Indicador MinCiencias y persistencia en JSON.
2. ⚡ **C++ (C++17):** Sistema en terminal interactiva de alto rendimiento con menús formateados, tablas de estadísticas con `<iomanip>`, auditoría de historial en Pila LIFO, cola de validación FIFO, cálculo paramétrico del indicador por grupos e investigadores, y persistencia en CSV plano tipificado.

El repositorio se divide formalmente en dos entregas:
- **`Taller_2/`:** Solución base correspondiente al Taller 2 (gestión jerárquica, CRUDs, Pila/Cola, sin la fórmula de indicadores de MinCiencias).
- **`Parcial_2/`:** Solución extendida correspondiente al Parcial 2 (motor del Indicador MinCiencias con pesos relativos, filtros por ventanas de años, pestaña interactiva de indicadores, exclusión formal de productos inactivos o no validados, y verificación cruzada).

> ℹ️ Para consultar la bitácora detallada de cambios aplicados entre el Taller y el Parcial, revisa el archivo [CAMBIOS_PARCIAL.md](CAMBIOS_PARCIAL.md).

---

## 🏗️ Estructuras de Datos Implementadas (Sin Librerías Externas)

Todas las estructuras de datos operan sobre nodos enlazados construidos manualmente a nivel de punteros y referencias:

| Estructura | Propósito en el Sistema | Implementación Python | Implementación C++ |
| :--- | :--- | :--- | :--- |
| **Multilista Jerárquica** | Modelo central en memoria: `Grupo ➔ Investigadores ➔ Productos` con enlaces de pertenencia jerárquica sin redundancia. | [multilista.py](file:///c:/Users/Esteb/OneDrive/Documentos/Taller_EstructuraDeDatos_2corte/Parcial_2/python/modelos/multilista.py) | [grupos.hpp](file:///c:/Users/Esteb/OneDrive/Documentos/Taller_EstructuraDeDatos_2corte/Parcial_2/cpp/grupos.hpp) |
| **Lista Enlazada Genérica** | Almacenamiento dinámico de entidades con punteros `cabeza` y `cola`. | [lista.py](file:///c:/Users/Esteb/OneDrive/Documentos/Taller_EstructuraDeDatos_2corte/Parcial_2/python/modelos/lista.py) | [estructuras.hpp](file:///c:/Users/Esteb/OneDrive/Documentos/Taller_EstructuraDeDatos_2corte/Parcial_2/cpp/estructuras.hpp) |
| **Pila (Stack — LIFO)** | Historial de auditoría y mecanismo de **Deshacer (Undo)** ante eliminaciones lógicas (`Ctrl+Z`). | [pila.py](file:///c:/Users/Esteb/OneDrive/Documentos/Taller_EstructuraDeDatos_2corte/Parcial_2/python/modelos/pila.py) | [grupos.hpp](file:///c:/Users/Esteb/OneDrive/Documentos/Taller_EstructuraDeDatos_2corte/Parcial_2/cpp/grupos.hpp) |
| **Cola (Queue — FIFO)** | **Cola de Importación** masiva y buffer de atención secuencial para validación de productos. | [cola.py](file:///c:/Users/Esteb/OneDrive/Documentos/Taller_EstructuraDeDatos_2corte/Parcial_2/python/modelos/cola.py) | [grupos.hpp](file:///c:/Users/Esteb/OneDrive/Documentos/Taller_EstructuraDeDatos_2corte/Parcial_2/cpp/grupos.hpp) |

---

## 📐 Fórmula del Indicador de Producción Científica (MinCiencias)

El sistema modela con exactitud la fórmula paramétrica ponderada del modelo de medición MinCiencias:

$$\text{Indicador} = 3.7 \cdot Nc\_Top + 2.3 \cdot Nc\_A + 0.4 \cdot Nc\_B + 1.5 \cdot AP + 0.5 \cdot DPC + 1.0 \cdot Fr\_A + 0.2 \cdot Fr\_B + 0.1 \cdot Cohe + 0.3 \cdot Coop$$

### Taxonomía de Ponderación:
- **$Nc\_Top$ (3.7):** Artículos en revistas A1 / Top.
- **$Nc\_A$ (2.3):** Artículos en revistas A2 / A, libros de investigación y patentes concedidas.
- **$Nc\_B$ (0.4):** Artículos en revistas categoría B y capítulos en libro resultado de investigación.
- **$AP$ (1.5):** Apropiación Social del Conocimiento, eventos científicos y artículos categoría C.
- **$DPC$ (0.5):** Conceptos técnicos, software con registro y registros de diseño industrial.
- **$Fr\_A$ (1.0):** Tesis de Doctorado y trabajos de grado de Maestría sustentados y aprobados.
- **$Fr\_B$ (0.2):** Trabajos de grado de pregrado aprobados y proyectos de semillero tutelados.
- **$Cohe$ (0.1):** Indicador de cohesión grupal (coautoría interna).
- **$Coop$ (0.3):** Indicador de cooperación internacional e interinstitucional.

### Reglas de Medición y Filtros:
1. **Condición de Validez:** Solo suman al puntaje los productos donde `validado == True` y `activo == True`.
2. **Filtro Temporal:** Soporta `Todos los años`, `Últimos 5 años`, `Últimos 10 años` o `Personalizado` (con validación de no inversión $Desde \le Hasta$).
3. **Desglose de Estados en la Tabla:** Los productos excluidos se listan con puntaje `0.00` y su estado explícito (`"No validado"`, `"Inactivo"`, `"Fuera de rango"`) estilisados visualmente en color gris.
4. **Respuesta ante Escenario Cero:** Si ningún producto cumple los criterios, el total se fija en `0.00` con un aviso descriptivo de la causa.

---

## 📁 Estructura del Repositorio

```text
Taller_EstructuraDeDatos_2corte/
│
├── Taller_2/                               # Entrega del Taller 2 (Base)
│   ├── cpp/                                # Solución en C++17 (Taller2_ERV_LGR.cpp)
│   ├── python/                             # Solución en Python (Taller2_ERV_LGR.py)
│   └── docs/                               # Documento técnico completo (.docx)
│
├── Parcial_2/                              # Entrega del Parcial 2 (Completo con Indicadores)
│   ├── cpp/                                # Solución en C++17 (Parcial2_ERV_LGR.cpp)
│   ├── python/                             # Solución GUI en Python (Parcial2_ERV_LGR.py)
│   └── docs/                               # Especificación IEEE 830 (.md) y Documento Word (.docx)
│       ├── Requisitos_Parcial2.md          # Especificación formal con diagramas Mermaid
│       └── Requisitos_Parcial2_ERV_LGR.docx# Documento Word oficial para entrega
│
├── CAMBIOS_PARCIAL.md                      # Bitácora detallada de cambios Taller 2 -> Parcial 2
├── integrantes.txt                         # Identificación institucional de los integrantes
└── README.md                               # Guía general de inicio y documentación
```

---

## 🚀 Guía de Inicio Rápido

### 1. 🐍 Aplicación en Python (GUI de Escritorio)

#### Requisitos
- Python 3.10 o superior ([python.org](https://www.python.org/downloads/)).

#### Instalación de Dependencias
```bash
pip install customtkinter matplotlib pandas requests beautifulsoup4 pillow python-docx
```

#### Ejecución
```bash
# Ejecutar Parcial 2 (con pestaña de Indicadores y modelo MinCiencias)
python Parcial_2/python/Parcial2_ERV_LGR.py

# O ejecutar Taller 2 (versión base del taller)
python Taller_2/python/Taller2_ERV_LGR.py
```

---

### 2. ⚡ Aplicación en C++ (Terminal Interactiva)

#### Compilación y Ejecución del Parcial 2:
```powershell
# Compilación con g++ (C++17)
g++ -std=c++17 -Wall -Wextra -I Parcial_2/cpp Parcial_2/cpp/Parcial2_ERV_LGR.cpp -o Parcial_2/cpp/parcial2.exe

# Ejecución
.\Parcial_2/cpp/parcial2.exe
```

#### Compilación y Ejecución del Taller 2:
```powershell
# Compilación con g++ (C++17)
g++ -std=c++17 -Wall -Wextra -I Taller_2/cpp Taller_2/cpp/Taller2_ERV_LGR.cpp -o Taller_2/cpp/taller2.exe

# Ejecución
.\Taller_2/cpp/taller2.exe
```

---

## 💾 Persistencia de Datos

- **Persistencia JSON (`Parcial_2/python/datos/datos.json`):** Almacena el árbol jerárquico completo en memoria secundaria, serializando los atributos extendidos `peso_relativo`, `puntaje`, `gran_categoria` y `codigo_minciencias`.
- **Persistencia CSV (`Parcial_2/cpp/datos.csv`):** Almacena los registros con formato de texto plano tipificado (`GRUPO`, `INVESTIGADOR`, `PRODUCTO`), permitiendo portabilidad con suites como Excel y garantizando compatibilidad entre C++ y Python.

---

## 🎥 Enlace al Video Explicativo

- **Video Explicativo en YouTube (EXPLICACION DEL TALLER ):** [https://youtu.be/AXiJqifF1NA]
- **Video Explicativo en YouTube (EXPLICACION DEL PARCIAL):** [https://youtu.be/WLI6ps9aR20]
- 
- **Docente:** Ing. Adith Pérez  
- **Asignatura:** Estructura de Datos (Grupo 05) — Universidad Popular del Cesar (UPC)
