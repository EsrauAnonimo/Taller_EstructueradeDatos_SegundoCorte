# -*- coding: utf-8 -*-
"""Pestaña de Indicador de Producción Científica (Modelo MinCiencias - Parcial 2)."""

from typing import Optional, List, Dict, Any
import datetime
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

        # 4. Cargar datos iniciales en la pestaña
        self.refresh(silent=True)

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
            command=self._on_target_changed,
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

        self.combo_year = ctk.CTkComboBox(
            filter_row,
            width=180,
            values=["Todos", "Últimos 2", "Últimos 5", "Personalizado"],
            command=self._on_year_filter_mode_change,
            font=font("body"),
            dropdown_font=font("body"),
            corner_radius=RADIUS["control"],
            border_color=COLORS["border"],
        )
        self.combo_year.set("Todos")
        self.combo_year.pack(side="left", padx=(0, 15))

        self.frame_range = ctk.CTkFrame(filter_row, fg_color="transparent")
        # Se muestra únicamente cuando se selecciona Personalizado

        lbl_d = ctk.CTkLabel(self.frame_range, text="Desde:", font=font("small"), text_color=COLORS["ink"])
        lbl_d.pack(side="left", padx=(0, 4))
        self.entry_desde = ctk.CTkEntry(self.frame_range, width=70, font=font("small"), corner_radius=RADIUS["control"])
        self.entry_desde.insert(0, "2020")
        self.entry_desde.pack(side="left", padx=(0, 10))
        self.entry_desde.bind("<Return>", lambda _e: self.calcular(silent=False))

        lbl_h = ctk.CTkLabel(self.frame_range, text="Hasta:", font=font("small"), text_color=COLORS["ink"])
        lbl_h.pack(side="left", padx=(0, 4))
        self.entry_hasta = ctk.CTkEntry(self.frame_range, width=70, font=font("small"), corner_radius=RADIUS["control"])
        self.entry_hasta.insert(0, "2026")
        self.entry_hasta.pack(side="left")
        self.entry_hasta.bind("<Return>", lambda _e: self.calcular(silent=False))

        self.btn_apply_range = ctk.CTkButton(
            self.frame_range,
            text="Aplicar",
            width=65,
            height=28,
            font=font("small"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            corner_radius=RADIUS["control"],
            command=lambda: self.calcular(silent=False),
        )
        self.btn_apply_range.pack(side="left", padx=(8, 0))

    def _on_target_changed(self, choice: Optional[str] = None):
        """Manejador al cambiar la selección en el ComboBox de Grupo o Investigador."""
        self.calcular(silent=True)

    def _on_year_filter_mode_change(self, mode: str):
        """Maneja el cambio de modo en el filtro por año."""
        if mode == "Personalizado":
            self.frame_range.pack(side="left")
        else:
            self.frame_range.pack_forget()
        self.calcular(silent=True)


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
        selected = self.combo_target.get() if self.combo_target else ""
        if selected and "No hay" not in selected and "Cargando" not in selected:
            self.calcular(silent=True)

    def refresh(self, silent: bool = True):
        """Recarga los datos de grupos e investigadores desde la multilista."""
        self._load_caches()
        self._populate_combo()
        selected = self.combo_target.get() if self.combo_target else ""
        if selected and "No hay" not in selected and "Cargando" not in selected:
            try:
                self.calcular(silent=silent)
            except Exception as e:
                print(f"Aviso al actualizar indicador: {e}")

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
                if gid is None or gid == "":
                    gid = getattr(curr_g.data, "codigo_gruplac", "")
                gnom = getattr(curr_g.data, "nombre", f"Grupo {gid}")
                self._grupos_cache.append((gid, f"[{gid}] {gnom}"))

                curr_i = curr_g.sublist
                while curr_i is not None:
                    if curr_i.active:
                        cedula = getattr(curr_i.data, "cedula", None)
                        iid = cedula if cedula else (getattr(curr_i.data, "id", None) or "")
                        nom_full = (
                            getattr(curr_i.data, "nombre", "")
                            or f"{getattr(curr_i.data, 'nombres', '')} {getattr(curr_i.data, 'apellidos', '')}".strip()
                            or f"Investigador {iid}"
                        )
                        self._investigadores_cache.append((iid, f"[{iid}] {nom_full} ({gnom})"))
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

    def _reset_results(self):
        """Restablece los textos de KPIs y vacía las tablas de resultados."""
        self.card_total.lbl_value.configure(text="0.0")
        if self.card_total.lbl_note is not None:
            self.card_total.lbl_note.configure(text="Puntaje de producción MinCiencias")
        if hasattr(self.card_total, "update_value"):
            self.card_total.update_value("0.0")

        self.card_prods.lbl_value.configure(text="0")
        if self.card_prods.lbl_note is not None:
            self.card_prods.lbl_note.configure(text="0 validados para medición")
        if hasattr(self.card_prods, "update_value"):
            self.card_prods.update_value("0", note="0 validados para medición")

        self.card_top.lbl_value.configure(text="0")
        if hasattr(self.card_top, "update_value"):
            self.card_top.update_value("0")

        self.card_entidad.lbl_value.configure(text="—")
        if self.card_entidad.lbl_note is not None:
            self.card_entidad.lbl_note.configure(text="Seleccione una entidad para calcular")
        if hasattr(self.card_entidad, "update_value"):
            self.card_entidad.update_value("—", note="Seleccione una entidad para calcular")

        for item in self.tree_breakdown.get_children():
            self.tree_breakdown.delete(item)

        for item in self.tree_prods.get_children():
            self.tree_prods.delete(item)

    def calcular(self, silent: bool = False):
        """Calcula el indicador según la entidad seleccionada en el ComboBox."""
        print("Calculando indicador...")

        app = self._app_ref
        if not app or not hasattr(app, "multilista") or app.multilista.head_group is None:
            if not silent:
                messagebox.showwarning("Atención", "No hay datos para calcular")
            self._reset_results()
            return

        if not self._grupos_cache and not self._investigadores_cache:
            self._load_caches()

        if self._selected_mode == "Grupo" and not self._grupos_cache:
            if not silent:
                messagebox.showwarning("Atención", "No hay datos para calcular")
            self._reset_results()
            return
        elif self._selected_mode == "Investigador" and not self._investigadores_cache:
            if not silent:
                messagebox.showwarning("Atención", "No hay datos para calcular")
            self._reset_results()
            return

        selected_text = self.combo_target.get().strip() if self.combo_target else ""
        if not selected_text or "No hay" in selected_text or "Cargando" in selected_text:
            if not silent:
                messagebox.showwarning("Atención", "No hay datos para calcular")
            self._reset_results()
            return

        # Extraer el ID o Cédula dentro de los corchetes [ID]
        target_id = None
        if "[" in selected_text and "]" in selected_text:
            target_id = selected_text.split("[")[1].split("]")[0].strip()

        if not target_id:
            if not silent:
                messagebox.showwarning("Atención", "No hay datos para calcular")
            self._reset_results()
            return

        # Determinar filtro por año desde el ComboBox
        filtro_modo = self.combo_year.get().strip()
        anio_min = None
        anio_max = None
        current_year = datetime.date.today().year
        filtro_desc = "Todos los años"

        if "2" in filtro_modo:
            anio_min = current_year - 2
            anio_max = current_year
            filtro_desc = f"{anio_min} - {anio_max}"
        elif "5" in filtro_modo:
            anio_min = current_year - 5
            anio_max = current_year
            filtro_desc = f"{anio_min} - {anio_max}"
        elif "Personalizado" in filtro_modo or "Rango" in filtro_modo:
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
                if not silent:
                    messagebox.showwarning("Atención", "Los años del rango deben ser números enteros.")
                return

        # Ejecutar cálculo
        try:
            if self._selected_mode == "Grupo":
                calc_id = int(target_id) if str(target_id).isdigit() else target_id
                res = indicadores.calcular_indicador_grupo(
                    app.multilista, calc_id, anio_min=anio_min, anio_max=anio_max
                )
                productos = app.multilista.get_productos_by_grupo(calc_id)
                if not productos and not str(target_id).isdigit():
                    g_node = app.multilista.get_group_by_code(str(target_id))
                    if g_node and hasattr(g_node.data, "id"):
                        productos = app.multilista.get_productos_by_grupo(g_node.data.id)
            else:
                calc_id = str(target_id)
                res = indicadores.calcular_indicador_investigador(
                    app.multilista, calc_id, anio_min=anio_min, anio_max=anio_max
                )
                productos = app.multilista.get_productos_by_investigador(calc_id)

            print(f"Indicador calculado exitosamente: {res.get('indicador', 0.0):.2f} ({res.get('entidad_nombre', '')})")
        except Exception as err:
            print(f"Error al calcular indicador: {err}")
            if not silent:
                messagebox.showerror("Error", f"Error al calcular el indicador: {err}")
            return

        # Actualizar KPIs usando .configure() y set_value / update_value
        indicador_str = f"{res['indicador']:.2f}"
        self.card_total.lbl_value.configure(text=indicador_str)
        if hasattr(self.card_total, "update_value"):
            self.card_total.update_value(indicador_str)
        elif hasattr(self.card_total, "set_value"):
            self.card_total.set_value(indicador_str)

        total_prods_count = res.get("total_productos", 0)
        if productos:
            prods_en_periodo = [p for p in productos if indicadores._filtra_anio(p, anio_min, anio_max)]
            total_prods_count = max(len(prods_en_periodo), res.get("total_validados", 0))

        prods_str = str(total_prods_count)
        prods_note = f"{res.get('total_validados', 0)} validados · Filtro: {filtro_desc}"
        self.card_prods.lbl_value.configure(text=prods_str)
        if self.card_prods.lbl_note is not None:
            self.card_prods.lbl_note.configure(text=prods_note)
        if hasattr(self.card_prods, "update_value"):
            self.card_prods.update_value(prods_str, note=prods_note)
        elif hasattr(self.card_prods, "set_value"):
            self.card_prods.set_value(prods_str, note=prods_note)

        top_a_count = str(res["counts"].get("Nc_Top", 0) + res["counts"].get("Nc_A", 0))
        self.card_top.lbl_value.configure(text=top_a_count)
        if hasattr(self.card_top, "update_value"):
            self.card_top.update_value(top_a_count)
        elif hasattr(self.card_top, "set_value"):
            self.card_top.set_value(top_a_count)

        entidad_nombre = res.get("entidad_nombre", str(target_id))
        if len(entidad_nombre) > 22:
            entidad_nombre = entidad_nombre[:20] + "..."
        entidad_note = f"Tipo: {res.get('entidad_tipo', self._selected_mode)}"
        self.card_entidad.lbl_value.configure(text=entidad_nombre)
        if self.card_entidad.lbl_note is not None:
            self.card_entidad.lbl_note.configure(text=entidad_note)
        if hasattr(self.card_entidad, "update_value"):
            self.card_entidad.update_value(entidad_nombre, note=entidad_note)
        elif hasattr(self.card_entidad, "set_value"):
            self.card_entidad.set_value(entidad_nombre, note=entidad_note)

        # Limpiar y actualizar tabla de desglose
        for item in self.tree_breakdown.get_children():
            self.tree_breakdown.delete(item)

        for var, coef in res["coefficients"].items():
            desc = res["descriptions"].get(var, var)
            val = res["counts"].get(var, 0)
            sub = res["subtotals"].get(var, 0.0)
            val_str = f"{val:.2f}" if isinstance(val, float) else str(val)
            self.tree_breakdown.insert("", "end", values=(var, desc, f"{coef}", val_str, f"{sub:.2f}"))

        # Limpiar y actualizar tabla de productos detallada filtrada por año
        for item in self.tree_prods.get_children():
            self.tree_prods.delete(item)

        for p in productos:
            if not indicadores._filtra_anio(p, anio_min, anio_max):
                continue
            is_val = indicadores._es_validado(p)
            is_act = indicadores._es_activo(p)
            indicadores.asignar_puntaje_producto(p)
            pid = getattr(p, "id", "")
            ptit = getattr(p, "titulo", "")
            ptip = getattr(p, "tipo", "")
            pcat = getattr(p, "categoria", "")
            pw = getattr(p, "peso_relativo", 0.0)
            psc = getattr(p, "puntaje", 0.0) if (is_val and is_act) else 0.0
            if not is_act:
                pval = "No (Inactivo)"
            elif not is_val:
                pval = "No (No validado)"
            else:
                pval = "Sí (Validado)"
            self.tree_prods.insert("", "end", values=(pid, ptit, ptip, pcat, f"{pw:.1f}", f"{psc:.1f}", pval))

        # Feedback visual cuando el cálculo fue ejecutado explícitamente con el botón
        if not silent:
            try:
                original_text = self.btn_calc.cget("text")
                self.btn_calc.configure(text="  ✓ Calculado")
                self.after(1400, lambda: self.btn_calc.configure(text=original_text))
            except Exception:
                pass
            if app and hasattr(app, "show_toast"):
                app.show_toast(f"Indicador calculado: {res['indicador']:.2f} pts ({entidad_nombre})")

