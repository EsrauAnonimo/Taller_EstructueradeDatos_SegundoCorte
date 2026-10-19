# -*- coding: utf-8 -*-
"""Formularios modales para la captura y edición de entidades en PEA-i."""

from .base_form import FormularioBase
from .grupo_form import GrupoForm
from .investigador_form import InvestigadorForm
from .producto_form import ProductoForm

__all__ = [
    "FormularioBase",
    "GrupoForm",
    "InvestigadorForm",
    "ProductoForm",
]
