# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton
class InvestigadoresTab(QWidget):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.table = QTableWidget(0,7)
        self.table.setHorizontalHeaderLabels(['ID','Cédula','Nombres','Apellidos','Email','Grupo','Activo'])
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(QPushButton('Crear')); btn_layout.addWidget(QPushButton('Editar'))
        btn_layout.addWidget(QPushButton('Actualizar')); btn_layout.addStretch()
        layout = QVBoxLayout(); layout.addLayout(btn_layout); layout.addWidget(self.table); self.setLayout(layout)
    def load_data(self):
        pass
