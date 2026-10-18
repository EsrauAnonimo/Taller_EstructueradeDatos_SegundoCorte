# -*- coding: utf-8 -*-
"""
dashboard.py
Dashboard interactivo (Streamlit) para visualizar los datos generados por el
programa en C++ del taller. Disenado como el panel de control de un centro de
investigacion.

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
        df = pd.read_csv(io.StringIO(contenido), header=None, names=range(7),
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
        "GRUPO", 4, ["tipo", "id_grupo", "grupo", "plan"])
    investigadores = filtrar_por_tipo(
        "INVESTIGADOR", 6,
        ["tipo", "id_grupo", "id", "investigador", "area", "categoria"])
    productos = filtrar_por_tipo(
        "PRODUCTO", 7,
        ["tipo", "id_grupo", "id", "titulo", "anio", "categoria", "validado"])

    # Conversion de tipos: los id y el anio a numero, validado a Si/No.
    grupos["id_grupo"] = pd.to_numeric(grupos["id_grupo"], errors="coerce")
    investigadores["id_grupo"] = pd.to_numeric(investigadores["id_grupo"],
                                               errors="coerce")
    productos["id_grupo"] = pd.to_numeric(productos["id_grupo"],
                                          errors="coerce")

    investigadores["id"] = pd.to_numeric(investigadores["id"], errors="coerce")
    productos["id"] = pd.to_numeric(productos["id"], errors="coerce")
    productos["anio"] = pd.to_numeric(productos["anio"],
                                      errors="coerce").fillna(0).astype(int)
    productos["validado"] = productos["validado"].apply(
        lambda valor: "Si" if str(valor) == "1" else "No")

    return {"grupos": grupos,
            "investigadores": investigadores,
            "productos": productos}


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
        color_continuous_scale="Blues",
        title="Distribución de productos por año")

    figura.update_traces(textposition="outside")
    figura.update_layout(
        template="plotly_white",
        xaxis_title="Año de publicación",
        yaxis_title="Cantidad de productos",
        showlegend=False,
        coloraxis_showscale=False,
        title_x=0.01,
        margin=dict(t=60, b=40, l=40, r=20))
    return figura


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
        datos, x="Investigador", y="Cantidad de productos",
        text="Cantidad de productos",
        color="Investigador",
        color_discrete_sequence=px.colors.qualitative.Bold,
        title="Productos por investigador")

    figura.update_traces(textposition="outside")
    figura.update_layout(
        template="plotly_white",
        xaxis_title="Investigador",
        yaxis_title="Cantidad de productos",
        showlegend=False,
        title_x=0.01,
        margin=dict(t=60, b=40, l=40, r=20))
    return figura


def construir_grafico_categoria(productos_filtrados):
    """
    Devuelve una figura de Plotly (gráfico de torta) con la proporción de
    productos según su categoría (Artículo, Libro, Ponencia, etc.), o None
    si no hay datos.

    Se usa la misma paleta cualitativa que el gráfico por investigador para
    que todo el tablero mantenga una línea visual coherente.
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
        color_discrete_sequence=px.colors.qualitative.Bold,
        title="Proporción de productos por categoría")

    # Se muestra el nombre de la categoría y su porcentaje dentro de cada
    # porción; el valor absoluto queda al pasar el cursor.
    figura.update_traces(textposition="inside", textinfo="percent+label")
    figura.update_layout(
        template="plotly_white",
        title_x=0.01,
        margin=dict(t=60, b=40, l=40, r=40))
    return figura


def main():
    # --- 2. Encabezado -----------------------------------------------------
    st.title("🔬 Dashboard de Investigación")
    st.markdown("#### Panel de control del centro de investigación")
    st.markdown(
        "Supervisa la producción científica del centro: **grupos**, "
        "**investigadores** y **productos** registrados desde el programa en "
        "C++. Usa la barra lateral para acotar la información.")

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
        st.title("Panel de Control")
        st.markdown("Centro de Investigación")
        st.divider()

        st.subheader("Filtro por Grupo")
        opciones_grupo = ["Todos"] + sorted(
            grupos["grupo"].dropna().unique())
        grupo_seleccionado = st.selectbox("Grupo", opciones_grupo)

        # Los investigadores disponibles dependen del grupo elegido.
        if grupo_seleccionado == "Todos":
            investigadores_disponibles = investigadores_full
        else:
            investigadores_disponibles = investigadores_full[
                investigadores_full["grupo"] == grupo_seleccionado]

        st.subheader("Filtro por Investigador")
        opciones_investigador = ["Todos"] + sorted(
            investigadores_disponibles["investigador"].dropna().unique())
        investigador_seleccionado = st.selectbox(
            "Investigador", opciones_investigador)

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

    # --- 3. Tarjetas de metricas -------------------------------------------
    if grupo_seleccionado == "Todos":
        grupos_filtrados = grupos
    else:
        grupos_filtrados = grupos[grupos["grupo"] == grupo_seleccionado]

    columna1, columna2, columna3 = st.columns(3)
    columna1.metric("Grupos de investigación",
                    grupos_filtrados["id_grupo"].nunique(), border=True)
    columna2.metric("Investigadores",
                    investigadores_filtrados["investigador"].nunique(),
                    border=True)
    columna3.metric("Productos", len(productos_filtrados), border=True)

    st.divider()

    # --- 4 y 5. Graficos profesionales en dos columnas ---------------------
    st.subheader("Análisis de la producción")
    columna_izquierda, columna_derecha = st.columns(2)

    with columna_izquierda:
        figura_anio = construir_grafico_anio(productos_filtrados)
        if figura_anio is None:
            st.info("No hay productos para los filtros seleccionados.")
        else:
            st.plotly_chart(figura_anio, use_container_width=True)

    with columna_derecha:
        figura_investigador = construir_grafico_investigador(
            productos_filtrados, investigadores_full)
        if figura_investigador is None:
            st.info("No hay productos para los filtros seleccionados.")
        else:
            st.plotly_chart(figura_investigador, use_container_width=True)

    # --- 5b. Grafico de torta: proporcion por categoria --------------------
    st.subheader("Distribución por categoría")

    figura_categoria = construir_grafico_categoria(productos_filtrados)
    if figura_categoria is None:
        st.info("No hay productos para los filtros seleccionados.")
    else:
        # Se centra el grafico con columnas proporcionales para que la torta
        # no quede ni muy estirada ni pegada a los bordes en pantallas anchas.
        columna_torta_izq, columna_torta_centro, columna_torta_der = (
            st.columns([1, 2, 1]))
        with columna_torta_centro:
            st.plotly_chart(figura_categoria, use_container_width=True)

    st.divider()

    # --- 6. Tablas con los datos filtrados ---------------------------------
    st.subheader("Datos filtrados")
    pestana_productos, pestana_investigadores = st.tabs(
        ["📦 Productos", "👩‍🔬 Investigadores"])

    with pestana_productos:
        tabla_productos = productos_filtrados[
            ["grupo", "id", "titulo", "anio", "categoria", "validado"]].rename(
            columns={"grupo": "Grupo", "id": "ID", "titulo": "Título",
                     "anio": "Año", "categoria": "Categoría",
                     "validado": "Validado"})
        if tabla_productos.empty:
            st.info("No hay productos para los filtros seleccionados.")
        else:
            st.dataframe(tabla_productos, use_container_width=True,
                         hide_index=True)

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
