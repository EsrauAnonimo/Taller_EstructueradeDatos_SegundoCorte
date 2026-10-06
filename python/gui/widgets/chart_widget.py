# -*- coding: utf-8 -*-
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk


class ChartWidget(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.fig = Figure(figsize=(4, 2.5), dpi=100)
        self.fig.patch.set_facecolor('#FAF9F6')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#FAF9F6')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def plot_bar(self, labels, values):
        self.ax.clear()
        if labels:
            self.ax.bar(labels, values, color='#4A4A4A')
        self.ax.grid(color='#E5E3DF', linestyle='--', linewidth=0.5, alpha=0.5)
        self.ax.set_facecolor('#FAF9F6')
        self.fig.patch.set_facecolor('#FAF9F6')
        self.fig.tight_layout()
        self.canvas.draw()

    def clear(self):
        self.ax.clear()
        self.canvas.draw()