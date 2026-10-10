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
    """Contenedor de gráfico estadístico Matplotlib con estado vacío centrado."""

    def __init__(self, master, title: Optional[str] = None, **kwargs):
        base_kwargs = {
            'fg_color': COLORS['surface'],
            'corner_radius': 0,
        }
        merged_kwargs = {**base_kwargs, **kwargs}
        super().__init__(master, **merged_kwargs)

        self._default_title = title
        self.fig = Figure(figsize=(3.8, 2.5), dpi=100)
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
        """Dibuja un gráfico de barras estilizado o muestra estado vacío centrado sin ejes."""
        self.ax.clear()
        bar_color = color or CHART_COLORS[0]
        chart_title = title or self._default_title

        has_data = labels and values and any(v > 0 for v in values)

        if has_data:
            self.ax.axis('on')
            str_labels = [str(l) for l in labels]
            self.ax.bar(
                str_labels,
                values,
                width=BAR_WIDTH,
                color=bar_color,
                edgecolor='none',
                zorder=3,
            )
            # Rotar levemente si hay muchas etiquetas o alguna es extensa
            if len(str_labels) > 4 or any(len(str(l)) > 6 for l in str_labels):
                self.ax.tick_params(axis='x', rotation=20)

            max_val = max(values) if values else 1
            self.ax.set_ylim(0, max_val * 1.15 if max_val > 0 else 1)
            style_bar_axes(self.ax, chart_title)
        else:
            # Ocultar completamente ejes, spines y cuadrícula en estado vacío
            self.ax.axis('off')

            if chart_title:
                self.ax.text(
                    0.0,
                    1.05,
                    chart_title,
                    transform=self.ax.transAxes,
                    fontsize=11,
                    fontweight='bold',
                    color=COLORS['ink'],
                    va='top',
                )

            # Mensaje centrado elegante y limpio sin glifos incompatibles
            self.ax.text(
                0.5,
                0.52,
                "Sin datos disponibles",
                ha='center',
                va='center',
                transform=self.ax.transAxes,
                fontsize=11,
                fontweight='bold',
                color=COLORS['ink_soft'],
            )
            self.ax.text(
                0.5,
                0.38,
                "Registra o importa información para visualizar la gráfica",
                ha='center',
                va='center',
                transform=self.ax.transAxes,
                fontsize=9,
                color=COLORS['muted'],
            )

        self.fig.tight_layout()
        self.canvas.draw()

    def clear(self):
        """Limpia el gráfico actual restableciendo el estado vacío centrado."""
        self.plot_bar([], [])