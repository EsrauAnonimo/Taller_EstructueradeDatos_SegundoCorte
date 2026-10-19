# Lista de Chequeo y Control de Entregables (Checklist)

> **Universidad Popular del Cesar (UPC)**  
> **Facultad de Ingenierías y Tecnológicas — Ingeniería de Sistemas**  
> **Asignatura:** Estructura de Datos (Grupo 05)  
> **Taller 2 — Segundo Corte**  
> **Docente:** Ing. Adith Pérez (`adithperez@unicesar.edu.co`)

---

## 1. Verificación de las Notas del Enunciado (Notas 1 a 10)

| Ítem | Requerimiento de la Nota | Entregable Asociado / Ubicación | Estado | Observaciones |
| :---: | :--- | :--- | :---: | :--- |
| **Nota 1** | 2 archivos en formato texto donde se consignen las respuestas a los ejercicios (`.cpp` y `.py`). | • Python: `entrega/python/EV_LG.py`<br>• C++: `cpp/main.cpp` | **Listo (Python)** / *Pendiente (C++)* | La parte Python cuenta con su lanzador verificado `EV_LG.py`. El archivo consolidado con iniciales de C++ (`Taller2_EV_LG.cpp`) debe gestionarse en la rama/carpeta de C++. |
| **Nota 2** | Archivo Word (`.docx`) de especificación técnica formal con diseño de estructuras, estrategia, diagramas, casos de uso, SPEC y HU. | `entrega/python/Taller2_EV_LG_Especificacion.docx` | **Listo** | Generado con `python-docx` (1.38 MB), portada institucional UPC, tablas de variables I/O y 6 diagramas conceptuales incrustados en alta resolución. |
| **Nota 3** | Video explicativo de ~10 minutos en YouTube o carpeta compartida, respetando identidad institucional y con **estudiantes visibles todo el tiempo**. | • Guion: `entrega/python/Guion_video.md`<br>• Grabación: `[COMPLETAR URL]` | **Guion Listo** / *Video Pendiente* | El guion técnico con asignación de minutos y roles está 100% completo. Queda pendiente la grabación física por parte de Esteban y Luis y pegar el enlace de YouTube. |
| **Nota 4** | Archivo de texto plano con la información de identificación de los estudiantes. | `entrega/python/integrantes.txt` | **Listo** | Contiene nombres completos, cédulas, correos institucionales de ambos estudiantes y marcadores `[COMPLETAR]` para código estudiantil. |
| **Nota 5** | Entrega de archivos al correo electrónico institucional `adithperez@unicesar.edu.co`. | `entrega/python/Correo_entrega.md` | **Listo (Plantilla)** / *Envío Pendiente* | Plantilla de correo redactada formalmente con lista exhaustiva de adjuntos y formato de asunto exacto. |
| **Nota 6** | Entrega antes del lunes 19 de octubre a las 11:59 am. | Cronograma de entrega | **En Tiempo** | Los entregables documentales y de código Python quedan finalizados y congelados antes del límite. |
| **Nota 7** | Asunto exacto del correo: `Estructura de datos Taller 2 Grupo XX 2026`. | `entrega/python/Correo_entrega.md` | **Listo** | Formato exacto establecido en la plantilla, dejando `XX` o `05 / [COMPLETAR]`. |
| **Nota 8** | Archivos fuente nombrados con las iniciales de los estudiantes (`EV_LG.py`). | `entrega/python/EV_LG.py` | **Listo** | Lanzador mínimo validado en terminal (`EV_LG verification SUCCESS`). |
| **Nota 9** | Archivo donde se consigne la persistencia de los datos utilizados. | • `entrega/python/Taller2_EV_LG_datos.json`<br>• `entrega/python/README_persistencia.md` | **Listo** | Copia íntegra de los datos de MinCiencias (Grupo GISICO UPC) acompañada de guía técnica de deserialización. |
| **Nota 10** | El usuario puede decidir si cargar los datos del archivo o ejecutar sin datos. | `python/gui/app.py:L136-137` | **Listo** | La aplicación inicia por defecto con listas vacías y permite la carga inmediata mediante `Ctrl + O` o menú contextual. |

---

## 2. Verificación de Ejercicios del Enunciado (Puntos 1 a 12)

