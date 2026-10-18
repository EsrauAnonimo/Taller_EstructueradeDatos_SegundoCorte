# Persistencia de Datos — PEA-i (Taller 2)

> **Universidad Popular del Cesar (UPC)**  
> **Facultad de Ingenierías y Tecnológicas — Ingeniería de Sistemas**  
> **Asignatura:** Estructura de Datos (Grupo 05)  
> **Archivo de Datos:** `Taller2_EV_LG_datos.json`

---

## 1. Descripción del Archivo de Persistencia

El archivo `Taller2_EV_LG_datos.json` (copia certificada del archivo de trabajo `python/datos/datos.json`) almacena en formato JSON estructurado el estado completo de la **Multilista jerárquica en memoria** del sistema PEA-i.

Contiene datos reales extraídos directamente desde el portal oficial de **MinCiencias / GrupLAC** para el grupo de investigación de la UPC:
- **Grupo:** GRUPO DE INVESTIGACION EN SISTEMAS Y COMPUTACIÓN -GISICO- (Código GrupLAC: `00000000002099`).
- **Investigador Líder:** John Jairo Patiño Vanegas (Cédula: `0000799157`).
- **Productos Científicos:** Producción histórica indexada, clasificada bajo la taxonomía oficial MinCiencias 2024 en Generación de Nuevo Conocimiento (GNC), Desarrollo Tecnológico e Innovación (DTI) y Apropiación Social del Conocimiento (ASC).

---

## 2. Estructura Jerárquica del JSON

El JSON está diseñado para reflejar la relación ortogonal de la Multilista en memoria (`Grupo ➔ Investigadores ➔ Productos`):

```json
{
  "grupos": [
    {
      "grupo": {
        "id": 1,
        "codigo_gruplac": "00000000002099",
        "nombre": "GRUPO DE INVESTIGACION EN SISTEMAS Y COMPUTACIÓN -GISICO-",
        "categoria": "C",
        "lider": "john jairo PATIÑO VANEGAS",
        "activo": true,
        "fecha_creacion": "2001 - 2",
        "plan": "PLAN DE TRABAJO:\n1) Consolidación de un grupo...\nOBJETIVOS:..."
      },
      "investigadores": [
        {
          "investigador": {
            "id": "0000799157",
            "cedula": "0000799157",
            "nombres": "john jairo",
            "apellidos": "PATIÑO VANEGAS",
            "email": "",
            "activo": true,
            "grupo_id": 1
          },
          "productos": [
            {
              "id": "PRD-108",
              "titulo": "CONSTRUCCIÓN Y EVALUACIÓN DE LOS RESULTADOS DE APRENDIZAJE...",
              "tipo": "Capítulos en libro resultado de investigación",
              "categoria": "Nuevo conocimiento",
              "validado": true,
              "anio": 2024,
              "investigador_id": "0000799157",
              "grupo_id": 1,
              "raw": null,
              "gran_categoria": "GNC",
              "codigo_minciencias": "2.2.1.4",
              "categoria_producto": "Nuevo conocimiento",
              "validacion": "No validado",
              "investigador_cedula": "0000799157"
            }
          ]
        }
      ]
    }
  ]
}
```

### Campos Clave y Significado
- `grupo`: Objeto que representa el nodo de Grupo (identificador, código, nombre, categoría MinCiencias, líder, estado lógico y plan estratégico).
- `investigadores`: Arreglo de sublista de integrantes vinculados al grupo. Cada elemento encapsula el objeto `investigador` y su propia sublista de `productos`.
- `productos`: Arreglo de sublista de productos científicos adscritos al investigador y al grupo. Incluye normalización MinCiencias (`gran_categoria`: GNC/DTI/ASC/FRH, `codigo_minciencias`: ej. `2.2.1.4`, y estado textual de `validacion`: Validado / No validado / En revisión).

---

## 3. Cómo Cargar los Datos en la Aplicación

Existen tres mecanismos directos para cargar este archivo de persistencia en la aplicación PEA-i:

### Método A: Carga Interactiva desde la Interfaz Gráfica (Recomendado)
1. Inicie la aplicación (mediante `python python/gui/app.py` o ejecutando el lanzador `EV_LG.py`).
2. Presione la combinación de teclas **`Ctrl + O`** (o haga clic en el ícono de engranaje **⚙** ubicado en la esquina inferior izquierda del sidebar).
3. Seleccione la opción **"Cargar datos desde JSON"**.
4. En el explorador de archivos, seleccione el archivo `Taller2_EV_LG_datos.json` (o `python/datos/datos.json`).
5. La aplicación deserializará el archivo, reconstruirá la Multilista en memoria y actualizará inmediatamente las 4 pestañas: Grupos, Investigadores, Productos y el Dashboard Estadístico con sus 4 gráficos.

### Método B: Arranque Predeterminado
El gestor `PersistenciaJSON` (`python/persistencia/persistencia_json.py`) busca de forma predeterminada el archivo en la ruta relativa `python/datos/datos.json`. Como `Taller2_EV_LG_datos.json` es idéntico a dicho archivo, al solicitar la recarga de persistencia el sistema lee directamente el almacenamiento local.

### Método C: Carga Programática (Python)
Para inspeccionar o manipular los datos desde consola o scripts externos:

```python
import sys
from pathlib import Path

# Agregar raíz del proyecto al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from persistencia.persistencia_json import PersistenciaJSON

# Instanciar persistencia apuntando al archivo
persistencia = PersistenciaJSON("entrega/python/Taller2_EV_LG_datos.json")
datos = persistencia.load()

# Reconstruir la Multilista en memoria
multilista = PersistenciaJSON.to_multilist(datos)

print(f"Grupos cargados: {len(multilista)}")
for grupo in multilista.iterate_groups():
    print(f"- {grupo.nombre} (Código: {grupo.codigo_gruplac})")
```

---

## 4. Interoperabilidad con C++ y Rust

El formato JSON adoptado posee total interoperabilidad con las otras soluciones del taller:
- **C++:** Puede deserializarse utilizando la biblioteca de cabecera única `nlohmann/json.hpp` o convertirse a `datos.csv` respetando la estructura tabular plana (`Grupo,Investigador,Producto,Año,Categoría`).
- **Rust:** Puede deserializarse mediante `serde` y `serde_json` mapeando a las estructuras equivalentes `struct Grupo`, `struct Investigador` y `struct Producto`.
