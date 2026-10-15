# -*- coding: utf-8 -*-
"""Pestana de Estadisticas y Analitica de Investigacion – rediseno completo."""

from typing import List, Dict, Any, Optional
from collections import Counter
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import matplotlib.pyplot as plt
import pandas as pd

from gui.styles import (
    COLORS,
    CHART_COLORS,
    SPACING,
    RADIUS,
    CONTROL_HEIGHT,
    font,
    button,
    card,
    entry,
    combo,
)
from gui.widgets.stat_card import StatCard
from gui.widgets.chart_widget import ChartWidget
from entidades.taxonomia_minciencias import get_by_nombre


# ---------------------------------------------------------------------------
# Helpers para iterar sobre la estructura de datos (Multilista o CRUD)
# ---------------------------------------------------------------------------

def _iter_grupos(app):
    try:
        curr = app.multilista.head_group
        while curr is not None:
            yield curr.data
            curr = curr.next
        return
    except Exception:
        pass
    try:
        yield from app.grupo_crud.list_all()
    except Exception:
        pass


def _iter_investigadores(app):
    try:
        curr_g = app.multilista.head_group
        while curr_g is not None:
            curr_i = curr_g.sublist
            while curr_i is not None:
                yield curr_i.data
                curr_i = curr_i.next
            curr_g = curr_g.next
        return
    except Exception:
        pass
    try:
        yield from app.inv_crud.list_all()
    except Exception:
        pass


def _iter_productos(app):
    try:
        curr_g = app.multilista.head_group
        while curr_g is not None:
            curr_i = curr_g.sublist
            while curr_i is not None:
                curr_p = curr_i.sublist
                while curr_p is not None:
                    yield curr_p.data
                    curr_p = curr_p.next
                curr_i = curr_i.next
            curr_g = curr_g.next
        return
    except Exception:
        pass
    try:
        yield from app.prod_crud.list_all()
    except Exception:
        pass


def _is_active(obj):
    return bool(getattr(obj, "activo", getattr(obj, "active", True)))


def _is_validated(obj):
    return bool(getattr(obj, "validado", getattr(obj, "active", True)))


def _group_id(grupo) -> str:
    return str(getattr(grupo, "id", "") or getattr(grupo, "codigo_gruplac", "") or "")


def _investigator_id(investigador) -> str:
    return str(
        getattr(investigador, "cedula", None)
        or getattr(investigador, "id", None)
        or ""
    )


def _investigator_group_id(investigador) -> str:
    return str(getattr(investigador, "grupo_id", "") or getattr(investigador, "group", "") or "")


def _product_group_id(producto) -> str:
    return str(getattr(producto, "grupo_id", "") or getattr(producto, "group", "") or "")


def _product_investigator_id(producto) -> str:
    return str(
        getattr(producto, "investigador_id", None)
        or getattr(producto, "investigador_cedula", None)
        or getattr(producto, "inv_id", "")
        or ""
    )


def _get_field(obj, *keys, default=None):
    """Obtiene el primer valor no nulo ni vacio buscando en atributos o claves si es dict."""
    if obj is None:
        return default
    is_dict = isinstance(obj, dict)
    for k in keys:
        if is_dict:
            val = obj.get(k)
        else:
            val = getattr(obj, k, None)
        if val is not None and str(val).strip() != "":
            return val
    return default


def _product_year(producto) -> Optional[int]:
    """Devuelve el año del producto como entero en rango valido (1900..actual), o None si no es válido."""
    raw = _get_field(producto, "anio", "year")
    if raw is None:
        return None
    try:
        y = int(raw)
        return y if 1900 <= y <= datetime.datetime.now().year else None
    except (ValueError, TypeError):
        return None


def _normalize_gran_categoria(gc_raw: Any, tipo_raw: str = "") -> Optional[str]:
    """Normaliza las grandes categorías MinCiencias a sus siglas canónicas: GNC, DTI, ASC, FRH."""
    if not gc_raw and tipo_raw:
        sub = get_by_nombre(str(tipo_raw))
        if sub and sub.get("gran_categoria"):
            gc_raw = sub["gran_categoria"]
    if not gc_raw:
        return None
    s = str(gc_raw).strip().upper()
    if s in ("GNC", "NUEVO CONOCIMIENTO", "GENERACIÓN DE NUEVO CONOCIMIENTO", "GENERACION DE NUEVO CONOCIMIENTO"):
        return "GNC"
    if s in ("DTI", "DESARROLLO TECNOLÓGICO", "DESARROLLO TECNOLOGICO", "DESARROLLO TECNOLÓGICO E INNOVACIÓN", "DESARROLLO TECNOLOGICO E INNOVACION"):
        return "DTI"
    if s in ("ASC", "APROPIACIÓN SOCIAL", "APROPIACION SOCIAL", "APROPIACIÓN SOCIAL DEL CONOCIMIENTO", "APROPIACION SOCIAL DEL CONOCIMIENTO"):
        return "ASC"
    if s in ("FRH", "FORMACIÓN DE RECURSO HUMANO", "FORMACION DE RECURSO HUMANO", "FORMACIÓN DE TALENTO HUMANO", "RECURSO HUMANO"):
        return "FRH"
    for code, full in [("GNC", "CONOCIMIENTO"), ("DTI", "TECNOL"), ("ASC", "APROPIA"), ("FRH", "HUMANO")]:
        if full in s:
            return code
    return None