- [x] **Punto 1:** Gestión de grupos e investigadores (`crud/crud_grupos.py`, `crud/crud_investigadores.py`).
- [x] **Punto 2:** Para cada grupo y para cada investigador, gestión de sus productos (`modelos/multilista.py:L291, L317`).
- [x] **Punto 3:** Para cada grupo, gestión de integrantes, plan de trabajo y productos (`entidades/grupo.py:plan`, `multilista.py`).
- [x] **Punto 4:** Para cada investigador, gestión de información personal y producción científica (`entidades/investigador.py`).
- [x] **Punto 5:** Taxonomía y detalles de clasificación MinCiencias 2024 (`entidades/taxonomia_minciencias.py`).
- [x] **Punto 6:** Identificación completa de variables de entrada, salida y calculadas (`docs/variables_io.md` y Especificación Word).
- [x] **Punto 7:** Web Scraping desde URL GrupLAC y contingencia CSV (`scraping/scienti.py`). *(Nota: PDF básico y CvLAC independiente identificados en limitaciones).*
- [x] **Punto 8:** Estructura de datos de LISTAS propia en memoria (`modelos/lista.py`, `modelos/multilista.py`).
- [x] **Punto 9:** CRUD completo con categoría, validación y eliminación lógica/física (`entidades/producto.py`, `modelos/nodo.py:active`, `multilista.py`).
- [x] **Punto 10:** Filtro de productos por año y ventana de observación (Últimos 2 años, Últimos 5 años, Personalizado) (`gui/tabs/estadisticas_tab.py`).
- [x] **Punto 11:** Capacidad de editar y modificar cualquier dato existente mediante formularios modales validados.
- [x] **Punto 12:** Dashboard analítico descriptivo en Python con Pandas, KPIs y 4 gráficos interactivos de Matplotlib (Evolución anual, Grandes categorías GNC/DTI/ASC/FRH, Top 10 tipos e Histograma de productividad).

---

## 3. Complementos y Valor Agregado (Puntos 13 y 14)

- [x] **Git y GitHub:** Control de versiones ordenado, ramas especializadas (`python`), commits semánticos por documento.
- [x] **GUI Creativa:** Interfaz CustomTkinter con paleta institucional UPC (Verde `#006633` y Azul marino `#0F1B3D`), logo de Unicesar, tarjetas con bordes, barra lateral unificada y atajos de teclado globales.
- [x] **Estructuras Auxiliares:**
  - [x] **Pila (Stack - LIFO):** Sistema de Deshacer (Undo) para eliminaciones accidentales (`modelos/pila.py`, `app.undo_stack`).
  - [x] **Cola (Queue - FIFO):** Cola de importación de URLs en segundo plano mediante hilos desacoplados (`modelos/cola.py`, `ColaImportacionModal`).
- [x] **Interoperabilidad:** Formato estándar JSON (`Taller2_EV_LG_datos.json`) consumible entre Python, C++ y Rust.
- [ ] **Versión C++:** Desarrollada en la carpeta `cpp/` por el integrante Luis Gomes (*verificar entrega en rama/carpeta C++*).
- [ ] **Versión Rust:** Prototipo opcional en rama `rust` (*fuera del alcance del entregable Python*).

---

## 📌 Acciones Finales Pendientes para los Estudiantes

1. **Grabar el Video de Sustentación:**
   - Reunirse Esteban y Luis (vía OBS Studio, Zoom, Google Meet o Teams).
   - Encender ambas cámaras web (requisito indispensable de la Nota 3).
   - Seguir el guion de 10 minutos consignado en `Guion_video.md`.
   - Subir el video a YouTube (en modo Oculto) o a Google Drive con acceso público.
2. **Actualizar Marcadores `[COMPLETAR]`:**
   - Pegar la URL del video en `Correo_entrega.md` y en este checklist.
   - Completar los códigos estudiantiles en `integrantes.txt` si se desean adjuntar junto a las cédulas.
   - Ajustar el número de grupo `XX` en el asunto del correo si difiere de `Grupo 05`.
3. **Enviar Correo Electrónico:**
   - Adjuntar los archivos de `entrega/python/` detallados en `Correo_entrega.md`.
   - Enviar a `adithperez@unicesar.edu.co` antes de las 11:59 am del lunes 19 de octubre.
