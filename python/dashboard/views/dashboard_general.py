# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import plotly.express as px
from collections import Counter


def render(data, multilist, grupo_crud, investigador_crud, producto_crud, year_filter):
    """Renderiza el dashboard general."""
    st.header("Dashboard General")
    if not data or not data.get("grupos"):
        st.info("No hay datos cargados.")
        return

    productos = producto_crud.list_all()
    grupos = grupo_crud.list_all()
    invs = investigador_crud.list_all()

    col1, col2, col3 = st.columns(3)
    col1.metric("Grupos activos", len(grupos))
    col2.metric("Investigadores activos", len(invs))
    col3.metric("Productos activos", len(productos))

    filtered = []
    for p in productos:
        a = getattr(p, 'anio', None)
        if year_filter == "Todos":
            filtered.append(p)
        elif year_filter == "Últimos 2 años":
            if a is not None and a >= 2024:
                filtered.append(p)
        elif year_filter == "Últimos 5 años":
            if a is not None and a >= 2021:
                filtered.append(p)
        elif year_filter == "Personalizado":
            filtered.append(p)

    if filtered:
        counts_anio = Counter(getattr(p, 'anio', None) for p in filtered if getattr(p, 'anio', None) is not None)
        fig1 = px.bar(x=list(counts_anio.keys()), y=list(counts_anio.values()), title="Productos por año")
        st.plotly_chart(fig1, use_container_width=True)

        counts_tipo = Counter(getattr(p, 'tipo', 'Desconocido') for p in filtered)
        fig2 = px.bar(x=list(counts_tipo.keys()), y=list(counts_tipo.values()), title="Productos por tipo")
        st.plotly_chart(fig2, use_container_width=True)

        counts_cat = Counter(getattr(p, 'categoria', 'Desconocida') for p in filtered)
        fig3 = px.histogram(x=list(counts_cat.keys()), title="Productos por categoría")
        st.plotly_chart(fig3, use_container_width=True)