# -*- coding: utf-8 -*-
"""Vista: Por Investigador."""

import streamlit as st
import plotly.express as px
from collections import Counter


def render(data, multilist, grupo_crud, investigador_crud, producto_crud, year_filter):
    """Renderiza vista por investigador."""
    st.header("Por Investigador")
    if not data or not data.get("grupos"):
        st.info("No hay datos cargados.")
        return

    invs = investigador_crud.list_all()
    for inv in invs:
        ced = getattr(inv, 'cedula', None)
        prods = producto_crud.list_by_investigador(ced) if ced else []
        if prods:
            counts_anio = Counter(getattr(p, 'anio', None) for p in prods if getattr(p, 'anio', None) is not None)
            fig = px.bar(x=list(counts_anio.keys()), y=list(counts_anio.values()), title=f"Productos por año - {getattr(inv, 'nombres', '')}")
            st.plotly_chart(fig, use_container_width=True)
            counts_tipo = Counter(getattr(p, 'tipo', 'Desconocido') for p in prods)
            fig2 = px.bar(x=list(counts_tipo.keys()), y=list(counts_tipo.values()), title=f"Productos por tipo - {getattr(inv, 'nombres', '')}")
            st.plotly_chart(fig2, use_container_width=True)