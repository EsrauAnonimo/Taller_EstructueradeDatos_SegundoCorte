# -*- coding: utf-8 -*-
# Grupos tab
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox
from gui.forms.grupo_form import GrupoForm
from entidades.grupo import Grupo

class GruposTab(QWidget):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.table = QTableWidget(0,6)
        self.table.setHorizontalHeaderLabels(['ID','Código Gruplac','Nombre','Categoría','Líder','Activo'])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.btn_create = QPushButton('Crear')
        self.btn_edit = QPushButton('Editar')
        self.btn_delete = QPushButton('Eliminar')
        self.btn_refresh = QPushButton('Actualizar')
        self.btn_create.clicked.connect(self.create_group)
        self.btn_edit.clicked.connect(self.edit_group)
        self.btn_delete.clicked.connect(self.delete_group)
        self.btn_refresh.clicked.connect(self.load_data)
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
            grupos = self.app.grupo_crud.list_all()
        except Exception:
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
            self.table.setItem(row,0,QTableWidgetItem(str(getattr(g,'id',''))))
            self.table.setItem(row,1,QTableWidgetItem(str(getattr(g,'codigo_gruplac',''))))
            self.table.setItem(row,2,QTableWidgetItem(str(getattr(g,'nombre',''))))
            self.table.setItem(row,3,QTableWidgetItem(str(getattr(g,'categoria',''))))
            self.table.setItem(row,4,QTableWidgetItem(str(getattr(g,'lider',''))))
            self.table.setItem(row,5,QTableWidgetItem('Sí' if getattr(g,'activo',True) else 'No'))
    def get_selected_id(self):
        row = self.table.currentRow()
        if row < 0: return None
        item = self.table.item(row,0)
        if not item: return None
        try:
            return int(item.text())
        except Exception:
            return None
    def create_group(self):
        dlg = GrupoForm(parent=self)
        if dlg.exec():
            try:
                self.app.grupo_crud.create(Grupo(**dlg.get_data()))
                self.app.save_data()
                self.load_data()
            except Exception as e:
                QMessageBox.warning(self,'Error',str(e))
    def edit_group(self):
        gid = self.get_selected_id()
        if not gid: return
        try:
            g = self.app.grupo_crud.get_by_id(gid)
        except Exception:
            g = None
        if not g: return
        dlg = GrupoForm(grupo=g,parent=self)
        if dlg.exec():
            try:
                self.app.grupo_crud.update(gid,**dlg.get_data())
                self.app.save_data()
                self.load_data()
            except Exception as e:
                QMessageBox.warning(self,'Error',str(e))
    def delete_group(self):
        gid = self.get_selected_id()
        if not gid: return
        if QMessageBox.question(self,'Confirmar','¿Eliminar grupo?') == QMessageBox.StandardButton.Yes:
            try:
                self.app.grupo_crud.delete(gid)
                self.app.save_data()
                self.load_data()
            except Exception as e:
                QMessageBox.warning(self,'Error',str(e))
