# -*- coding: utf-8 -*-
"""
dashboard.py
Dashboard interactivo (Streamlit) para visualizar los datos generados por el
programa en C++ del taller. Disenado como el panel de control de un centro de
investigacion con un estilo SaaS moderno (modo claro).

Lee el archivo ../cpp/datos.csv, que tiene un formato separado por comas donde
cada linea empieza con una etiqueta que indica el tipo de registro:

    GRUPO,idGrupo,nombre,plan
    INVESTIGADOR,idGrupo,id,nombre,area,categoria
    PRODUCTO,idGrupo,id,titulo,anio,categoria,validado

Como cada tipo de registro tiene una cantidad distinta de columnas, el archivo
se lee sin encabezado (header=None) y luego se separa por la primera columna.

Requisitos e instalacion:
    pip install streamlit pandas plotly

Ejecucion (desde la raiz del proyecto):
    streamlit run python/dashboard.py
"""

import io
import os

import pandas as pd
import plotly.express as px
import streamlit as st

# Ruta al CSV relativa a ESTE archivo, para que funcione sin importar desde
# que directorio se ejecute el comando.
RUTA_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "cpp", "datos.csv")

# --- 1. Configuracion inicial de la pagina --------------------------------
# Debe ser la primera funcion de Streamlit que se ejecuta.
st.set_page_config(page_title="Dashboard de Investigación",
                   page_icon="🔬", layout="wide")


# --- Paleta y estilos ------------------------------------------------------
# Colores corporativos usados en los graficos y en el CSS. Se definen aqui
# para mantener una linea visual coherente en todo el tablero.
COLOR_PRIMARIO = "#4361ee"     # Azul principal (SaaS).
COLOR_ACENTO = "#7209b7"       # Morado de acento.
COLOR_EXITO = "#10b981"        # Verde para "Validado".
COLOR_ALERTA = "#ef4444"       # Rojo para "Pendiente".
PALETA_CATEGORICA = ["#4361ee", "#7209b7", "#f72585", "#4cc9f0",
                     "#f8961e", "#10b981", "#ef476f"]


