# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QComboBox, QLabel, QSpinBox
class ProductosTab(QWidget):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.table = QTableWidget(0,8)
        self.table.setHorizontalHeaderLabels(['ID','Título','Tipo','Categoría','Año','Validado','Investigador','Grupo'])
        layout = QVBoxLayout(); layout.addWidget(self.table); self.setLayout(layout)
    def load_data(self):
        pass
