# -*- coding: utf-8 -*-
"""Pestaña de Estadísticas y Analítica de Investigación."""

from typing import List, Dict
from collections import Counter
import customtkinter as ctk

from gui.styles import (
    COLORS,
    CHART_COLORS,
    SPACING,
    font,
    button,
    card,
)
from gui.widgets.stat_card import StatCard
from gui.widgets.chart_widget import ChartWidget


class EstadisticasTab(ctk.CTkFrame):
    """Muestra métricas resumidas y visualizaciones gráficas de la actividad científica."""

    def __init__(self, master, app=None):
        super().__init__(master, fg_color='transparent')
        self._app_ref = app
        self.pack(fill='both', expand=True)

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- 1. Encabezado ---
        self.header_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.header_frame.grid(
            row=0,
            column=0,
            sticky='ew',
            padx=SPACING['lg'],
            pady=(SPACING['lg'], SPACING['md']),
        )

        self.header_left = ctk.CTkFrame(self.header_frame, fg_color='transparent')
        self.header_left.pack(side='left', fill='x', expand=True)

        self.title_label = ctk.CTkLabel(
            self.header_left,
            text="Estadísticas de investigación",
            font=font('display'),
            text_color=COLORS['ink'],
            anchor='w',
        )
        self.title_label.pack(fill='x', anchor='w')

        self.subtitle_label = ctk.CTkLabel(
            self.header_left,
            text="Consolidado de productividad científica, investigadores y grupos",
            font=font('body'),
            text_color=COLORS['muted'],
            anchor='w',
        )
        self.subtitle_label.pack(fill='x', anchor='w', pady=(SPACING['xs'], 0))

        # Botón actualizar terciario unificado
        self.btn_refresh = button(
            self.header_frame,
            text="Actualizar",
            variant='tertiary',
            command=self.refresh,
        )
        self.btn_refresh.pack(side='right')

        # --- 2. Tarjetas de métricas (3 columnas uniformes compactas sin emojis) ---
        self.stats_container = ctk.CTkFrame(self, fg_color='transparent')
        self.stats_container.grid(
            row=1,
            column=0,
            sticky='ew',
            padx=SPACING['lg'],
            pady=(0, SPACING['md']),
        )
        self.stats_container.grid_columnconfigure((0, 1, 2), weight=1, uniform='stats_cols')

        self.card_grupos = StatCard(
            self.stats_container,
            title="Grupos registrados",
            value="0",
            icon="",
            variation="0 activos",
            accent_color=CHART_COLORS[0],
        )
        self.card_grupos.grid(row=0, column=0, sticky='nsew', padx=(0, SPACING['sm']))

        self.card_investigadores = StatCard(
            self.stats_container,
            title="Investigadores",
            value="0",
            icon="",
            variation="0 activos",
            accent_color=CHART_COLORS[1],
        )
        self.card_investigadores.grid(row=0, column=1, sticky='nsew', padx=(SPACING['sm'], SPACING['sm']))

        self.card_productos = StatCard(
            self.stats_container,
            title="Producción científica",
            value="0",
            icon="",
            variation="0 validados",
            accent_color=CHART_COLORS[2],
        )
        self.card_productos.grid(row=0, column=2, sticky='nsew', padx=(SPACING['sm'], 0))

        # --- 3. Gráficos (3 columnas uniformes, cada uno dentro de su tarjeta con estado vacío) ---
        self.charts_container = ctk.CTkFrame(self, fg_color='transparent')
        self.charts_container.grid(
            row=2,
            column=0,
            sticky='nsew',
            padx=SPACING['lg'],
            pady=(0, SPACING['lg']),
        )
        self.charts_container.grid_rowconfigure(0, weight=1)
        self.charts_container.grid_columnconfigure((0, 1, 2), weight=1, uniform='charts_cols')

        # Tarjeta para Gráfico 1 (Productos por año)
        self.card_chart1 = card(self.charts_container)
        self.card_chart1.grid(row=0, column=0, sticky='nsew', padx=(0, SPACING['sm']))
        self.chart1 = ChartWidget(self.card_chart1, title="Productos por año")
        self.chart1.pack(fill='both', expand=True, padx=SPACING['sm'], pady=SPACING['sm'])

        # Tarjeta para Gráfico 2 (Productos por tipo)
        self.card_chart2 = card(self.charts_container)
        self.card_chart2.grid(row=0, column=1, sticky='nsew', padx=(SPACING['sm'], SPACING['sm']))
        self.chart2 = ChartWidget(self.card_chart2, title="Productos por tipo")
        self.chart2.pack(fill='both', expand=True, padx=SPACING['sm'], pady=SPACING['sm'])

        # Tarjeta para Gráfico 3 (Investigadores por grupo)
        self.card_chart3 = card(self.charts_container)
        self.card_chart3.grid(row=0, column=2, sticky='nsew', padx=(SPACING['sm'], 0))
        self.chart3 = ChartWidget(self.card_chart3, title="Investigadores por grupo")
        self.chart3.pack(fill='both', expand=True, padx=SPACING['sm'], pady=SPACING['sm'])

        self.refresh()

    def get_app(self):
        """Resuelve dinámicamente la instancia principal de App en la jerarquía."""
        if self._app_ref is not None:
            return self._app_ref
        curr = self
        while curr is not None:
            if hasattr(curr, 'grupo_crud'):
                self._app_ref = curr
                return curr
            curr = getattr(curr, 'master', None)
        return None

    def refresh(self):
        """Calcula las métricas actuales y actualiza las tarjetas y gráficos."""
        app = self.get_app()
        if not app:
            return

        # 1. Obtención de datos de grupos
        all_grupos = []
        try:
            curr = app.multilista.head_group
            while curr is not None:
                all_grupos.append(curr.data)
                curr = curr.next
        except Exception:
            try:
                all_grupos = list(app.grupo_crud.list_all())
            except Exception:
                all_grupos = []

        # 2. Obtención de investigadores
        all_investigadores = []
        try:
            curr_g = app.multilista.head_group
            while curr_g is not None:
                curr_i = curr_g.sublist
                while curr_i is not None:
                    all_investigadores.append(curr_i.data)
                    curr_i = curr_i.next
                curr_g = curr_g.next
        except Exception:
            try:
                all_investigadores = list(app.inv_crud.list_all())
            except Exception:
                all_investigadores = []

        # 3. Obtención de productos
        all_productos = []
        try:
            curr_g = app.multilista.head_group
            while curr_g is not None:
                curr_i = curr_g.sublist
                while curr_i is not None:
                    curr_p = curr_i.sublist
                    while curr_p is not None:
                        all_productos.append(curr_p.data)
                        curr_p = curr_p.next
                    curr_i = curr_i.next
                curr_g = curr_g.next
        except Exception:
            try:
                all_productos = list(app.prod_crud.list_all())
            except Exception:
                all_productos = []

        # 4. Cálculos para StatCards
        total_g = len(all_grupos)
        act_g = sum(1 for g in all_grupos if getattr(g, 'activo', getattr(g, 'active', True)))
        var_g = f"{act_g} activos" if total_g > 0 else "Sin registros"

        total_i = len(all_investigadores)
        act_i = sum(1 for i in all_investigadores if getattr(i, 'activo', getattr(i, 'active', True)))
        var_i = f"{act_i} activos" if total_i > 0 else "Sin registros"

        total_p = len(all_productos)
        act_p = sum(1 for p in all_productos if getattr(p, 'validado', getattr(p, 'active', True)))
        var_p = f"{act_p} validados" if total_p > 0 else "Sin registros"

        self.card_grupos.set_value(str(total_g), variation=var_g)
        self.card_investigadores.set_value(str(total_i), variation=var_i)
        self.card_productos.set_value(str(total_p), variation=var_p)

        # 5. Gráfico 1: Productos por año (solo activos)
        years_counter = Counter()
        for p in all_productos:
            if getattr(p, 'validado', getattr(p, 'active', True)):
                try:
                    y = int(getattr(p, 'anio', 0) or getattr(p, 'year', 0))
                    if y > 1900:
                        years_counter[y] += 1
                except Exception:
                    pass

        if years_counter:
            sorted_years = sorted(years_counter.keys())
            chart1_labels = [str(y) for y in sorted_years]
            chart1_values = [years_counter[y] for y in sorted_years]
        else:
            chart1_labels, chart1_values = [], []

        self.chart1.plot_bar(
            chart1_labels,
            chart1_values,
            title="Productos por año",
            color=CHART_COLORS[0],
        )

        # 6. Gráfico 2: Productos por tipo
        types_counter = Counter()
        for p in all_productos:
            if getattr(p, 'validado', getattr(p, 'active', True)):
                t = getattr(p, 'tipo', '') or getattr(p, 'type', '')
                if t:
                    types_counter[str(t).strip()] += 1

        if types_counter:
            chart2_labels = list(types_counter.keys())
            chart2_values = [types_counter[k] for k in chart2_labels]
        else:
            chart2_labels, chart2_values = [], []

        self.chart2.plot_bar(
            chart2_labels,
            chart2_values,
            title="Productos por tipo",
            color=CHART_COLORS[1],
        )

        # 7. Gráfico 3: Investigadores por grupo
        group_names: Dict[int, str] = {}
        for g in all_grupos:
            gid = getattr(g, 'id', None)
            gcode = getattr(g, 'codigo_gruplac', '') or getattr(g, 'code', '') or getattr(g, 'nombre', f"G{gid}")
            if gid is not None:
                group_names[gid] = str(gcode)

        inv_group_counter = Counter()
        for i in all_investigadores:
            if getattr(i, 'activo', getattr(i, 'active', True)):
                gid = getattr(i, 'grupo_id', getattr(i, 'group', None))
                if gid is not None:
                    try:
                        gid_int = int(gid)
                        label = group_names.get(gid_int, f"Grupo {gid_int}")
                    except ValueError:
                        label = str(gid)
                    inv_group_counter[label] += 1

        if inv_group_counter:
            chart3_labels = list(inv_group_counter.keys())
            chart3_values = [inv_group_counter[k] for k in chart3_labels]
        else:
            chart3_labels, chart3_values = [], []

        self.chart3.plot_bar(
            chart3_labels,
            chart3_values,
            title="Investigadores por grupo",
            color=CHART_COLORS[3],
        )