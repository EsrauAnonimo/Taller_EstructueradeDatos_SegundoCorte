# Guion Técnico de Grabación del Video de Sustentación (~10 Minutos)

> **Universidad Popular del Cesar (UPC)**  
> **Facultad de Ingenierías y Tecnológicas — Departamento de Ingeniería de Sistemas**  
> **Asignatura:** Estructura de Datos (Grupo 05)  
> **Taller 2 — Segundo Corte:** Programa Estadístico de Análisis de Investigación (PEA-i)  
> **Docente:** Ing. Adith Pérez (`adithperez@unicesar.edu.co`)

---

## ⚠️ Recordatorios Críticos de la Nota 3 del Enunciado

Antes de iniciar la grabación, verificar rigurosamente los siguientes tres requerimientos obligatorios:
1. **Estudiantes visibles en video TODO el tiempo:** Las cámaras web de los estudiantes deben permanecer activas y visibles en pantalla durante la totalidad de los 10 minutos (mediante recuadro tipo *Picture-in-Picture* en OBS Studio, Zoom, Google Meet o Teams). No está permitido ocultar la cámara ni usar solo voz en off.
2. **Identidad Institucional de la UPC:** Debe exhibirse el logo institucional de la Universidad Popular del Cesar en la esquina superior izquierda de la app, portada del video o diapositiva de apertura, indicando facultad, programa y grupo.
3. **Plataforma de Publicación:** El video resultante debe subirse a **YouTube** (configurado como *No listado / Oculto* o *Público*) o en una carpeta compartida de Google Drive/OneDrive con permisos de lectura abiertos para el docente `adithperez@unicesar.edu.co`.

---

## 👥 Reparto y Asignación de Roles

- **Integrante 1 (Esteban Raúl Vergara Jaime — CC: 1065595117):**
  Apertura institucional, arquitectura de estructuras de datos en memoria (Multilista, Pila, Cola), gestión de Grupos e Investigadores, y cierre formal.
- **Integrante 2 (Luis Eduardo Gomes Rosales — CC: 1118821800):**
  Gestión y taxonomía MinCiencias de Productos, proceso de Ingesta Web (Web Scraping GrupLAC), Cola FIFO en segundo plano, Dashboard Estadístico interactivo con los 4 gráficos y Persistencia JSON.

---

## ⏱️ Estructura Cronológica del Guion (~10 Minutos)

| Tramo Temporal | Duración | Locutor Principal | Pantalla / Escena a Mostrar | Puntos del Enunciado Explicados |
| :--- | :--- | :--- | :--- | :--- |
| **00:00 - 01:00** | 1:00 min | Integrante 1 (Esteban) | Portada institucional UPC con logo + Ventana principal PEA-i recién abierta con listas vacías. | Presentación institucional, Nota 3 (cámaras visibles), Nota 10 (arranque vacío o carga). |
| **01:00 - 02:40** | 1:40 min | Integrante 1 (Esteban) | Diagrama de Multilista en pantalla + Pestaña "Grupos" y "Investigadores" de la app. | Puntos 1, 2, 3, 4 y 8 (Multilista Grupo ➔ Investigador ➔ Producto, integrantes, plan). |
| **02:40 - 04:00** | 1:20 min | Integrante 1 (Esteban) | Demostración en vivo en Pestaña "Grupos" borrando un grupo y pulsando el botón "Deshacer". | Punto 9 (CRUD, borrado lógico y Pila Stack LIFO para Undo / reversibilidad). |
| **04:00 - 05:30** | 1:30 min | Integrante 2 (Luis) | Pestaña "Productos", apertura del formulario de edición y filtro rápido (2/5 años/personalizado). | Puntos 2, 5, 9, 10 y 11 (Taxonomía MinCiencias 2024: GNC, DTI, ASC, FRH, validación y filtros de año). |
| **05:30 - 07:00** | 1:30 min | Integrante 2 (Luis) | Clic en ⚙ ➔ Descarga directa GrupLAC y apertura del diálogo modal "Cola de importación FIFO". | Punto 7 y Punto 8 (Web Scraping GrupLAC con BS4/requests, Cola Queue FIFO en segundo plano). |
| **07:00 - 08:40** | 1:40 min | Integrante 2 (Luis) | Pestaña "Estadísticas" (Dashboard): KPIs, resumen Pandas, alternancia de vistas y 4 gráficos. | Punto 12 (Dashboard estadístico, resumen descriptivo, vistas Global/Grupo/Investigador, Matplotlib). |
| **08:40 - 09:30** | 0:50 min | Integrante 1 (Esteban) | Visualización del archivo `datos.json` en editor y atajo Ctrl+S en la app. Explicación de interoperabilidad. | Punto 14 (Persistencia JSON, interoperabilidad con C++ y Rust, notas 9 y 10). |
| **09:30 - 10:00** | 0:30 min | Ambos integrantes | Conclusiones rápidas, agradecimiento institucional y despedida. | Cierre formal, enlaces al repositorio de GitHub y correo del docente. |

---

## 🎬 Guion Detallado Tramo a Tramo