# ---------------------------------------------------------------------------
# Contenedor de tarjeta de grafico individual
# ---------------------------------------------------------------------------

class ChartCard(ctk.CTkFrame):
    """Tarjeta contenedora con borde sutil para envolver un ChartWidget."""

    def __init__(self, master, title: str, height: int = 340, **kwargs):
        super().__init__(
            master,
            corner_radius=RADIUS["card"],
            fg_color=COLORS["surface"],
            border_width=1,
            border_color=COLORS["border"],
            height=height,
            **kwargs,
        )
        self.chart = ChartWidget(self, title=title)
        self.chart.pack(fill="both", expand=True, padx=4, pady=4)


# ---------------------------------------------------------------------------
# Pestana principal EstadisticasTab
# ---------------------------------------------------------------------------

class EstadisticasTab(ctk.CTkScrollableFrame):
    """Dashboard analitico con KPIs compactos, filtros reactivos, resumen
    estadistico con pandas y graficos Matplotlib responsivos y optimizados.
    """

    def __init__(self, master, app=None):
        super().__init__(master, fg_color="transparent")
        self._app_ref = app
        self.pack(fill="both", expand=True)

        # Variables de estado de filtrado
        self._view_mode = "Global"  # Global, Por grupo, Por investigador
        self._selected_target_id: Optional[str] = None
        self._target_choices: Dict[str, str] = {}  # Label -> ID

        # Construccion de la UI
        self._build_header()
        self._build_kpi_row()
        self._build_filters_bar()
        self._build_summary_card()
        self._build_charts_grid()

        # Cache de columnas de grid para resize responsivo
        self._current_cols = 0
        self._charts_container.bind("<Configure>", self._on_container_resize)

        self.refresh()

    # -----------------------------------------------------------------------
    # 1. Encabezado con botones de accion
    # -----------------------------------------------------------------------

    def _build_header(self):
        self._header = ctk.CTkFrame(self, fg_color="transparent")
        self._header.pack(fill="x", padx=SPACING["lg"], pady=(SPACING["lg"], SPACING["sm"]))

        left = ctk.CTkFrame(self._header, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            left,
            text="Estadisticas de investigacion",
            font=font("display"),
            text_color=COLORS["ink"],
            anchor="w",
        ).pack(fill="x", anchor="w")

        ctk.CTkLabel(
            left,
            text="Analitica de productividad cientifica, distribucion de investigadores y grupos",
            font=font("body"),
            text_color=COLORS["muted"],
            anchor="w",
        ).pack(fill="x", anchor="w", pady=(SPACING["xs"], 0))

        # Botones a la derecha
        right = ctk.CTkFrame(self._header, fg_color="transparent")
        right.pack(side="right")

        self._btn_export = button(
            right,
            text="📷  Exportar grafica (PNG)",
            variant="secondary",
            command=self._export_png,
        )
        self._btn_export.pack(side="left", padx=(0, SPACING["sm"]))

        self._btn_refresh = button(
            right,
            text="⟳  Actualizar",
            variant="primary",
            command=self.refresh,
        )
        self._btn_refresh.pack(side="left")

    # -----------------------------------------------------------------------
    # 2. Tarjetas KPI compactas (110 px)
    # -----------------------------------------------------------------------

    def _build_kpi_row(self):
        self._kpi_container = ctk.CTkFrame(self, fg_color="transparent")
        self._kpi_container.pack(fill="x", padx=SPACING["lg"], pady=(0, SPACING["md"]))
        self._kpi_container.grid_columnconfigure((0, 1, 2), weight=1, uniform="kpi")

        self.card_grupos = StatCard(
            self._kpi_container,
            title="Grupos registrados",
            value="0",
            icon="👥",
            variation="0 activos",
            accent_color=CHART_COLORS[0],
        )
        self.card_grupos.grid(row=0, column=0, sticky="nsew", padx=(0, SPACING["sm"]))

        self.card_investigadores = StatCard(
            self._kpi_container,
            title="Investigadores",
            value="0",
            icon="🎓",
            variation="0 activos",
            accent_color=CHART_COLORS[1],
        )
        self.card_investigadores.grid(row=0, column=1, sticky="nsew",
                                      padx=(SPACING["sm"], SPACING["sm"]))

        self.card_productos = StatCard(
            self._kpi_container,
            title="Produccion cientifica",
            value="0",
            icon="📚",
            variation="0 validados",
            accent_color=CHART_COLORS[2],
        )
        self.card_productos.grid(row=0, column=2, sticky="nsew", padx=(SPACING["sm"], 0))

    # -----------------------------------------------------------------------
    # 3. Barra de filtros: Selector de Vista + Filtro de Ano
    # -----------------------------------------------------------------------

    def _build_filters_bar(self):
        self._filters_card = card(self)
        self._filters_card.pack(fill="x", padx=SPACING["lg"], pady=(0, SPACING["md"]))

        inner = ctk.CTkFrame(self._filters_card, fg_color="transparent")
        inner.pack(fill="x", padx=SPACING["md"], pady=SPACING["sm"])

        # Zona Izquierda: Selector de Vista (Global, Por grupo, Por investigador)
        v_left = ctk.CTkFrame(inner, fg_color="transparent")
        v_left.pack(side="left", fill="x")

        ctk.CTkLabel(
            v_left,
            text="Vista:",
            font=font("heading"),
            text_color=COLORS["ink"],
        ).pack(side="left", padx=(0, SPACING["sm"]))

        self._view_var = ctk.StringVar(value="Global")
        self._view_menu = combo(
            v_left,
            values=["Global", "Por grupo", "Por investigador"],
            variable=self._view_var,
            command=self._on_view_changed,
            width=170,
        )
        self._view_menu.pack(side="left", padx=(0, SPACING["sm"]))

        # Combo para seleccionar el grupo o investigador especifico
        self._target_var = ctk.StringVar(value="Todos")
        self._target_menu = combo(
            v_left,
            values=["Todos"],
            variable=self._target_var,
            command=self._on_target_changed,
            width=220,
        )
        # Se muestra solo si no es vista global
        self._target_menu.pack_forget()

        # Zona Derecha: Filtro de Ano compartido
        v_right = ctk.CTkFrame(inner, fg_color="transparent")
        v_right.pack(side="right")

        ctk.CTkLabel(
            v_right,
            text="Periodo:",
            font=font("heading"),
            text_color=COLORS["ink"],
        ).pack(side="left", padx=(0, SPACING["sm"]))

        self._year_seg = ctk.CTkSegmentedButton(
            v_right,
            values=["Todos", "Últimos 2", "Últimos 5", "Personalizado"],
            command=self._on_year_filter_changed,
            height=CONTROL_HEIGHT,
            corner_radius=RADIUS["control"],
            fg_color=COLORS["segment_bg"],
            selected_color=COLORS["accent"],
            selected_hover_color=COLORS["accent_hover"],
            unselected_color=COLORS["surface"],
            unselected_hover_color=COLORS["surface_alt"],
            text_color=COLORS["ink"],
            font=font("small"),
        )
        self._year_seg.set("Todos")
        self._year_seg.pack(side="left", padx=(0, SPACING["sm"]))

        # Inputs Desde/Hasta para rango personalizado
        self._range_frame = ctk.CTkFrame(v_right, fg_color="transparent")

        self._from_entry = entry(
            self._range_frame,
            placeholder_text="Desde",
            width=70,
        )
        self._from_entry.pack(side="left", padx=(0, SPACING["xs"]))
        self._from_entry.bind("<KeyRelease>", lambda e: self.refresh())

        ctk.CTkLabel(
            self._range_frame,
            text="a",
            font=font("small"),
            text_color=COLORS["muted"],
        ).pack(side="left", padx=(0, SPACING["xs"]))

        self._to_entry = entry(
            self._range_frame,
            placeholder_text="Hasta",
            width=70,
        )
        self._to_entry.pack(side="left")
        self._to_entry.bind("<KeyRelease>", lambda e: self.refresh())

    # -----------------------------------------------------------------------
    # 4. Tarjeta de Resumen Descriptivo (calculado con pandas)
    # -----------------------------------------------------------------------

    def _build_summary_card(self):
        self._summary_card = card(self)
        self._summary_card.pack(fill="x", padx=SPACING["lg"], pady=(0, SPACING["md"]))

        inner = ctk.CTkFrame(self._summary_card, fg_color="transparent")
        inner.pack(fill="x", padx=SPACING["md"], pady=SPACING["md"])

        # Encabezado del resumen
        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x", pady=(0, SPACING["sm"]))

        self._lbl_summary_title = ctk.CTkLabel(
            top,
            text="Resumen descriptivo de productividad cientifica",
            font=font("heading"),
            text_color=COLORS["ink"],
            anchor="w",
        )
        self._lbl_summary_title.pack(side="left")

        self._lbl_summary_sub = ctk.CTkLabel(
            top,
            text="(Distribucion de productos por entidad segun filtro activo)",
            font=font("small"),
            text_color=COLORS["muted"],
            anchor="w",
        )
        self._lbl_summary_sub.pack(side="left", padx=(SPACING["sm"], 0))

        # Rejilla de indicadores descriptivos: Total, Promedio, Mediana, Minimo, Maximo
        self._stat_grid = ctk.CTkFrame(inner, fg_color="transparent")
        self._stat_grid.pack(fill="x")
        self._stat_grid.grid_columnconfigure((0, 1, 2, 3, 4), weight=1, uniform="stats")

        self._metric_labels = {}
        metrics_meta = [
            ("total", "TOTAL PRODUCTOS", "0"),
            ("promedio", "PROMEDIO", "0.0"),
            ("mediana", "MEDIANA", "0.0"),
            ("min", "MINIMO", "0"),
            ("max", "MAXIMO", "0"),
        ]

        for idx, (key, title, default_val) in enumerate(metrics_meta):
            box = ctk.CTkFrame(
                self._stat_grid,
                corner_radius=RADIUS["card"],
                fg_color=COLORS["surface_alt"],
                border_width=1,
                border_color=COLORS["border"],
                height=68,
            )
            box.grid(row=0, column=idx, sticky="nsew",
                     padx=(0 if idx == 0 else SPACING["xs"],
                           0 if idx == 4 else SPACING["xs"]))
            box.pack_propagate(False)

            ctk.CTkLabel(
                box,
                text=title,
                font=font("small"),
                text_color=COLORS["muted"],
                anchor="center",
            ).pack(fill="x", pady=(8, 2))

            lbl_v = ctk.CTkLabel(
                box,
                text=default_val,
                font=font("heading"),
                text_color=COLORS["ink"],
                anchor="center",
            )
            lbl_v.pack(fill="x")
            self._metric_labels[key] = lbl_v

    # -----------------------------------------------------------------------
    # 5. Grid de Graficos Matplotlib (Responsive 3, 2 o 1 columnas)
    # -----------------------------------------------------------------------

    def _build_charts_grid(self):
        self._charts_container = ctk.CTkFrame(self, fg_color="transparent")
        self._charts_container.pack(fill="both", expand=True, padx=SPACING["lg"],
                                    pady=(0, SPACING["lg"]))

        self.card_chart1 = ChartCard(self._charts_container, title="Productos por año")
        self.card_chart2 = ChartCard(self._charts_container, title="Productos por gran categoría")
        self.card_chart3 = ChartCard(self._charts_container, title="Productos por tipo (top 10)")
        self.card_chart4 = ChartCard(self._charts_container, title="Histograma: productos por investigador")

        self._all_chart_cards = [
            self.card_chart1,
            self.card_chart2,
            self.card_chart3,
            self.card_chart4,
        ]

        self._empty_stats_msg = ctk.CTkLabel(
            self,
            text="No hay datos para las estadísticas con los filtros seleccionados.",
            font=font("body_bold"),
            text_color=COLORS["muted"],
            anchor="center",
        )

    def _on_container_resize(self, event):
        """Ajusta reactivamente el numero de columnas segun el ancho del frame garantizando igual alto."""
        width = event.width
        if width <= 10:
            return

        # 4 columnas si width >= 1500; 2 columnas si >= 750; 1 si es menor
        if width >= 1500:
            cols = 4
        elif width >= 750:
            cols = 2
        else:
            cols = 1

        if cols == self._current_cols:
            return

        self._current_cols = cols

        # Limpiar configuracion previa
        for i in range(len(self._all_chart_cards) + 2):
            self._charts_container.grid_columnconfigure(i, weight=0)
            self._charts_container.grid_rowconfigure(i, weight=0)

        for i in range(cols):
            self._charts_container.grid_columnconfigure(i, weight=1, uniform="chart_col")

        num_rows = (len(self._all_chart_cards) + cols - 1) // cols
        for r in range(num_rows):
            self._charts_container.grid_rowconfigure(r, weight=1, uniform="chart_row")

        pad = SPACING["sm"]
        for idx, card_w in enumerate(self._all_chart_cards):
            r = idx // cols
            c = idx % cols
            card_w.grid(
                row=r,
                column=c,
                sticky="nsew",
                padx=pad,
                pady=pad,
            )

    # -----------------------------------------------------------------------
    # Manejadores de eventos de filtros
    # -----------------------------------------------------------------------

    def _on_view_changed(self, value: str):
        self._view_mode = value
        app = self.get_app()
        if not app:
            return

        if value == "Global":
            self._target_menu.pack_forget()
            self._selected_target_id = None
        elif value == "Por grupo":
            # Cargar grupos disponibles en el combo
            grupos = list(_iter_grupos(app))
            self._target_choices = {"Todos los grupos": ""}
            for g in grupos:
                gid = _group_id(g)
                gcode = str(getattr(g, "codigo_gruplac", "") or getattr(g, "nombre", f"Grupo {gid}"))
                lbl = f"{gid} - {gcode[:24]}"
                self._target_choices[lbl] = gid

            vals = list(self._target_choices.keys())
            self._target_menu.configure(values=vals)
            self._target_var.set(vals[0])
            self._selected_target_id = None
            self._target_menu.pack(side="left", padx=(0, SPACING["sm"]))
        elif value == "Por investigador":
            invs = list(_iter_investigadores(app))
            self._target_choices = {"Todos los investigadores": ""}
            for i in invs:
                iid = _investigator_id(i)
                nombre = str(getattr(i, "nombres", "") or getattr(i, "nombre", "")).strip()
                apellido = str(getattr(i, "apellidos", "")).strip()
                inom = f"{nombre} {apellido}".strip() or f"Investigador {iid}"
                lbl = f"{iid} - {inom[:24]}"
                self._target_choices[lbl] = iid

            vals = list(self._target_choices.keys())
            self._target_menu.configure(values=vals)
            self._target_var.set(vals[0])
            self._selected_target_id = None
            self._target_menu.pack(side="left", padx=(0, SPACING["sm"]))

        self.refresh()

    def _on_target_changed(self, choice: str):
        self._selected_target_id = self._target_choices.get(choice, "") or None
        self.refresh()

    def _on_year_filter_changed(self, value: str):
        if value == "Personalizado":
            self._range_frame.pack(side="left")
            self._from_entry.focus_set()
        else:
            self._range_frame.pack_forget()
        self.refresh()

    # -----------------------------------------------------------------------
    # Resolucion de instancia App
    # -----------------------------------------------------------------------

    def get_app(self):
        if self._app_ref is not None:
            return self._app_ref
        curr = self
        while curr is not None:
            if hasattr(curr, "grupo_crud"):
                self._app_ref = curr
                return curr
            curr = getattr(curr, "master", None)
        return None

    # -----------------------------------------------------------------------
    # Logica de refresco y calculo analitico
    # -----------------------------------------------------------------------

    def refresh(self):
        """Calcula de forma reactiva las metricas y actualiza tarjetas y graficas."""
        app = self.get_app()
        if not app:
            return

        # Cierra las figuras anteriores con plt.close(fig) al redibujar
        for card in getattr(self, "_all_chart_cards", []):
            if hasattr(card, "chart") and hasattr(card.chart, "fig") and card.chart.fig is not None:
                try:
                    plt.close(card.chart.fig)
                except Exception:
                    pass
        try:
            plt.close("all")
        except Exception:
            pass

        all_grupos = list(_iter_grupos(app))
        all_investigadores = list(_iter_investigadores(app))
        all_productos = list(_iter_productos(app))

        # 1. Filtrado de productos y entidades segun periodo y vista seleccionada
        filtered_prods = self._filter_products(all_productos)
        scoped_grupos, scoped_investigadores = self._filter_entities(
            all_grupos,
            all_investigadores,
            filtered_prods,
        )

        # 2. Actualizar Tarjetas KPI con el mismo alcance de filtros
        tot_g = len(scoped_grupos)
        act_g = sum(1 for g in scoped_grupos if _is_active(g))
        tot_i = len(scoped_investigadores)
        act_i = sum(1 for i in scoped_investigadores if _is_active(i))
        tot_p = len(filtered_prods)
        act_p = sum(1 for p in filtered_prods if _is_validated(p))

        self.card_grupos.set_value(
            str(tot_g),
            variation=f"{act_g} activos" if tot_g > 0 else "Sin registros",
        )
        self.card_investigadores.set_value(
            str(tot_i),
            variation=f"{act_i} activos" if tot_i > 0 else "Sin registros",
        )
        self.card_productos.set_value(
            str(tot_p),
            variation=f"{act_p} validados" if tot_p > 0 else "Sin registros",
        )

        # 3. Resumen Descriptivo con pandas
        self._update_descriptive_summary(scoped_grupos, scoped_investigadores, filtered_prods)

        # 4. Grafico 1: Productos por año (etiquetas cada 2 o 5 años)
        self._plot_chart1_years(filtered_prods)

        # 5. Grafico 2: Productos por gran categoría (GNC, DTI, ASC, FRH)
        self._plot_chart2_gran_categoria(filtered_prods)

        # 6. Grafico 3: Productos por tipo (top 10 barras horizontales)
        self._plot_chart3_tipo(filtered_prods)

        # 7. Grafico 4: Histograma real con ax.hist de productos por investigador
        self._plot_chart4_histogram_investigadores(scoped_investigadores, filtered_prods)

        self._toggle_empty_message(bool(filtered_prods))

    # -----------------------------------------------------------------------
    # Metodos auxiliares de calculo
    # -----------------------------------------------------------------------

    def _filter_products(self, prods: List[Any]) -> List[Any]:
        """Aplica los filtros de ano y vista activa a la lista de productos."""
        cur_year = datetime.datetime.now().year
        year_mode = self._year_seg.get()

        res = []
        for p in prods:
            if not _is_validated(p):
                continue

            # Filtro por vista (Grupo o Investigador)
            if self._view_mode == "Por grupo" and self._selected_target_id:
                if _product_group_id(p) != str(self._selected_target_id):
                    continue
            elif self._view_mode == "Por investigador" and self._selected_target_id:
                if _product_investigator_id(p) != str(self._selected_target_id):
                    continue

            # Filtro por ano
            pyear = _product_year(p)

            if year_mode == "Últimos 2":
                if pyear is None or pyear < (cur_year - 2):
                    continue
            elif year_mode == "Últimos 5":
                if pyear is None or pyear < (cur_year - 5):
                    continue
            elif year_mode == "Personalizado":
                f_txt = self._from_entry.get().strip()
                t_txt = self._to_entry.get().strip()
                if (f_txt or t_txt) and pyear is None:
                    continue
                try:
                    if f_txt and pyear < int(f_txt):
                        continue
                except ValueError:
                    pass
                try:
                    if t_txt and pyear > int(t_txt):
                        continue
                except ValueError:
                    pass

            res.append(p)
        return res

    def _filter_entities(self, grupos, investigadores, productos_filtrados):
        """Devuelve grupos e investigadores afectados por vista, entidad y periodo."""
        grupos_res = list(grupos)
        investigadores_res = list(investigadores)

        if self._view_mode == "Por grupo" and self._selected_target_id:
            gid = str(self._selected_target_id)
            grupos_res = [g for g in grupos_res if _group_id(g) == gid]
            investigadores_res = [i for i in investigadores_res if _investigator_group_id(i) == gid]
        elif self._view_mode == "Por investigador" and self._selected_target_id:
            iid = str(self._selected_target_id)
            investigadores_res = [i for i in investigadores_res if _investigator_id(i) == iid]
            group_ids = {_investigator_group_id(i) for i in investigadores_res if _investigator_group_id(i)}
            group_ids.update(_product_group_id(p) for p in productos_filtrados if _product_group_id(p))
            grupos_res = [g for g in grupos_res if _group_id(g) in group_ids]

        if self._year_seg.get() != "Todos":
            product_group_ids = {_product_group_id(p) for p in productos_filtrados if _product_group_id(p)}
            product_inv_ids = {_product_investigator_id(p) for p in productos_filtrados if _product_investigator_id(p)}
            grupos_res = [g for g in grupos_res if _group_id(g) in product_group_ids]
            investigadores_res = [i for i in investigadores_res if _investigator_id(i) in product_inv_ids]

        return grupos_res, investigadores_res

    def _toggle_empty_message(self, has_data: bool):
        if has_data:
            self._empty_stats_msg.pack_forget()
        else:
            self._empty_stats_msg.pack(fill="x", padx=SPACING["lg"], pady=(0, SPACING["md"]))

    def _update_descriptive_summary(self, grupos, investigadores, productos):
        """Calcula metricas estadisticas con pandas."""
        total_prods = len(productos)
        self._metric_labels["total"].configure(text=str(total_prods))

        if total_prods == 0:
            self._metric_labels["promedio"].configure(text="0.0")
            self._metric_labels["mediana"].configure(text="0.0")
            self._metric_labels["min"].configure(text="0")
            self._metric_labels["max"].configure(text="0")
            return

        # Calcular distribucion de productos por entidad (agrupacion con pandas)
        # Segun la vista: si es "Por investigador", agrupamos por tipo; si no, por entidad
        if self._view_mode == "Por investigador":
            tipos = [str(getattr(p, "tipo", "") or getattr(p, "type", "Sin tipo")) for p in productos]
            s = pd.Series(tipos).value_counts()
        else:
            inv_keys = [
                str(
                    getattr(p, "investigador_id", None)
                    or getattr(p, "investigador_cedula", None)
                    or getattr(p, "grupo_id", "General")
                )
                for p in productos
            ]
            s = pd.Series(inv_keys).value_counts()

        if not s.empty:
            mean_v = float(s.mean())
            median_v = float(s.median())
            min_v = int(s.min())
            max_v = int(s.max())

            self._metric_labels["promedio"].configure(text=f"{mean_v:.2f}")
            self._metric_labels["mediana"].configure(text=f"{median_v:.1f}")
            self._metric_labels["min"].configure(text=str(min_v))
            self._metric_labels["max"].configure(text=str(max_v))
        else:
            self._metric_labels["promedio"].configure(text="0.0")
            self._metric_labels["mediana"].configure(text="0.0")
            self._metric_labels["min"].configure(text="0")
            self._metric_labels["max"].configure(text="0")

    def _plot_chart1_years(self, prods):
        years_cnt = Counter()
        for p in prods:
            y = _product_year(p)
            if y is None or y <= 1900:
                continue
            years_cnt[y] += 1

        print(f"[DEBUG _plot_chart1_years] Recibidos: {len(prods)} productos | Campo leído: 'anio' | Años distintos: {len(years_cnt)} | Total productos graficados: {sum(years_cnt.values())}")

        if years_cnt:
            sorted_y = sorted(years_cnt.keys())
            span = sorted_y[-1] - sorted_y[0] if len(sorted_y) > 1 else 0
            # Muestra una etiqueta cada 2 o 5 años (o 1 si hay pocos) para legibilidad en eje X
            step = 5 if span >= 15 else (2 if span >= 6 else 1)

            display_labels = []
            for idx, y in enumerate(sorted_y):
                if y % step == 0 or idx == 0 or idx == len(sorted_y) - 1:
                    display_labels.append(str(y))
                else:
                    display_labels.append("")

            self.card_chart1.chart.plot_bar(
                [str(y) for y in sorted_y],
                [years_cnt[y] for y in sorted_y],
                title="Productos por año",
                color=CHART_COLORS[0],
                display_labels=display_labels,
            )
        else:
            self.card_chart1.chart.clear()

    def _plot_chart2_gran_categoria(self, prods):
        """Grafica productos en las 4 grandes categorías de MinCiencias (GNC, DTI, ASC, FRH)."""
        categories = ["GNC", "DTI", "ASC", "FRH"]
        cat_cnt = {c: 0 for c in categories}

        for p in prods:
            gc = _get_field(p, "gran_categoria", "gran_cat", "categoria_producto", "categoria")
            tipo = _get_field(p, "tipo", "type", default="")
            code = _normalize_gran_categoria(gc, tipo)
            if code in cat_cnt:
                cat_cnt[code] += 1

        print(f"[DEBUG _plot_chart2_gran_categoria] Recibidos: {len(prods)} productos | Campo leído: 'gran_categoria' | Conteo: {cat_cnt}")

        lbls = categories
        vals = [cat_cnt[c] for c in lbls]
        if any(v > 0 for v in vals):
            self.card_chart2.chart.plot_bar(
                lbls,
                vals,
                title="Productos por gran categoría",
                color=CHART_COLORS[1],
            )
        else:
            self.card_chart2.chart.clear()

    def _plot_chart3_tipo(self, prods):
        """Grafica productos por tipo (top 10 barras horizontales)."""
        tipo_cnt = Counter()
        for p in prods:
            t = _get_field(p, "tipo", "type")
            if t:
                clean_t = str(t).strip()
                if clean_t and clean_t.lower() not in ("", "sin tipo", "none", "null"):
                    tipo_cnt[clean_t] += 1

        top10 = tipo_cnt.most_common(10)
        print(f"[DEBUG _plot_chart3_tipo] Recibidos: {len(prods)} productos | Campo leído: 'tipo' | Tipos distintos: {len(tipo_cnt)} | Top 10: {top10}")

        if top10:
            lbls = [item[0] for item in top10]
            vals = [item[1] for item in top10]
            self.card_chart3.chart.plot_barh(
                lbls,
                vals,
                title="Productos por tipo (top 10)",
                color=CHART_COLORS[2],
                max_items=10,
            )
        else:
            self.card_chart3.chart.clear()

    # Alias de compatibilidad
    _plot_chart3_subcategorias = _plot_chart3_tipo

    def _plot_chart4_histogram_investigadores(self, scoped_investigadores, prods):
        """Histograma real con ax.hist de productos por investigador respetando Vista y Periodo."""
        inv_cnt = Counter()
        for p in prods:
            iid = _product_investigator_id(p) or "Sin investigador"
            inv_cnt[str(iid)] += 1

        # Respetar el alcance de entidades según Vista y Periodo
        if self._view_mode == "Por investigador" and self._selected_target_id:
            target_id = str(self._selected_target_id)
            values = [inv_cnt.get(target_id, 0)]
        elif scoped_investigadores:
            values = [inv_cnt.get(str(_investigator_id(inv)), 0) for inv in scoped_investigadores]
        else:
            values = list(inv_cnt.values())

        print(f"[DEBUG _plot_chart4_histogram_investigadores] Investigadores evaluados: {len(values)} | Min: {min(values) if values else 0} | Max: {max(values) if values else 0} | Total productos: {sum(values)}")

        if values:
            bins = min(8, max(1, len(set(values))))
            self.card_chart4.chart.plot_histogram(
                values,
                bins=bins,
                title="Histograma: productos por investigador",
                color=CHART_COLORS[3 % len(CHART_COLORS)],
            )
        else:
            self.card_chart4.chart.clear()

    # Alias de compatibilidad
    _plot_chart5_histogram_investigadores = lambda self, prods: self._plot_chart4_histogram_investigadores(None, prods)

    # -----------------------------------------------------------------------
    # 7. Exportacion de graficas a archivo PNG
    # -----------------------------------------------------------------------

    def _export_png(self):
        """Permite guardar un mosaico de las visualizaciones activas en formato PNG."""
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("Imagen PNG", "*.png"), ("Todos los archivos", "*.*")],
            title="Exportar graficas a PNG",
            initialfile="PEAi_Estadisticas.png",
        )
        if not path:
            return

        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_agg import FigureCanvasAgg

            export_fig = Figure(figsize=(12, 8.5), dpi=200, facecolor=COLORS["surface"])
            axes = export_fig.subplots(2, 2)

            app = self.get_app()
            prods = self._filter_products(list(_iter_productos(app))) if app else []

            # Grafico 1: Barras verticales de anos
            ax1 = axes[0, 0]
            ax1.set_facecolor(COLORS["surface"])
            years_cnt = Counter()
            for p in prods:
                y = _product_year(p)
                if y is not None and y > 1900:
                    years_cnt[y] += 1
            if years_cnt:
                sy = sorted(years_cnt.keys())
                span = sy[-1] - sy[0] if len(sy) > 1 else 0
                step = 5 if span >= 15 else (2 if span >= 6 else 1)
                labels = [str(y) if (y % step == 0 or idx == 0 or idx == len(sy) - 1) else "" for idx, y in enumerate(sy)]
                ax1.bar(range(len(sy)), [years_cnt[y] for y in sy], color=CHART_COLORS[0])
                ax1.set_xticks(range(len(sy)))
                ax1.set_xticklabels(labels, rotation=25 if len([l for l in labels if l]) > 6 else 0)
                ax1.set_title("Productos por año", fontweight="bold", fontsize=11, loc="left")
            else:
                ax1.axis("off")
                ax1.text(0.5, 0.5, "Sin datos para graficar", ha="center", va="center")

            # Grafico 2: Gran categoría (4 barras)
            ax2 = axes[0, 1]
            ax2.set_facecolor(COLORS["surface"])
            gc_order = ["GNC", "DTI", "ASC", "FRH"]
            gc_cnt = {c: 0 for c in gc_order}
            for p in prods:
                gc = _get_field(p, "gran_categoria", "gran_cat", "categoria_producto", "categoria")
                tipo = _get_field(p, "tipo", "type", default="")
                code = _normalize_gran_categoria(gc, tipo)
                if code in gc_cnt:
                    gc_cnt[code] += 1
            if any(v > 0 for v in gc_cnt.values()):
                ax2.bar(gc_order, [gc_cnt[c] for c in gc_order], color=CHART_COLORS[1])
                ax2.set_title("Productos por gran categoría", fontweight="bold", fontsize=11, loc="left")
            else:
                ax2.axis("off")
                ax2.text(0.5, 0.5, "Sin datos para graficar", ha="center", va="center")

            # Grafico 3: Productos por tipo (top 10)
            ax3 = axes[1, 0]
            ax3.set_facecolor(COLORS["surface"])
            tipo_cnt = Counter()
            for p in prods:
                t = _get_field(p, "tipo", "type")
                if t:
                    clean_t = str(t).strip()
                    if clean_t and clean_t.lower() not in ("", "sin tipo", "none", "null"):
                        tipo_cnt[clean_t] += 1
            if tipo_cnt:
                top10 = tipo_cnt.most_common(10)
                pairs = list(reversed(top10))
                ax3.barh([p[0][:30] for p in pairs], [p[1] for p in pairs], color=CHART_COLORS[2])
                ax3.set_title("Productos por tipo (top 10)", fontweight="bold", fontsize=11, loc="left")
            else:
                ax3.axis("off")
                ax3.text(0.5, 0.5, "Sin datos para graficar", ha="center", va="center")

            # Grafico 4: Histograma real de productos por investigador
            ax4 = axes[1, 1]
            ax4.set_facecolor(COLORS["surface"])
            inv_cnt = Counter()
            for p in prods:
                iid = _product_investigator_id(p) or "Sin investigador"
                inv_cnt[str(iid)] += 1
            hist_vals = list(inv_cnt.values())
            if hist_vals:
                bins = min(8, max(1, len(set(hist_vals))))
                ax4.hist(
                    hist_vals,
                    bins=bins,
                    color=CHART_COLORS[3 % len(CHART_COLORS)],
                    edgecolor=COLORS["surface"],
                    linewidth=1.2,
                    rwidth=0.88,
                )
                ax4.set_title("Histograma: productos por investigador", fontweight="bold", fontsize=11, loc="left")
            else:
                ax4.axis("off")
                ax4.text(0.5, 0.5, "Sin datos para graficar", ha="center", va="center")

            for ax in (ax1, ax2, ax3, ax4):
                if ax.axison:
                    ax.spines["top"].set_visible(False)
                    ax.spines["right"].set_visible(False)
                    ax.tick_params(labelsize=8)

            export_fig.tight_layout()
            canvas_agg = FigureCanvasAgg(export_fig)
            canvas_agg.print_png(path)
            plt.close(export_fig)

            messagebox.showinfo("Exportacion exitosa", f"Graficas exportadas exitosamente en:\n{path}")
        except Exception as exc:
            messagebox.showerror("Error al exportar", f"No se pudo guardar la imagen: {exc}")

