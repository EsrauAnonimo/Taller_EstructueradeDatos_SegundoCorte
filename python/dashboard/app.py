# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from persistencia.persistencia_postgres import PersistenciaPostgres
from modelos.multilista import Multilist
from crud.crud_grupos import GrupoCRUD
from crud.crud_investigadores import InvestigadorCRUD
from crud.crud_productos import ProductoCRUD
from dashboard.views import dashboard_general, por_grupo, por_investigador, por_producto
from dashboard import styles


@st.cache_data
def load_data():
    """Carga datos desde PostgreSQL."""
    try:
        persistencia = PersistenciaPostgres()
        data = persistencia.load()
        multilist = PersistenciaPostgres.to_multilist(data)
        return data, multilist
    except Exception as e:
        return None, None


def main():
    """Punto de entrada del dashboard."""
    st.set_page_config(page_title="PEA-i", layout="wide")
    st.markdown(
        f"""
        <style>
            .stApp {{ background-color: {styles.BACKGROUND}; }}
            h1, h2, h3 {{ font-family: 'Georgia', serif; color: {styles.TEXT_PRIMARY}; }}
            body {{ font-family: 'Inter', sans-serif; color: {styles.TEXT_SECONDARY}; }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    data, multilist = load_data()
    if multilist is None:
        multilist = Multilist()

    grupo_crud = GrupoCRUD(multilist)
    investigador_crud = InvestigadorCRUD(multilist)
    producto_crud = ProductoCRUD(multilist)

    with st.sidebar:
        st.title("PEA-i")
        year_filter = st.selectbox(
            "Filtro por año",
            ["Todos", "Últimos 2 años", "Últimos 5 años", "Personalizado"],
        )

    pages = [
        st.Page(lambda: dashboard_general.render(data, multilist, grupo_crud, investigador_crud, producto_crud, year_filter), title="Dashboard General"),
        st.Page(lambda: por_grupo.render(data, multilist, grupo_crud, investigador_crud, producto_crud, year_filter), title="Por Grupo"),
        st.Page(lambda: por_investigador.render(data, multilist, grupo_crud, investigador_crud, producto_crud, year_filter), title="Por Investigador"),
        st.Page(lambda: por_producto.render(data, multilist, grupo_crud, investigador_crud, producto_crud, year_filter), title="Por Producto"),
    ]

    pg = st.navigation(pages)
    pg.run()


if __name__ == "__main__":
    main()