### Segmento 1: Introducción Institucional y Arranque (00:00 - 01:00)
- **Cámara:** Ambos integrantes visibles en recuadros superiores.
- **Pantalla:** Portada con imagotipo de la Universidad Popular del Cesar y ventana de la aplicación PEA-i.
- **Habla Integrante 1 (Esteban):**
  > *"Cordial saludo, profesor Adith Pérez y comunidad académica de la Universidad Popular del Cesar. Mi nombre es Esteban Raúl Vergara Jaime y me acompaña mi compañero Luis Eduardo Gomes Rosales, estudiantes de Ingeniería de Sistemas del curso Estructura de Datos (Grupo 05).*  
  > *A continuación sustentamos el Taller 2 del segundo corte: el desarrollo del sistema PEA-i (Programa Estadístico de Análisis de Investigación). Como se observa en pantalla, damos estricto cumplimiento a la Nota 3 del enunciado manteniendo nuestras cámaras encendidas y visibles durante toda la presentación junto a la identidad institucional de la UPC.*  
  > *En atención a la Nota 10, la aplicación arranca con estructuras en memoria limpias, permitiendo al usuario decidir si operar en blanco o cargar los datos existentes con Ctrl+O."*

---

### Segmento 2: Arquitectura Multilista, Grupos e Investigadores (01:00 - 02:40)
- **Cámara:** Esteban en primer plano / Luis en recuadro.
- **Pantalla:** Diagrama conceptual de la Multilista en el documento técnico y navegación a la pestaña "Grupos" e "Investigadores".
- **Habla Integrante 1 (Esteban):**
  > *"En el núcleo computacional (puntos 1 al 4 y punto 8), no utilizamos bases de datos relacionales ni colecciones de alto nivel. Implementamos a mano en la carpeta `modelos/` una **Multilista Jerárquica** basada en nodos con doble enlace y punteros ortogonales.*  
  > *El nivel 1 almacena los Grupos de Investigación enlazados horizontalmente. Cada nodo de grupo contiene su puntero `sublist` vertical hacia la lista de Investigadores adscritos (Nivel 2), y cada investigador tiene su respectiva `sublist` hacia sus Productos científicos (Nivel 3).*  
  > *Mostramos aquí en la pestaña 'Grupos' el registro del grupo oficial GISICO de la UPC, su código GrupLAC, categoría C, líder y plan estratégico completo de trabajo. Al pasar a la pestaña 'Investigadores', vemos a sus integrantes vinculados y el filtro que permite aislar a los miembros de cada grupo."*

---

### Segmento 3: Eliminación Lógica y Pila de Deshacer (Undo) (02:40 - 04:00)
- **Cámara:** Esteban en primer plano / Luis en recuadro.
- **Pantalla:** Pestaña "Grupos" seleccionando un registro, haciendo clic en "Eliminar" y luego pulsando "Deshacer".
- **Habla Integrante 1 (Esteban):**
  > *"El punto 9 exige operaciones CRUD completas y borrado lógico. Para esto implementamos dos mecanismos:*  
  > *Primero, cada nodo cuenta con un atributo `active`. Al desactivar un registro, este se oculta de las vistas sin romper la cadena de punteros en memoria.*  
  > *Segundo, para la eliminación física integramos una **Pila propia (Stack - LIFO)** en `modelos/pila.py`. Cuando elimino este grupo de prueba, el sistema realiza un `push` de la entidad y todas sus sublistas a la pila `app.undo_stack`.*  
  > *Observen cómo en la barra de estado se enciende el contador 'Deshacer: 1'. Al presionar el botón 'Deshacer' (o Ctrl+Z), se ejecuta un `pop` que extrae el último registro apilado y lo reinserta exactamente en su posición de la Multilista con todas sus relaciones intactas."*

---

### Segmento 4: Productos, Taxonomía MinCiencias y Filtros de Año (04:00 - 05:30)
- **Cámara:** Luis en primer plano / Esteban en recuadro.
- **Pantalla:** Pestaña "Productos", apertura del formulario modal de producto y uso de los botones de filtro temporal.
- **Habla Integrante 2 (Luis):**
  > *"Pasando a la gestión de producción científica (puntos 5, 9, 10 y 11), nos encontramos en la pestaña 'Productos'. Aquí implementamos de manera rigurosa la **Taxonomía oficial de MinCiencias 2024** (`entidades/taxonomia_minciencias.py`).*  
  > *Cada producto se clasifica obligatoriamente en una de las cuatro grandes categorías: Generación de Nuevo Conocimiento (GNC), Desarrollo Tecnológico (DTI), Apropiación Social (ASC) o Formación de Recurso Humano (FRH), asignando además su estado de validación formal: 'Validado', 'No validado' o 'En revisión'.*  
  > *Para dar respuesta al Punto 10, contamos con la barra de filtrado por ventana de observación: podemos hacer clic en 'Últimos 2 años', 'Últimos 5 años' o definir un rango 'Personalizado' (por ejemplo 2020 a 2024). Observen cómo la tabla y la Multilista filtran los productos en tiempo real a través del método `get_productos_by_anio_range`."*

---

