# -*- coding: utf-8 -*-
# Grupos tab
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox
from gui.forms.grupo_form import GrupoForm

class GruposTab(QWidget):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.table = QTableWidget(0,6)
        self.table.setHorizontalHeaderLabels(['ID','Código','Nombre','Categoría','Líder','Activo'])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.btn_create = QPushButton('Crear')
        self.btn_edit = QPushButton('Editar')
        self.btn_delete = QPushButton('Eliminar')
        self.btn_refresh = QPushButton('Actualizar')
        btn_layout = QHBoxLayout()
        for b in [self.btn_create,self.btn_edit,self.btn_delete,self.btn_refresh]:
            btn_layout.addWidget(b)
        btn_layout.addStretch()
        layout = QVBoxLayout()
        layout.addLayout(btn_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)
    def load_data(self):
        self.table.setRowCount(0)
        try:
            grupos = self.app.grupo_crud.listar()
        except Exception:
            grupos = []
        if not grupos:
            self.table.setRowCount(1)
            for c in range(6):
                self.table.setItem(0,c,QTableWidgetItem('No hay datos'))
            return
        self.table.setRowCount(len(grupos))
        for row,g in enumerate(grupos):
            self.table.setItem(row,0,QTableWidgetItem(str(g.id)))
            self.table.setItem(row,1,QTableWidgetItem(g.codigo or ''))
            self.table.setItem(row,2,QTableWidgetItem(g.nombre or ''))
            self.table.setItem(row,3,QTableWidgetItem(g.categoria or ''))
            self.table.setItem(row,4,QTableWidgetItem(g.lider or ''))
            self.table.setItem(row,5,QTableWidgetItem('Sí' if g.activo else 'No'))
