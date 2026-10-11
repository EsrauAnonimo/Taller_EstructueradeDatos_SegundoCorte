# -*- coding: utf-8 -*-
"""ChartWidget: Matplotlib wrapper embebido en CustomTkinter con diseno moderno."""

from typing import List, Union, Optional
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk

from gui.styles import (
    COLORS,
    CHART_COLORS,
    BAR_WIDTH,
    style_bar_axes,
)

_EMPTY_TITLE = "Sin datos para graficar"
_EMPTY_SUB = "No hay registros disponibles para este periodo o filtro"


def _draw_empty(ax, title: Optional[str] = None):
    """Oculta completamente los ejes y cuadricula y muestra un estado vacio elegante."""
    ax.clear()
    ax.axis("off")
    ax.set_facecolor(COLORS["surface"])
    if ax.figure is not None:
        ax.figure.patch.set_facecolor(COLORS["surface"])

    if title:
        ax.text(
            0.0, 1.08, title,
            transform=ax.transAxes,
            fontsize=11, fontweight="bold",
            color=COLORS["ink"], va="top", ha="left",
        )

    # Mensaje centrado elegante sin glifos incompatibles
    ax.text(
        0.5, 0.54, _EMPTY_TITLE,
        ha="center", va="center",
        transform=ax.transAxes,
        fontsize=12, fontweight="bold",
        color=COLORS["ink_soft"],
    )
    ax.text(
        0.5, 0.40, _EMPTY_SUB,
        ha="center", va="center",
        transform=ax.transAxes,
        fontsize=9,
        color=COLORS["muted"],
    )