### Segmento 5: Web Scraping de GrupLAC y Cola FIFO en Segundo Plano (05:30 - 07:00)
- **Cámara:** Luis en primer plano / Esteban en recuadro.
- **Pantalla:** Despliegue del menú de la tuerca ⚙, clic en "Descargar del SCIENTI" y apertura del diálogo "Cola de importación".
- **Habla Integrante 2 (Luis):**
  > *"El Punto 7 solicita la capacidad de descargar datos mediante Web Scraping desde el portal SCIENTI MinCiencias. En `scraping/scienti.py` construimos un scraper robusto con BeautifulSoup y Requests con sesión de reintentos automáticos.*  
  > *Con un solo clic desde el menú de ajustes podemos descargar los datos del grupo GISICO UPC (código 00000000002099).*  
  > *Pero además, respondiendo a la estructura de **Cola (Queue - FIFO)** requerida, desarrollamos el modal de 'Cola de Importación'. Aquí el usuario puede encolar múltiples URLs de GrupLAC. La estructura `Queue` almacena las peticiones en orden de llegada y un hilo secundario (`threading.Thread`) las procesa secuencialmente mediante `dequeue`, reportando el porcentaje de avance sin congelar en ningún momento la interfaz gráfica."*

---

### Segmento 6: Dashboard Estadístico Multivista y Gráficos (07:00 - 08:40)
- **Cámara:** Luis en primer plano / Esteban en recuadro.
- **Pantalla:** Pestaña "Estadísticas". Demostración de KPIs, tarjeta de resumen descriptivo, selección de vista "Por grupo" y los 4 gráficos.
- **Habla Integrante 2 (Luis):**
  > *"Llegamos al Punto 12 del enunciado: la visualización estadística avanzada mediante un Dashboard interactivo.*  
  > *En la parte superior disponemos de tres tarjetas KPI con el total y los registros activos de Grupos, Investigadores y Productos.*  
  > *Inmediatamente después, el panel descriptivo utiliza la librería Pandas para computar matemáticamente la producción: total, promedio, mediana, valor mínimo y valor máximo.*  
  > *A continuación se despliega la cuadrícula con los **4 gráficos analíticos de Matplotlib**:*  
  > *1. Gráfico de barras de evolución temporal (Productos por año).*  
  > *2. Distribución canónica por Gran Categoría MinCiencias (GNC, DTI, ASC, FRH).*  
  > *3. Gráfico de barras horizontales con el Top 10 de tipologías más frecuentes.*  
  > *4. Histograma de productividad por investigador.*  
  > *El usuario puede alternar la perspectiva en tres vistas: 'Global' institucional, 'Por grupo' o 'Por investigador', recalculando al instante todas las métricas."*

---

### Segmento 7: Persistencia JSON e Interoperabilidad (08:40 - 09:30)
- **Cámara:** Esteban en primer plano / Luis en recuadro.
- **Pantalla:** Visualización del archivo `datos.json` abierto en Visual Studio Code o explorador y atajo Ctrl+S en la aplicación.
- **Habla Integrante 1 (Esteban):**
  > *"En cuanto a la persistencia (Notas 9 y 10), el sistema serializa la Multilista en `python/datos/datos.json` mediante `persistencia/persistencia_json.py`.*  
  > *Este formato JSON desacoplado no solo almacena fielmente las claves jerárquicas, sino que garantiza la **interoperabilidad** (punto 14.d) con la solución homóloga en C++ desarrollada por el compañero Luis y los prototipos en Rust, permitiendo compartir el mismo archivo de datos entre lenguajes.*  
  > *Asimismo, el sistema incluye atajos globales como Ctrl+S para guardar, Ctrl+O para cargar y un botón para exportar todo el dashboard gráfico en formato PNG."*

---

### Segmento 8: Conclusiones y Despedida (09:30 - 10:00)
- **Cámara:** Ambos integrantes en plano compartido / pantalla completa con créditos finales.
- **Habla Integrante 1 (Esteban):**
  > *"En conclusión, hemos implementado con éxito todas las estructuras requeridas —lista doble, multilista ortogonal, pila y cola— integradas armónicamente en una interfaz moderna con CustomTkinter para la Universidad Popular del Cesar."*
- **Habla Integrante 2 (Luis):**
  > *"Todos los entregables, códigos fuentes con nuestras iniciales `EV_LG.py`, archivo de persistencia, manual de usuario y documento de especificación formal quedan consignados en la rama 'python' del repositorio de GitHub y remitidos al correo institucional del docente. ¡Muchas gracias por su atención!"*

---

## 📋 Checklist Pre-Grabación para los Estudiantes
- [ ] Cámara web encendida, bien iluminada y visible durante toda la grabación.
- [ ] Resolución de grabación ajustada a 1080p (1920x1080) a 30 o 60 fps.
- [ ] Aplicación PEA-i ejecutándose con resolución mínima de 1280x760.
- [ ] Archivo `datos.json` verificado en la carpeta `python/datos/`.
- [ ] Tiempo cronometrado en ensayos entre 9:30 y 10:30 minutos.
- [ ] Enlace de YouTube listo para pegar en `Checklist_entrega.md` y `Correo_entrega.md`.
