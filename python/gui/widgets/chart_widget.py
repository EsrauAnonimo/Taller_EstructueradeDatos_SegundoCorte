# -*- coding: utf-8 -*-
"""ChartWidget: Matplotlib wrapper embedded in CustomTkinter with modern styling."""

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


class ChartWidget(ctk.CTkFrame):
    """Contenedor de gráfico estadístico Matplotlib con estilo minimalista."""

    def __init__(self, master, title: Optional[str] = None, **kwargs):
        base_kwargs = {
            'fg_color': COLORS['surface'],
            'corner_radius': 0,
        }
        merged_kwargs = {**base_kwargs, **kwargs}
        super().__init__(master, **merged_kwargs)

        self._default_title = title
        # Figura con fondo uniforme a la tarjeta
        self.fig = Figure(figsize=(3.8, 2.6), dpi=100)
        self.fig.patch.set_facecolor(COLORS['surface'])

        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(COLORS['surface'])
        style_bar_axes(self.ax, self._default_title)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.configure(bg=COLORS['surface'], highlightthickness=0)
        self.canvas_widget.pack(fill='both', expand=True, padx=4, pady=4)

    def plot_bar(
        self,
        labels: List[Union[str, int]],
        values: List[Union[int, float]],
        title: Optional[str] = None,
        color: Optional[str] = None,
    ):
        """Dibuja un gráfico de barras estilizado."""
        self.ax.clear()
        bar_color = color or CHART_COLORS[0]
        chart_title = title or self._default_title

        if labels and values and any(v > 0 for v in values):
            str_labels = [str(l) for l in labels]
            bars = self.ax.bar(
                str_labels,
                values,
                width=BAR_WIDTH,
                color=bar_color,
                edgecolor='none',
                zorder=3,
            )
            # Si hay más de 4 etiquetas o alguna es larga, rotar levemente para legibilidad
            if len(str_labels) > 4 or any(len(str(l)) > 6 for l in str_labels):
                self.ax.tick_params(axis='x', rotation=20)

            # Ajuste de escala en eje Y para que los valores no toquen el borde superior
            max_val = max(values) if values else 1
            self.ax.set_ylim(0, max_val * 1.15 if max_val > 0 else 1)
        else:
            # Estado sin datos
            self.ax.text(
                0.5,
                0.5,
                "Sin datos para graficar",
                ha='center',
                va='center',
                transform=self.ax.transAxes,
                color=COLORS['muted'],
                fontsize=11,
            )

        style_bar_axes(self.ax, chart_title)
        self.fig.tight_layout()
        self.canvas.draw()

    def clear(self):
        """Limpia el gráfico actual."""
        self.ax.clear()
        style_bar_axes(self.ax, self._default_title)
        self.canvas.draw()