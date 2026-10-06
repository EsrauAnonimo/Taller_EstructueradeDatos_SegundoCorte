# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QDialog
class ProductoForm(QDialog):
    def __init__(self,producto=None,investigadores=None,parent=None):
        super().__init__(parent)
