# -*- coding: utf-8 -*-
"""Estilos y tema para GUI CustomTkinter."""

import customtkinter as ctk

COLOR_PALETTE = {
    'bg': '#FAF9F6',
    'fg': '#1A1A1A',
    'muted': '#6B6B6B',
    'border': '#E5E3DF',
    'accent': '#1A1A1A',
    'accent_text': '#FAF9F6',
}


def apply_theme():
    """Aplica tema claro."""
    ctk.set_appearance_mode('light')
    ctk.set_default_color_theme('blue')