def inyectar_estilos():
    """
    Inyecta el CSS personalizado que da el aspecto de dashboard SaaS moderno
    (modo claro): fondo gris claro, tarjetas blancas con bordes redondeados y
    sombras suaves, tipografia moderna y barra lateral blanca.

    Es puramente visual: no afecta la logica de datos, filtros ni descargas.
    """
    st.markdown(
        """
        <style>
        /* ---- Tipografia moderna ---- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"], .stApp, button, input, select, textarea {
            font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
        }

        /* ---- Texto oscuro y en negrilla en todo el tablero ----
           Se fuerza un color casi negro (#1e293b) y peso semi-negrita
           (600) en todos los textos para que se lean bien sobre las
           tarjetas blancas. */
        .stApp p,
        .stApp h1,
        .stApp h2,
        .stApp h3,
        .stApp h4,
        .stApp span,
        .stApp label,
        .stApp li {
            color: #1e293b;
            font-weight: 600;
        }

        /* ---- Fondo general (gris muy claro) ---- */
        .stApp {
            background-color: #f8f9fa;
        }
        [data-testid="stHeader"] {
            background: transparent;
        }

        /* ---- Encabezado tipo SaaS ---- */
        .app-header {
            background-color: #ffffff;
            border: 1px solid #eef0f3;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            padding: 1.4rem 1.6rem;
            margin-bottom: 1.5rem;
        }
        .app-header h1 {
            font-size: 1.7rem;
            font-weight: 700;
            color: #1a1f36;
            margin: 0 0 0.35rem 0;
        }
        .app-header p {
            color: #1e293b;
            font-weight: 600;
            font-size: 0.95rem;
            margin: 0;
        }

        /* ---- Barra lateral: blanca con divisor sutil ---- */
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e9ecef;
        }
        [data-testid="stSidebar"] > div:first-child {
            background-color: #ffffff;
        }
        .sidebar-brand {
            font-size: 1.15rem;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 0.1rem;
        }
        .sidebar-sub {
            color: #1e293b;
            font-weight: 600;
            font-size: 0.8rem;
            margin-bottom: 0.5rem;
        }
        .filtro-titulo {
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: #1e293b;
            margin: 0.4rem 0 0.3rem 0;
        }

        /* ---- Tarjetas de metricas (KPIs) ----
           Se mantiene st.metric: se coloca el icono a la izquierda, el
           numero en grande y la descripcion del texto por debajo. */
        [data-testid="stMetric"] {
            position: relative;
            background-color: #ffffff;
            border: 1px solid #eef0f3;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            padding: 1.1rem 1.3rem;
            height: 100%;
            transition: box-shadow 0.2s ease;
        }
        [data-testid="stMetric"]:hover {
            box-shadow: 0 6px 14px rgba(0, 0, 0, 0.08);
        }
        [data-testid="stMetric"] > div {
            display: flex;
            flex-direction: column;
        }
        [data-testid="stMetricValue"] {
            order: -1;
            margin-left: 2.5rem;
            font-size: 2.1rem;
            font-weight: 700;
            color: #1e293b;
            line-height: 1.15;
        }
        [data-testid="stMetricIcon"] {
            position: absolute;
            left: 1.3rem;
            top: 1.15rem;
            font-size: 1.4rem;
        }
        [data-testid="stMetricLabel"] p {
            font-size: 0.85rem;
            font-weight: 600;
            color: #1e293b;
            margin-top: 0.35rem;
        }

        /* ---- Tarjetas de contenido (graficos y tablas) ---- */
        [data-testid="stPlotlyChart"] {
            background-color: #ffffff;
            border: 1px solid #eef0f3;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            padding: 12px;
        }

        [data-testid="stDataFrame"] {
            background-color: #ffffff;
            border: 1px solid #eef0f3;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }

        /* ---- Tabla de reporte (HTML) con badges de estado ---- */
        .tabla-wrap {
            background-color: #ffffff;
            border: 1px solid #eef0f3;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            overflow: hidden;
        }
        .tabla-reportes {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }
        .tabla-reportes thead th {
            background-color: #f8f9fa;
            color: #1a1f36;
            font-weight: 600;
            text-align: left;
            padding: 10px 14px;
            border-bottom: 1px solid #eef0f3;
            white-space: nowrap;
        }
        .tabla-reportes tbody td {
            padding: 9px 14px;
            border-bottom: 1px solid #f1f3f5;
            color: #374151;
        }
        .tabla-reportes tbody tr:last-child td {
            border-bottom: none;
        }

        /* ---- Titulos de seccion ---- */
        h3, h2 {
            color: #1e293b;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True)


# --- Lectura de datos ------------------------------------------------------

def leer_texto(ruta_csv):
    """
    Devuelve el contenido del archivo como texto.

    Se prueban varias codificaciones porque el programa en C++ escribe lo que
    el usuario teclea en la consola de Windows y eso puede quedar guardado en
    UTF-8 o en la codificacion local (cp1252/latin-1). utf-8 se intenta
    primero y las otras son planes de respaldo para no fallar por un acento.
    """
    for codificacion in ("utf-8", "cp1252", "latin-1"):
        try:
            with open(ruta_csv, "r", encoding=codificacion) as archivo:
                return archivo.read()
        except UnicodeDecodeError:
            continue  # Se intenta con la siguiente codificacion.
    # Ultimo recurso: reemplazar los bytes que no se puedan decodificar.
    with open(ruta_csv, "r", encoding="utf-8", errors="replace") as archivo:
        return archivo.read()


@st.cache_data(show_spinner=False, ttl=1)
def cargar_datos(ruta_csv):
    """
    Lee datos.csv y devuelve un diccionario con tres DataFrames:
    'grupos', 'investigadores' y 'productos'.

    Devuelve None si el archivo no existe o si no se puede leer.

    @st.cache_data evita releer el archivo en cada interaccion del usuario,
    pero con ttl=1 (tiempo de vida de 1 segundo) la cache caduca casi de
    inmediato: al presionar "Rerun" o actualizar la pagina se vuelve a leer
    el datos.csv mas reciente.
    """
    if not os.path.exists(ruta_csv):
        return None

    try:
        contenido = leer_texto(ruta_csv)
        # header=None -> el CSV no tiene fila de encabezados.
        # names=range(7) -> se fija el maximo de columnas (el registro
        #   PRODUCTO tiene 7). Es imprescindible: sin esto, pandas deduce 4
        #   columnas de la primera linea (GRUPO) y falla con las lineas de
        #   INVESTIGADOR/PRODUCTO que tienen mas campos. Las filas cortas se
        #   rellenan solas.
        # dtype=str y keep_default_na=False -> todo se lee como texto y los
        #   campos vacios no se convierten en NaN.
        df = pd.read_csv(io.StringIO(contenido), header=None, names=range(10),
                         dtype=str, keep_default_na=False)
    except Exception:
        return None

    if df.empty:
        return None

    def filtrar_por_tipo(etiqueta, cantidad_columnas, nombres):
        """
        Toma las filas que empiezan con 'etiqueta', asegura que tengan
        'cantidad_columnas' columnas y les pone nombres legibles.
        """
        sub = df[df[0] == etiqueta].copy()
        sub = sub.reindex(columns=range(cantidad_columnas), fill_value="")
        sub.columns = nombres
        return sub.reset_index(drop=True)

    grupos = filtrar_por_tipo(
        "GRUPO", 5, ["tipo", "id_grupo", "grupo", "plan", "activo"])
    investigadores = filtrar_por_tipo(
        "INVESTIGADOR", 7,
        ["tipo", "id_grupo", "id", "investigador", "area", "categoria", "activo"])
    productos = filtrar_por_tipo(
        "PRODUCTO", 8,
        ["tipo", "id_grupo", "id", "titulo", "anio", "categoria", "validado", "activo"])

    # Conversion de tipos: los id y el anio a numero, validado a Si/No.
    grupos["id_grupo"] = pd.to_numeric(grupos["id_grupo"], errors="coerce")
    if "id_grupo" in investigadores:
        investigadores["id_grupo"] = pd.to_numeric(investigadores["id_grupo"],
                                                   errors="coerce")
    if "id_grupo" in productos:
        productos["id_grupo"] = pd.to_numeric(productos["id_grupo"],
                                              errors="coerce")

    if "id" in investigadores:
        investigadores["id"] = pd.to_numeric(investigadores["id"], errors="coerce")
    if "id" in productos:
        productos["id"] = pd.to_numeric(productos["id"], errors="coerce")
    if "anio" in productos:
        productos["anio"] = pd.to_numeric(productos["anio"],
                                          errors="coerce").fillna(0).astype(int)
    if "validado" in productos:
        productos["validado"] = productos["validado"].apply(
            lambda valor: "Si" if str(valor) == "1" else "No")

    if "activo" in productos:
        productos = productos[productos["activo"].astype(str) == "1"].copy()
    if "activo" in investigadores:
        investigadores = investigadores[investigadores["activo"].astype(str) == "1"].copy()
    if "activo" in grupos:
        grupos = grupos[grupos["activo"].astype(str) == "1"].copy()

    return {"grupos": grupos,
            "investigadores": investigadores,
            "productos": productos}


# --- Graficos --------------------------------------------------------------

def _estilo_plotly(figura):
    """
    Aplica el aspecto visual comun a todas las figuras: plantilla limpia,
    tipografia oscura y en negrilla, rejilla suave y margenes consistentes.

    Todo el texto de los graficos (titulo, titulos de los ejes, etiquetas de
    los ticks y leyenda) usa el mismo color casi negro (#1e293b) con peso
    negrita, para que se lea bien sobre las tarjetas blancas.
    """
    texto = "#1e293b"

    figura.update_layout(
        template="plotly_white",
        font=dict(family="Inter, Segoe UI, sans-serif", color=texto,
                  weight="bold"),
        title_font=dict(color=texto, size=16, weight="bold"),
        legend_font=dict(color=texto, weight="bold"),
        title_x=0.01,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=60, b=40, l=40, r=20))

    # Titulo de los ejes y etiquetas (ticks) en oscuro y negrita.
    eje = dict(title_font=dict(color=texto, weight="bold"),
               tickfont=dict(color=texto, weight="bold"))
    figura.update_xaxes(gridcolor="#eef0f3", zeroline=False, **eje)
    figura.update_yaxes(gridcolor="#eef0f3", zeroline=False, **eje)
    return figura


def construir_grafico_anio(productos_filtrados):
    """
    Devuelve una figura de Plotly con la cantidad de productos por anio,
    o None si no hay datos.
    """
    por_anio = productos_filtrados.groupby("anio").size().sort_index()
    if por_anio.empty:
        return None

    # Se pasa a DataFrame para que plotly.express pueda usar nombres de
    # columna claros en los ejes.
    datos = por_anio.reset_index()
    datos.columns = ["Año", "Cantidad de productos"]

    figura = px.bar(
        datos, x="Año", y="Cantidad de productos",
        text="Cantidad de productos",
        color="Cantidad de productos",
        color_continuous_scale=["#c7d2fe", COLOR_PRIMARIO],
        title="Productos por año")

    figura.update_traces(textposition="outside",
                         marker_line_width=0, width=0.6,
                         textfont=dict(color="#1e293b", weight="bold"))
    figura.update_layout(
        xaxis_title="Año de publicación",
        yaxis_title="Cantidad de productos",
        showlegend=False,
        coloraxis_showscale=False)
    return _estilo_plotly(figura)


def construir_grafico_evolucion(productos_filtrados):
    """
    Devuelve una figura de Plotly (grafico de lineas) con la evolucion de la
    cantidad de productos a lo largo del tiempo, o None si no hay datos.
    """
    por_anio = productos_filtrados.groupby("anio").size().sort_index()
    if por_anio.empty:
        return None

    datos = por_anio.reset_index()
    datos.columns = ["Año", "Cantidad de productos"]

    figura = px.line(
        datos, x="Año", y="Cantidad de productos",
        markers=True, title="Evolución de Productos")

    figura.update_traces(
        line=dict(width=3, color=COLOR_PRIMARIO),
        marker=dict(size=9, color=COLOR_PRIMARIO, line=dict(width=1.5,
                                                            color="#ffffff")),
        fill="tozeroy",
        fillcolor="rgba(67, 97, 238, 0.10)")
    figura.update_layout(
        xaxis_title="Año",
        yaxis_title="Cantidad de productos")
    return _estilo_plotly(figura)


def construir_grafico_categoria(productos_filtrados):
    """
    Devuelve una figura de Plotly (gráfico de torta) con la proporción de
    productos según su categoría (Artículo, Libro, Ponencia, etc.), o None
    si no hay datos.

    Se usa la misma paleta cualitativa que el resto del tablero para
    mantener una línea visual coherente.
    """
    # Si la categoría viene vacía en el CSV se agrupa como "Sin categoría"
    # para no perder esos productos en el gráfico.
    categorias = productos_filtrados["categoria"].replace("", "Sin categoría")
    conteo = categorias.value_counts()

    if conteo.empty:
        return None

    datos = conteo.reset_index()
    datos.columns = ["Categoría", "Cantidad de productos"]

    figura = px.pie(
        datos, names="Categoría", values="Cantidad de productos",
        color_discrete_sequence=PALETA_CATEGORICA,
        hole=0.45,
        title="Proporción por categoría")

    # Se muestra el porcentaje dentro de cada porcion. El texto va en
    # negrita y en blanco porque cae sobre rellenos de color saturado (si
    # fuera oscuro no se leeria); el titulo, los ejes y la leyenda si van
    # en oscuro como el resto del tablero.
    figura.update_traces(textposition="inside", textinfo="percent",
                         textfont=dict(color="#ffffff", weight="bold"),
                         marker=dict(line=dict(color="#ffffff", width=2)))
    return _estilo_plotly(figura)


def construir_grafico_investigador(productos_filtrados, investigadores_full):
    """
    Devuelve una figura de Plotly con la cantidad de productos por
    investigador, o None si no hay datos.

    El CSV no guarda una relacion directa producto-investigador: ambos
    pertenecen a un grupo. Por eso se cruzan los productos con los
    investigadores de su mismo grupo.
    """
    productos_por_investigador = productos_filtrados.merge(
        investigadores_full[["id_grupo", "investigador"]],
        on="id_grupo", how="inner")
    conteo = (productos_por_investigador
              .groupby("investigador").size()
              .sort_values(ascending=False))

    if conteo.empty:
        return None

    datos = conteo.reset_index()
    datos.columns = ["Investigador", "Cantidad de productos"]

    figura = px.bar(
        datos, x="Cantidad de productos", y="Investigador",
        text="Cantidad de productos",
        orientation="h",
        color="Investigador",
        color_discrete_sequence=PALETA_CATEGORICA,
        title="Productos por investigador")

    figura.update_traces(textposition="outside", marker_line_width=0,
                         textfont=dict(color="#1e293b", weight="bold"))
    figura.update_layout(
        xaxis_title="Cantidad de productos",
        yaxis_title="Investigador",
        showlegend=False,
        yaxis=dict(categoryorder="total ascending"))
    return _estilo_plotly(figura)


def construir_tabla_productos_html(tabla):
    """
    Devuelve la tabla de productos como HTML con la columna "Validado"
    convertida en una etiqueta visual (badge): fondo verde para "Validado" y
    fondo rojo para "Pendiente".

    Se usa el Styler de pandas (style.map) y el HTML se genera con to_html().
    El resultado se inyecta con st.markdown(unsafe_allow_html=True), de modo
    que las etiquetas con fondo de color se ven en cualquier navegador.
    """
    def estilo_badge(valor):
        if valor == "Validado":
            base = "background-color: #10b981; color: #ffffff;"
        elif valor == "Pendiente":
            base = "background-color: #ef4444; color: #ffffff;"
        else:
            base = "background-color: #f1f3f5; color: #6b7280;"
        return base + " font-weight: 700; text-align: center;"

    # Los estilos del encabezado y de la tabla en general se definen en el
    # CSS inyectado (.tabla-wrap / .tabla-reportes); aqui solo se colorean
    # las celdas de "Validado" con el badge.
    estilizador = tabla.style.map(estilo_badge, subset=["Validado"])
    estilizador = estilizador.hide(axis="index")
    estilizador = estilizador.set_table_attributes('class="tabla-reportes"')
    return '<div class="tabla-wrap">' + estilizador.to_html() + '</div>'


def main():
    inyectar_estilos()

    # --- 2. Encabezado -----------------------------------------------------
    st.markdown(
        """
        <div class="app-header">
            <h1>🔬 Dashboard de Investigación</h1>
            <p>Panel de control del centro de investigación. Supervisa grupos,
            investigadores y productos registrados desde el programa en C++.
            Usa la barra lateral para acotar la información.</p>
        </div>
        """,
        unsafe_allow_html=True)

    datos = cargar_datos(RUTA_CSV)

    # Manejo de error si el archivo no existe o esta vacio.
    if datos is None:
        st.warning(
            "No se encontró el archivo `../cpp/datos.csv` o no se pudo leer. "
            "Ejecuta el programa en C++ y usa la opción **Guardar datos** "
            "para generarlo.")
        st.stop()

    grupos = datos["grupos"]
    investigadores = datos["investigadores"]
    productos = datos["productos"]

    if grupos.empty and productos.empty:
        st.info("El archivo existe pero no contiene datos para mostrar.")
        st.stop()

    # Se agrega el nombre del grupo a investigadores y productos para poder
    # filtrar y mostrar por nombre en lugar de por id.
    investigadores_full = investigadores.merge(
        grupos[["id_grupo", "grupo"]], on="id_grupo", how="left")
    productos_full = productos.merge(
        grupos[["id_grupo", "grupo"]], on="id_grupo", how="left")

    # --- 7. Barra lateral con filtros --------------------------------------
    with st.sidebar:
        st.markdown('<div class="sidebar-brand">🔬 Panel de Control</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="sidebar-sub">Centro de Investigación</div>',
                    unsafe_allow_html=True)
        st.divider()

        st.markdown('<div class="filtro-titulo">Filtrar por grupo</div>',
                    unsafe_allow_html=True)
        opciones_grupo = ["Todos"] + sorted(
            grupos["grupo"].dropna().unique())
        grupo_seleccionado = st.selectbox(
            "Grupo", opciones_grupo, label_visibility="collapsed")

        # Los investigadores disponibles dependen del grupo elegido.
        if grupo_seleccionado == "Todos":
            investigadores_disponibles = investigadores_full
        else:
            investigadores_disponibles = investigadores_full[
                investigadores_full["grupo"] == grupo_seleccionado]

        st.markdown('<div class="filtro-titulo">Filtrar por investigador</div>',
                    unsafe_allow_html=True)
        opciones_investigador = ["Todos"] + sorted(
            investigadores_disponibles["investigador"].dropna().unique())
        investigador_seleccionado = st.selectbox(
            "Investigador", opciones_investigador, label_visibility="collapsed")

    # --- Aplicacion de los filtros -----------------------------------------
    productos_filtrados = productos_full.copy()
    investigadores_filtrados = investigadores_disponibles.copy()

    if grupo_seleccionado != "Todos":
        productos_filtrados = productos_filtrados[
            productos_filtrados["grupo"] == grupo_seleccionado]

    if investigador_seleccionado != "Todos":
        ids_grupos_inv = investigadores_full[
            investigadores_full["investigador"] == investigador_seleccionado
        ]["id_grupo"].unique()
        productos_filtrados = productos_filtrados[
            productos_filtrados["id_grupo"].isin(ids_grupos_inv)]
        investigadores_filtrados = investigadores_filtrados[
            investigadores_filtrados["investigador"] ==
            investigador_seleccionado]

    # --- 8. Barra lateral: descarga y recarga ------------------------------
    # Se dibuja despues de aplicar los filtros para que el reporte descargable
    # contenga exactamente los datos que el usuario esta viendo.
    with st.sidebar:
        st.divider()

        # Tablas filtradas con nombres de columna legibles (las mismas que se
        # muestran en las pestanas "Productos" e "Investigadores").
        reporte_productos = productos_filtrados[
            ["grupo", "id", "titulo", "anio", "categoria", "validado"]].rename(
            columns={"grupo": "Grupo", "id": "ID", "titulo": "Título",
                     "anio": "Año", "categoria": "Categoría",
                     "validado": "Validado"})
        reporte_investigadores = investigadores_filtrados[
            ["grupo", "id", "investigador", "area", "categoria"]].rename(
            columns={"grupo": "Grupo", "id": "ID",
                     "investigador": "Investigador",
                     "area": "Área de conocimiento",
                     "categoria": "Categoría"})

        # Se genera cada CSV por separado en memoria. utf-8-sig agrega la marca
        # BOM para que Excel muestre bien los acentos (Título, Año, Categoría).
        csv_productos = reporte_productos.to_csv(index=False).encode("utf-8-sig")
        csv_investigadores = (
            reporte_investigadores.to_csv(index=False).encode("utf-8-sig"))

        st.download_button(
            "📥 Descargar Productos (CSV)",
            data=csv_productos,
            file_name="productos_investigacion.csv",
            mime="text/csv",
            use_container_width=True)

        st.download_button(
            "📥 Descargar Investigadores (CSV)",
            data=csv_investigadores,
            file_name="investigadores_investigacion.csv",
            mime="text/csv",
            use_container_width=True)

        # Boton para forzar la recarga de los datos: limpia la cache de
        # st.cache_data y vuelve a ejecutar el script desde el principio.
        if st.button("🔄 Recargar datos", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # --- 3. Tarjetas de metricas (KPIs) ------------------------------------
    if grupo_seleccionado == "Todos":
        grupos_filtrados = grupos
    else:
        grupos_filtrados = grupos[grupos["grupo"] == grupo_seleccionado]

    columna1, columna2, columna3 = st.columns(3, gap="medium")
    columna1.metric("Grupos de investigación",
                    grupos_filtrados["id_grupo"].nunique(), icon="🏛️")
    columna2.metric("Investigadores",
                    investigadores_filtrados["investigador"].nunique(),
                    icon="👩‍🔬")
    columna3.metric("Productos", len(productos_filtrados), icon="📦")

    st.write("")

    # --- 4, 5 y 5b. Graficos en tres columnas ------------------------------
    # El aspecto de tarjeta (fondo blanco, bordes redondeados y sombra) lo
    # aporta el CSS sobre el propio contenedor del grafico.
    st.subheader("Análisis de la producción")
    columna_anio, columna_evolucion, columna_categoria = st.columns(3)

    with columna_anio:
        figura_anio = construir_grafico_anio(productos_filtrados)
        if figura_anio is None:
            st.info("No hay productos para los filtros seleccionados.")
        else:
            st.plotly_chart(figura_anio, use_container_width=True)

    with columna_evolucion:
        figura_evolucion = construir_grafico_evolucion(productos_filtrados)
        if figura_evolucion is None:
            st.info("No hay productos para los filtros seleccionados.")
        else:
            st.plotly_chart(figura_evolucion, use_container_width=True)

    with columna_categoria:
        figura_categoria = construir_grafico_categoria(productos_filtrados)
        if figura_categoria is None:
            st.info("No hay productos para los filtros seleccionados.")
        else:
            st.plotly_chart(figura_categoria, use_container_width=True)

    # El detalle por investigador se conserva debajo para no perder esa vista.
    figura_investigador = construir_grafico_investigador(
        productos_filtrados, investigadores_full)
    if figura_investigador is None:
        st.info("No hay productos para los filtros seleccionados.")
    else:
        st.plotly_chart(figura_investigador, use_container_width=True)

    st.write("")

    # --- 6. Tablas con los datos filtrados ---------------------------------
    st.subheader("Datos filtrados")
    pestana_productos, pestana_investigadores = st.tabs(
        ["📦 Productos", "👩‍🔬 Investigadores"])

    with pestana_productos:
        tabla_productos = productos_filtrados[
            ["grupo", "id", "titulo", "anio", "categoria", "validado"]].rename(
            columns={"grupo": "Grupo", "id": "ID", "titulo": "Título",
                     "anio": "Año", "categoria": "Categoría",
                     "validado": "Validado"}).copy()

        if tabla_productos.empty:
            st.info("No hay productos para los filtros seleccionados.")
        else:
            # La columna "Validado" se muestra como etiqueta visual
            # (badge): "Validado" en verde y "Pendiente" en rojo.
            tabla_productos["Validado"] = tabla_productos["Validado"].map(
                {"Si": "Validado", "No": "Pendiente"}).fillna("Pendiente")
            st.markdown(construir_tabla_productos_html(tabla_productos),
                        unsafe_allow_html=True)

    with pestana_investigadores:
        tabla_investigadores = investigadores_filtrados[
            ["grupo", "id", "investigador", "area", "categoria"]].rename(
            columns={"grupo": "Grupo", "id": "ID",
                     "investigador": "Investigador",
                     "area": "Área de conocimiento",
                     "categoria": "Categoría"})
        if tabla_investigadores.empty:
            st.info("No hay investigadores para los filtros seleccionados.")
        else:
            st.dataframe(tabla_investigadores, use_container_width=True,
                         hide_index=True)


if __name__ == "__main__":
    main()
