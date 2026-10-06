# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import plotly.express as px
from collections import Counter


def render(data, multilist, grupo_crud, investigador_crud, producto_crud, year_filter):
    """Renderiza vista por grupo."""
    st.header("Por Grupo")
    if not data or not data.get("grupos"):
        st.info("No hay datos cargados.")
        return

    productos = producto_crud.list_all()
    grupos = grupo_crud.list_all()

    for g in grupos:
        gid = getattr(g, 'id', None)
        prods = producto_crud.list_by_group(gid) if gid is not None else []
        if prods:
            counts_anio = Counter(getattr(p, 'anio', None) for p in prods if getattr(p, 'anio', None) is not None)
            fig = px.bar(x=list(counts_anio.keys()), y=list(counts_anio.values()), title=f"Productos por año - {getattr(g, 'nombre', 'Grupo')}")
            st.plotly_chart(fig, use_container_width=True)
            counts_cat = Counter(getattr(p, 'categoria', 'Desconocida') for p in prods)
            fig2 = px.histogram(x=list(counts_cat.keys()), title=f"Productos por categoría - {getattr(g, 'nombre', 'Grupo')}")
            st.plotly_chart(fig2, use_container_width=True)