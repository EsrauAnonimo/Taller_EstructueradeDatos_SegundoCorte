# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QDialog
class InvestigadorForm(QDialog):
    def __init__(self,investigador=None,grupos=None,parent=None):
        super().__init__(parent)
