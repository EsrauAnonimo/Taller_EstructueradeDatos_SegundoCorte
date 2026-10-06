# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from gui.widgets.chart_widget import ChartWidget
class EstadísticasTab(QWidget):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        top=QHBoxLayout(); top.addWidget(QLabel('Grupos: 0')); top.addWidget(QLabel('Inv: 0')); top.addWidget(QLabel('Prod: 0'))
        layout=QVBoxLayout(); layout.addLayout(top); layout.addWidget(QLabel('Stats')); self.setLayout(layout)
    def load_data(self):
        pass
