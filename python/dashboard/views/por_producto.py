# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import plotly.express as px
from collections import Counter


def render(data, multilist, grupo_crud, investigador_crud, producto_crud, year_filter):
    """Renderiza vista por producto."""
    st.header("Por Producto")
    if not data or not data.get("grupos"):
        st.info("No hay datos cargados.")
        return

    productos = producto_crud.list_all()
    if productos:
        counts_tipo = Counter(getattr(p, 'tipo', 'Desconocido') for p in productos)
        fig = px.bar(x=list(counts_tipo.keys()), y=list(counts_tipo.values()), title="Productos por tipo")
        st.plotly_chart(fig, use_container_width=True)
        counts_cat = Counter(getattr(p, 'categoria', 'Desconocida') for p in productos)
        fig2 = px.histogram(x=list(counts_cat.keys()), title="Productos por categoría")
        st.plotly_chart(fig2, use_container_width=True)