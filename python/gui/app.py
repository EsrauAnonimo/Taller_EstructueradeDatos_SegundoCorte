# -*- coding: utf-8 -*-
import sys
import traceback
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
print('Iniciando PEA-i GUI...')
from PyQt6.QtWidgets import QMainWindow, QApplication, QTabWidget, QMessageBox, QStatusBar
from PyQt6.QtGui import QAction
from persistencia.persistencia_postgres import PersistenciaPostgres
from persistencia.persistencia_json import PersistenciaJSON
from modelos.multilista import Multilist
from crud.crud_grupos import GrupoCRUD
from crud.crud_investigadores import InvestigadorCRUD
from crud.crud_productos import ProductoCRUD
from gui.tabs.grupos_tab import GruposTab
from gui.tabs.investigadores_tab import InvestigadoresTab
from gui.tabs.productos_tab import ProductosTab
from gui.tabs.estadisticas_tab import EstadisticasTab
from gui.styles import STYLES
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PEA-i - Programa Estadístico de Análisis de Investigación')
        self.setMinimumSize(1200,700)
        self.persistencia = None
        self.multilista = Multilist()
        self.grupo_crud = GrupoCRUD(self.multilista)
        self.inv_crud = InvestigadorCRUD(self.multilista)
        self.prod_crud = ProductoCRUD(self.multilista)
        self.init_persistence()
        self.tab_widget = QTabWidget()
        self.grupos_tab = GruposTab(self)
        self.investigadores_tab = InvestigadoresTab(self)
        self.productos_tab = ProductosTab(self)
        self.estadisticas_tab = EstadisticasTab(self)
        self.tab_widget.addTab(self.grupos_tab,'Grupos')
        self.tab_widget.addTab(self.investigadores_tab,'Investigadores')
        self.tab_widget.addTab(self.productos_tab,'Productos')
        self.tab_widget.addTab(self.estadisticas_tab,'Estadísticas')
        self.setCentralWidget(self.tab_widget)
        self.create_menu()
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status()
        self.load_data()
    def init_persistence(self):
        try:
            p = PersistenciaPostgres()
            if p.conectar():
                p.desconectar()
                self.persistencia = p
                print('Persistencia activa: PostgreSQL')
                return
        except Exception as e:
            print('Error al intentar conectar:',e)
        self.persistencia = PersistenciaJSON()
        print('Persistencia activa: JSON')
        QMessageBox.warning(self,'Advertencia','Usando JSON.')
    def create_menu(self):
        m = self.menuBar()
        a = m.addMenu('Archivo')
        ac = QAction('Cargar datos',self); ag=QAction('Guardar datos',self); asx=QAction('Salir',self)
        ac.triggered.connect(self.load_data); ag.triggered.connect(self.save_data); asx.triggered.connect(self.close)
        a.addAction(ac); a.addAction(ag); a.addSeparator(); a.addAction(asx)
        d = m.addMenu('Datos'); dd=QAction('Descargar del SCIENTI',self); d.addAction(dd)
        h = m.addMenu('Ayuda'); ha=QAction('Acerca de',self); ha.triggered.connect(lambda:QMessageBox.information(self,'Acerca de','PEA-i')); h.addAction(ha)
    def update_status(self):
        name='PostgreSQL' if isinstance(self.persistencia,PersistenciaPostgres) else 'JSON'
        self.status_bar.showMessage('Capa de persistencia: '+name)
    def load_data(self):
        try:
            datos=self.persistencia.cargar()
            self.multilista=Multilist(); self.grupo_crud=GrupoCRUD(self.multilista); self.inv_crud=InvestigadorCRUD(self.multilista); self.prod_crud=ProductoCRUD(self.multilista)
            if datos:
                if 'grupos' in datos:
                    for g in datos['grupos']:
                        obj=self.grupo_crud.from_dict(g) if hasattr(self.grupo_crud,'from_dict') else g
                        self.grupo_crud.agregar(obj)
                if 'investigadores' in datos:
                    for i in datos['investigadores']:
                        obj=self.inv_crud.from_dict(i) if hasattr(self.inv_crud,'from_dict') else i
                        self.inv_crud.agregar(obj)
                if 'productos' in datos:
                    for p in datos['productos']:
                        obj=self.prod_crud.from_dict(p) if hasattr(self.prod_crud,'from_dict') else p
                        self.prod_crud.agregar(obj)
        except Exception:
            pass
        try:
            self.grupos_tab.load_data(); self.investigadores_tab.load_data(); self.productos_tab.load_data(); self.estadisticas_tab.load_data()
        except Exception:
            pass
    def save_data(self):
        try:
            datos={'grupos':[g.to_dict() if hasattr(g,'to_dict') else g.__dict__ for g in self.grupo_crud.listar()],'investigadores':[i.to_dict() if hasattr(i,'to_dict') else i.__dict__ for i in self.inv_crud.listar()],'productos':[p.to_dict() if hasattr(p,'to_dict') else p.__dict__ for p in self.prod_crud.listar()]}
            self.persistencia.guardar(datos)
        except Exception:
            pass
def main():
    try:
        app=QApplication(sys.argv)
        app.setStyleSheet(STYLES)
        w=MainWindow()
        w.show()
        print('Mostrando ventana principal...')
        sys.exit(app.exec())
    except Exception as e:
        print('Error al iniciar la GUI:',e)
        traceback.print_exc()
if __name__=='__main__':
    main()
