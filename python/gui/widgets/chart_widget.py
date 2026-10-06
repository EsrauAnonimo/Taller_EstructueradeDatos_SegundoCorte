# -*- coding: utf-8 -*-
# Widget para graficos con matplotlib

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PyQt6.QtWidgets import QWidget, QVBoxLayout


class ChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax.grid(True, linestyle='--', alpha=0.3)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plot_bar(self, labels, values, title=''):
        self.clear()
        self.ax.bar(labels, values, color='#d6d1c9')
        self.ax.set_title(title)
        self.ax.tick_params(axis='x', rotation=45)
        self.canvas.draw()

    def clear(self):
        self.ax.clear()
        self.ax.grid(True, linestyle='--', alpha=0.3)
        self.canvas.draw()