class ChartWidget(ctk.CTkFrame):
    """Contenedor de grafico estadistico Matplotlib reutilizable y optimizado.
    
    Reutiliza la misma instancia de Figure y FigureCanvasTkAgg para evitar
    degradacion de rendimiento y latencia en tkinter.
    """

    def __init__(self, master, title: Optional[str] = None, figsize=(4.0, 2.6), **kwargs):
        base_kwargs = {
            "fg_color": COLORS["surface"],
            "corner_radius": 0,
        }
        merged_kwargs = {**base_kwargs, **kwargs}
        super().__init__(master, **merged_kwargs)

        self._default_title = title
        # 1. Crear figura y canvas una sola vez
        self.fig = Figure(figsize=figsize, dpi=100)
        self.fig.patch.set_facecolor(COLORS["surface"])

        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(COLORS["surface"])
        _draw_empty(self.ax, self._default_title)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.configure(bg=COLORS["surface"], highlightthickness=0)
        self.canvas_widget.pack(fill="both", expand=True, padx=4, pady=4)
        self.canvas.draw()

    # ------------------------------------------------------------------
    def _reset(self):
        """Limpia los ejes sin recrear la figura ni el canvas."""
        self.ax.clear()
        self.ax.set_facecolor(COLORS["surface"])
        if self.fig:
            self.fig.patch.set_facecolor(COLORS["surface"])

    def _finish(self):
        """Ajusta margenes y redibuja de forma eficiente con draw_idle()."""
        try:
            self.fig.tight_layout()
        except Exception:
            pass
        self.canvas.draw_idle()

    # ------------------------------------------------------------------
    def plot_bar(
        self,
        labels: List[Union[str, int]],
        values: List[Union[int, float]],
        title: Optional[str] = None,
        color: Optional[str] = None,
        add_value_labels: bool = True,
    ):
        """Grafico de barras verticales con estilo limpio y valores sobre cada barra."""
        self._reset()
        bar_color = color or CHART_COLORS[0]
        chart_title = title or self._default_title
        has_data = bool(labels and values and any(v > 0 for v in values))

        if has_data:
            self.ax.axis("on")
            str_labels = [str(l) for l in labels]
            bars = self.ax.bar(
                str_labels, values,
                width=BAR_WIDTH,
                color=bar_color,
                edgecolor="none",
                zorder=3,
            )

            # Rotar etiquetas si son muchas o muy largas
            if len(str_labels) > 4 or any(len(s) > 6 for s in str_labels):
                self.ax.tick_params(axis="x", rotation=25)
            else:
                self.ax.tick_params(axis="x", rotation=0)

            max_val = max(values) if values else 1
            self.ax.set_ylim(0, max_val * 1.18 if max_val > 0 else 1)

            # Valores sobre las barras
            if add_value_labels:
                for bar, v in zip(bars, values):
                    if v > 0:
                        lbl_text = str(int(v)) if float(v) == int(v) else f"{v:.1f}"
                        self.ax.text(
                            bar.get_x() + bar.get_width() / 2,
                            bar.get_height() + max_val * 0.02,
                            lbl_text,
                            ha="center", va="bottom",
                            fontsize=8, fontweight="bold",
                            color=COLORS["ink_soft"],
                        )
            style_bar_axes(self.ax, chart_title)
        else:
            _draw_empty(self.ax, chart_title)

        self._finish()

    # ------------------------------------------------------------------
    def plot_barh(
        self,
        labels: List[str],
        values: List[Union[int, float]],
        title: Optional[str] = None,
        color: Optional[str] = None,
        add_value_labels: bool = True,
        max_items: int = 10,
    ):
        """Grafico de barras horizontales ordenadas de mayor a menor."""
        self._reset()
        bar_color = color or CHART_COLORS[1]
        chart_title = title or self._default_title
        has_data = bool(labels and values and any(v > 0 for v in values))

        if has_data:
            self.ax.axis("on")
            # Ordenar de mayor a menor para lectura jerarquica
            pairs = sorted(zip(values, labels), reverse=True)
            # Limitar a max_items para evitar saturacion visual si hay muchos
            if max_items and len(pairs) > max_items:
                pairs = pairs[:max_items]
            sorted_vals = [p[0] for p in pairs]
            sorted_lbls = [str(p[1]) for p in pairs]

            bars = self.ax.barh(
                sorted_lbls, sorted_vals,
                height=BAR_WIDTH,
                color=bar_color,
                edgecolor="none",
                zorder=3,
            )
            # Invertir eje Y para que el mayor quede arriba
            self.ax.invert_yaxis()

            max_val = max(sorted_vals) if sorted_vals else 1
            self.ax.set_xlim(0, max_val * 1.20 if max_val > 0 else 1)

            # Valores a la derecha de cada barra
            if add_value_labels:
                for bar, v in zip(bars, sorted_vals):
                    if v > 0:
                        lbl_text = str(int(v)) if float(v) == int(v) else f"{v:.1f}"
                        self.ax.text(
                            bar.get_width() + max_val * 0.02,
                            bar.get_y() + bar.get_height() / 2,
                            lbl_text,
                            va="center", ha="left",
                            fontsize=8, fontweight="bold",
                            color=COLORS["ink_soft"],
                        )

            # Estilo horizontal limpio: sin lineas superfluas
            self.ax.spines["top"].set_visible(False)
            self.ax.spines["right"].set_visible(False)
            self.ax.spines["bottom"].set_visible(False)
            self.ax.spines["left"].set_color(COLORS["border"])
            self.ax.tick_params(left=False, bottom=False, labelsize=9,
                                labelcolor=COLORS["muted"])
            self.ax.xaxis.grid(True, color=COLORS["border"],
                               linestyle="-", linewidth=0.8, alpha=0.6)
            self.ax.yaxis.grid(False)
            self.ax.set_facecolor(COLORS["surface"])
            if chart_title:
                self.ax.set_title(
                    chart_title, loc="left",
                    fontsize=12, fontweight="bold",
                    color=COLORS["ink"], pad=14,
                )
        else:
            _draw_empty(self.ax, chart_title)

        self._finish()

    # ------------------------------------------------------------------
    def plot_histogram(
        self,
        values: List[Union[int, float]],
        bins: int = 6,
        title: Optional[str] = None,
        color: Optional[str] = None,
    ):
        """Histograma estilizado de distribucion de frecuencias."""
        self._reset()
        bar_color = color or CHART_COLORS[3]
        chart_title = title or self._default_title
        filtered = [v for v in values if v is not None and v > 0]
        has_data = len(filtered) > 0

        if has_data:
            self.ax.axis("on")
            n_bins = max(1, min(bins, len(set(filtered))))
            counts, bin_edges, patches = self.ax.hist(
                filtered,
                bins=n_bins,
                color=bar_color,
                edgecolor=COLORS["surface"],
                linewidth=1.2,
                zorder=3,
                rwidth=0.88,
            )
            # Valores sobre las barras del histograma
            max_c = max(counts) if len(counts) > 0 and max(counts) > 0 else 1
            self.ax.set_ylim(0, max_c * 1.18)
            for count, patch in zip(counts, patches):
                if count > 0:
                    self.ax.text(
                        patch.get_x() + patch.get_width() / 2,
                        patch.get_height() + max_c * 0.02,
                        str(int(count)),
                        ha="center", va="bottom",
                        fontsize=8, fontweight="bold",
                        color=COLORS["ink_soft"],
                    )
            style_bar_axes(self.ax, chart_title)
        else:
            _draw_empty(self.ax, chart_title)

        self._finish()

    # ------------------------------------------------------------------
    def clear(self):
        """Limpia el grafico mostrando el estado vacio centrado."""
        self._reset()
        _draw_empty(self.ax, self._default_title)
        self._finish()

    def save_image(self, filepath: str):
        """Guarda la figura actual en disco en formato PNG de alta resolucion."""
        self.fig.savefig(
            filepath,
            dpi=200,
            bbox_inches="tight",
            facecolor=COLORS["surface"],
        )
