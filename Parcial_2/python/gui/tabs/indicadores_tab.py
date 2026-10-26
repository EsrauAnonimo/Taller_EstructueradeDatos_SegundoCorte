# -*- coding: utf-8 -*-
"""Pestaña de Indicador de Producción Científica (Modelo MinCiencias - Parcial 2)."""

from typing import Optional, List, Dict, Any
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk

from gui.styles import (
    COLORS,
    SPACING,
    RADIUS,
    font,
    button,
)
from gui.widgets.stat_card import StatCard
import indicadores


class IndicadoresTab(ctk.CTkFrame):
    """Pestaña interactiva para calcular y visualizar el Indicador de Producción Científica
    de Grupos e Investigadores según el modelo oficial de MinCiencias.
    """

    def __init__(self, master, app=None):
        super().__init__(master, fg_color="transparent")
        self._app_ref = app
        self.pack(fill="both", expand=True)

        self._grupos_cache = []
        self._investigadores_cache = []
        self._selected_mode = "Grupo"  # "Grupo" o "Investigador"

        # Grid principal
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 1. Encabezado institucional
        self._build_header()

        # 2. Barra de control y selección
        self._build_controls()

        # 3. Contenedor de resultados (KPIs + Desglose + Tabla de productos)
        self._build_results_area()

    def _build_header(self):
        """Construye el encabezado de la pestaña."""
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=SPACING["lg"],
            pady=(SPACING["sm"], SPACING["xs"]),
        )

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Indicador de Producción Científica",
            font=font("heading"),
            text_color=COLORS["ink"],
            anchor="w",
        )
        self.title_label.pack(side="left", anchor="w")

        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text=" · Modelo MinCiencias Colombia (Fórmula: 3.7*Nc_Top + 2.3*Nc_A + 0.4*Nc_B + 1.5*AP + 0.5*DPC + 1*Fr_A + 0.2*Fr_B + 0.1*Cohe + 0.3*Coop)",
            font=font("small"),
            text_color=COLORS["muted"],
            anchor="w",
        )
        self.subtitle_label.pack(side="left", anchor="w", padx=(6, 0))

    def _build_controls(self):
        """Construye la barra de selección de Grupo / Investigador."""
        self.controls_card = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["card"],
            border_width=1,
            border_color=COLORS["border"],
        )
        self.controls_card.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=SPACING["lg"],
            pady=(0, SPACING["sm"]),
        )

        ctrl_inner = ctk.CTkFrame(self.controls_card, fg_color="transparent")
        ctrl_inner.pack(fill="x", padx=SPACING["md"], pady=SPACING["sm"])

        # Selector de Modo: Grupo o Investigador
        lbl_tipo = ctk.CTkLabel(
            ctrl_inner,
            text="Calcular para:",
            font=font("body_bold"),
            text_color=COLORS["ink"],
        )
        lbl_tipo.pack(side="left", padx=(0, 10))

        self.seg_mode = ctk.CTkSegmentedButton(
            ctrl_inner,
            values=["Grupo", "Investigador"],
            command=self._on_mode_change,
            font=font("body"),
            selected_color=COLORS["primary"],
            selected_hover_color=COLORS["primary_hover"],
        )
        self.seg_mode.set("Grupo")
        self.seg_mode.pack(side="left", padx=(0, 20))

        # Selector desplegable (ComboBox)
        self.lbl_target = ctk.CTkLabel(
            ctrl_inner,
            text="Seleccionar Grupo:",
            font=font("body_bold"),
            text_color=COLORS["ink"],
        )
        self.lbl_target.pack(side="left", padx=(0, 10))

        self.combo_target = ctk.CTkComboBox(
            ctrl_inner,
            width=360,
            values=["Cargando..."],
            font=font("body"),
            dropdown_font=font("body"),
            corner_radius=RADIUS["control"],
            border_color=COLORS["border"],
        )
        self.combo_target.pack(side="left", padx=(0, 15))

        # Botón Calcular
        self.btn_calc = ctk.CTkButton(
            ctrl_inner,
            text="  Calcular Indicador",
            font=font("body_bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            corner_radius=RADIUS["control"],
            height=36,
            command=self.calcular,
        )
        self.btn_calc.pack(side="left", padx=(0, 10))

        # Botón Actualizar listas
        self.btn_refresh = ctk.CTkButton(
            ctrl_inner,
            text="⟳ Actualizar",
            width=90,
            font=font("small"),
            fg_color=COLORS["surface_alt"],
            text_color=COLORS["ink"],
            hover_color=COLORS["border"],
            corner_radius=RADIUS["control"],
            height=36,
            command=self.refresh,
        )
        self.btn_refresh.pack(side="left")

        # Fila 2 de controles: Filtro por Año (Últimos N años y Rango desde-hasta)
        filter_row = ctk.CTkFrame(self.controls_card, fg_color="transparent")
        filter_row.pack(fill="x", padx=SPACING["md"], pady=(0, SPACING["sm"]))

        lbl_filtro = ctk.CTkLabel(
            filter_row,
            text="Filtro por año:",
            font=font("body_bold"),
            text_color=COLORS["ink"],
        )
        lbl_filtro.pack(side="left", padx=(0, 10))

        self.seg_year = ctk.CTkSegmentedButton(
            filter_row,
            values=["Todos", "Últimos 3 años", "Últimos 5 años", "Rango"],
            command=self._on_year_filter_mode_change,
            font=font("body"),
            selected_color=COLORS["primary"],
            selected_hover_color=COLORS["primary_hover"],
        )
        self.seg_year.set("Todos")
        self.seg_year.pack(side="left", padx=(0, 15))

        self.frame_range = ctk.CTkFrame(filter_row, fg_color="transparent")
        self.frame_range.pack(side="left")

        lbl_d = ctk.CTkLabel(self.frame_range, text="Desde:", font=font("small"), text_color=COLORS["ink"])
        lbl_d.pack(side="left", padx=(0, 4))
        self.entry_desde = ctk.CTkEntry(self.frame_range, width=70, font=font("small"), corner_radius=RADIUS["control"])
        self.entry_desde.insert(0, "2020")
        self.entry_desde.pack(side="left", padx=(0, 10))

        lbl_h = ctk.CTkLabel(self.frame_range, text="Hasta:", font=font("small"), text_color=COLORS["ink"])
        lbl_h.pack(side="left", padx=(0, 4))
        self.entry_hasta = ctk.CTkEntry(self.frame_range, width=70, font=font("small"), corner_radius=RADIUS["control"])
        self.entry_hasta.insert(0, "2026")
        self.entry_hasta.pack(side="left")

    def _on_year_filter_mode_change(self, mode: str):
        """Maneja el cambio de modo en el filtro por año."""
        pass

    def _build_results_area(self):
        """Construye el área inferior con scroll, tarjetas KPI, desglose y lista de productos."""
        self.scroll_results = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
        )
        self.scroll_results.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=SPACING["lg"],
            pady=(0, SPACING["md"]),
        )

        # 3.1 Fila de tarjetas KPI
        self.kpi_frame = ctk.CTkFrame(self.scroll_results, fg_color="transparent")
        self.kpi_frame.pack(fill="x", pady=(0, SPACING["md"]))

        self.card_total = StatCard(
            self.kpi_frame,
            title="INDICADOR TOTAL",
            value="0.0",
            note="Puntaje de producción MinCiencias",
            icon="🏆",
            accent_color=COLORS["primary"],
        )
        self.card_total.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.card_prods = StatCard(
            self.kpi_frame,
            title="TOTAL PRODUCTOS",
            value="0",
            note="0 validados para medición",
            icon="📦",
            accent_color=COLORS["success"],
        )
        self.card_prods.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.card_top = StatCard(
            self.kpi_frame,
            title="NUEVO CONOCIMIENTO TOP / A",
            value="0",
            note="Nc_Top (A1) + Nc_A (A2/A)",
            icon="⭐",
            accent_color="#F59E0B",
        )
        self.card_top.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.card_entidad = StatCard(
            self.kpi_frame,
            title="ENTIDAD EVALUADA",
            value="—",
            note="Seleccione una entidad para calcular",
            icon="🎯",
            accent_color="#8B5CF6",
        )
        self.card_entidad.pack(side="left", fill="both", expand=True)

        # 3.2 Fila con Desglose de Fórmula y Detalle de Productos
        content_split = ctk.CTkFrame(self.scroll_results, fg_color="transparent")
        content_split.pack(fill="both", expand=True)

        # Panel izquierdo: Desglose de la Fórmula MinCiencias
        self.breakdown_frame = ctk.CTkFrame(
            content_split,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["card"],
            border_width=1,
            border_color=COLORS["border"],
        )
        self.breakdown_frame.pack(side="left", fill="both", expand=False, padx=(0, 10), ipadx=10, ipady=10)

        lbl_bd_title = ctk.CTkLabel(
            self.breakdown_frame,
            text="Desglose por Variable de la Fórmula",
            font=font("subheading"),
            text_color=COLORS["ink"],
        )
        lbl_bd_title.pack(anchor="w", padx=12, pady=(10, 6))

        # Tabla Treeview para el desglose de variables
        cols = ("var", "desc", "coef", "count", "subtotal")
        self.tree_breakdown = ttk.Treeview(
            self.breakdown_frame,
            columns=cols,
            show="headings",
            height=10,
        )
        self.tree_breakdown.heading("var", text="Variable")
        self.tree_breakdown.heading("desc", text="Componente MinCiencias")
        self.tree_breakdown.heading("coef", text="Peso")
        self.tree_breakdown.heading("count", text="Conteo / Valor")
        self.tree_breakdown.heading("subtotal", text="Subtotal")

        self.tree_breakdown.column("var", width=70, anchor="center")
        self.tree_breakdown.column("desc", width=220, anchor="w")
        self.tree_breakdown.column("coef", width=55, anchor="center")
        self.tree_breakdown.column("count", width=95, anchor="center")
        self.tree_breakdown.column("subtotal", width=75, anchor="e")

        self.tree_breakdown.pack(fill="both", expand=True, padx=12, pady=6)

        # Panel derecho: Productos asociados con peso relativo y puntaje
        self.prods_frame = ctk.CTkFrame(
            content_split,
            fg_color=COLORS["surface"],
            corner_radius=RADIUS["card"],
            border_width=1,
            border_color=COLORS["border"],
        )
        self.prods_frame.pack(side="left", fill="both", expand=True, ipadx=10, ipady=10)

        lbl_prods_title = ctk.CTkLabel(
            self.prods_frame,
            text="Productos Evaluados (Peso Relativo y Puntaje)",
            font=font("subheading"),
            text_color=COLORS["ink"],
        )
        lbl_prods_title.pack(anchor="w", padx=12, pady=(10, 6))

        prod_cols = ("id", "titulo", "tipo", "categoria", "peso", "puntaje", "validado")
        self.tree_prods = ttk.Treeview(
            self.prods_frame,
            columns=prod_cols,
            show="headings",
            height=10,
        )
        self.tree_prods.heading("id", text="ID")
        self.tree_prods.heading("titulo", text="Título del Producto")
        self.tree_prods.heading("tipo", text="Tipo / Subcategoría")
        self.tree_prods.heading("categoria", text="Categoría")
        self.tree_prods.heading("peso", text="Peso Rel.")
        self.tree_prods.heading("puntaje", text="Puntaje")
        self.tree_prods.heading("validado", text="Validado")

        self.tree_prods.column("id", width=65, anchor="center")
        self.tree_prods.column("titulo", width=240, anchor="w")
        self.tree_prods.column("tipo", width=140, anchor="w")
        self.tree_prods.column("categoria", width=100, anchor="center")
        self.tree_prods.column("peso", width=65, anchor="center")
        self.tree_prods.column("puntaje", width=65, anchor="center")
        self.tree_prods.column("validado", width=70, anchor="center")

        prod_scroll = ttk.Scrollbar(self.prods_frame, orient="vertical", command=self.tree_prods.yview)
        self.tree_prods.configure(yscrollcommand=prod_scroll.set)

        self.tree_prods.pack(side="left", fill="both", expand=True, padx=(12, 0), pady=6)
        prod_scroll.pack(side="right", fill="y", padx=(0, 12), pady=6)

    def _on_mode_change(self, mode: str):
        """Manejador al alternar entre Grupo e Investigador."""
        self._selected_mode = mode
        if mode == "Grupo":
            self.lbl_target.configure(text="Seleccionar Grupo:")
        else:
            self.lbl_target.configure(text="Seleccionar Investigador:")
        self._populate_combo()

    def refresh(self):
        """Recarga los datos de grupos e investigadores desde la multilista."""
        self._load_caches()
        self._populate_combo()

    def _load_caches(self):
        """Carga las listas de grupos e investigadores disponibles."""
        self._grupos_cache.clear()
        self._investigadores_cache.clear()

        app = self._app_ref
        if not app or not hasattr(app, "multilista"):
            return

        ml = app.multilista
        curr_g = ml.head_group
        while curr_g is not None:
            if curr_g.active:
                gid = getattr(curr_g.data, "id", None)
                gnom = getattr(curr_g.data, "nombre", f"Grupo {gid}")
                self._grupos_cache.append((gid, f"[{gid}] {gnom}"))

                curr_i = curr_g.sublist
                while curr_i is not None:
                    if curr_i.active:
                        iid = getattr(curr_i.data, "id", None) or getattr(curr_i.data, "cedula", "")
                        inom = getattr(curr_i.data, "nombre", f"Investigador {iid}")
                        self._investigadores_cache.append((iid, f"[{iid}] {inom} ({gnom})"))
                    curr_i = curr_i.next
            curr_g = curr_g.next

    def _populate_combo(self):
        """Llena el combobox según el modo seleccionado."""
        if not self._grupos_cache and not self._investigadores_cache:
            self._load_caches()

        if self._selected_mode == "Grupo":
            items = [lbl for _, lbl in self._grupos_cache]
            if not items:
                items = ["No hay grupos registrados"]
            self.combo_target.configure(values=items)
            self.combo_target.set(items[0])
        else:
            items = [lbl for _, lbl in self._investigadores_cache]
            if not items:
                items = ["No hay investigadores registrados"]
            self.combo_target.configure(values=items)
            self.combo_target.set(items[0])

    def calcular(self):
        """Calcula el indicador según la entidad seleccionada en el ComboBox."""
        selected_text = self.combo_target.get()
        if not selected_text or "No hay" in selected_text or "Cargando" in selected_text:
            messagebox.showwarning("Atención", "Por favor seleccione una entidad válida para calcular el indicador.")
            return

        app = self._app_ref
        if not app or not hasattr(app, "multilista"):
            messagebox.showerror("Error", "No se encontró la estructura de datos activa.")
            return

        # Extraer el ID dentro de los corchetes [ID]
        target_id = None
        if "[" in selected_text and "]" in selected_text:
            target_id = selected_text.split("[")[1].split("]")[0].strip()

        if not target_id:
            messagebox.showerror("Error", "No se pudo identificar el ID de la entidad seleccionada.")
            return

        # Intentar convertir a int si es numérico
        if target_id.isdigit():
            target_id = int(target_id)

        # Determinar filtro por año
        filtro_modo = self.seg_year.get()
        anio_min = None
        anio_max = None
        current_year = 2026
        filtro_desc = "Todos los años"

        if filtro_modo == "Últimos 3 años":
            anio_min = current_year - 3 + 1
            anio_max = current_year
            filtro_desc = f"{anio_min} - {anio_max}"
        elif filtro_modo == "Últimos 5 años":
            anio_min = current_year - 5 + 1
            anio_max = current_year
            filtro_desc = f"{anio_min} - {anio_max}"
        elif filtro_modo == "Rango":
            try:
                d_str = self.entry_desde.get().strip()
                h_str = self.entry_hasta.get().strip()
                if d_str:
                    anio_min = int(d_str)
                if h_str:
                    anio_max = int(h_str)
                if anio_min is not None and anio_max is not None and anio_min > anio_max:
                    anio_min, anio_max = anio_max, anio_min
                filtro_desc = f"{anio_min or 'inicio'} - {anio_max or 'fin'}"
            except ValueError:
                messagebox.showwarning("Atención", "Los años del rango deben ser números enteros.")
                return

        # Ejecutar cálculo
        if self._selected_mode == "Grupo":
            res = indicadores.calcular_indicador_grupo(app.multilista, target_id, anio_min=anio_min, anio_max=anio_max)
            productos = app.multilista.get_productos_by_grupo(target_id)
        else:
            res = indicadores.calcular_indicador_investigador(app.multilista, target_id, anio_min=anio_min, anio_max=anio_max)
            productos = app.multilista.get_productos_by_investigador(target_id)

        # Actualizar KPIs
        self.card_total.update_value(f"{res['indicador']:.2f}")
        self.card_prods.update_value(
            str(res["total_productos"]),
            note=f"{res['total_validados']} validados · Filtro: {filtro_desc}",
        )
        top_a_count = res["counts"].get("Nc_Top", 0) + res["counts"].get("Nc_A", 0)
        self.card_top.update_value(str(top_a_count))

        entidad_nombre = res.get("entidad_nombre", str(target_id))
        if len(entidad_nombre) > 22:
            entidad_nombre = entidad_nombre[:20] + "..."
        self.card_entidad.update_value(entidad_nombre, note=f"Tipo: {res['entidad_tipo']}")

        # Actualizar tabla de desglose
        for item in self.tree_breakdown.get_children():
            self.tree_breakdown.delete(item)

        for var, coef in res["coefficients"].items():
            desc = res["descriptions"].get(var, var)
            val = res["counts"].get(var, 0)
            sub = res["subtotals"].get(var, 0.0)
            val_str = f"{val:.2f}" if isinstance(val, float) else str(val)
            self.tree_breakdown.insert("", "end", values=(var, desc, f"{coef}", val_str, f"{sub:.2f}"))

        # Actualizar tabla de productos detallada filtrada por año
        for item in self.tree_prods.get_children():
            self.tree_prods.delete(item)

        for p in productos:
            if not indicadores._filtra_anio(p, anio_min, anio_max):
                continue
            indicadores.asignar_puntaje_producto(p)
            pid = getattr(p, "id", "")
            ptit = getattr(p, "titulo", "")
            ptip = getattr(p, "tipo", "")
            pcat = getattr(p, "categoria", "")
            pw = getattr(p, "peso_relativo", 0.0)
            psc = getattr(p, "puntaje", 0.0)
            pval = "Sí" if getattr(p, "validado", True) else "No"
            self.tree_prods.insert("", "end", values=(pid, ptit, ptip, pcat, f"{pw:.1f}", f"{psc:.1f}", pval))
