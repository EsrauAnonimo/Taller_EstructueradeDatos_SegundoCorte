# -*- coding: utf-8 -*-
"""Capa de persistencia."""

from .persistencia import PersistenciaBase
from .persistencia_json import PersistenciaJSON

__all__ = ['PersistenciaBase', 'PersistenciaJSON']