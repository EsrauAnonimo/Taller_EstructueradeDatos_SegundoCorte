# -*- coding: utf-8 -*-
import customtkinter as ctk
from gui.widgets.chart_widget import ChartWidget


class EstadisticasTab(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.card1 = ctk.CTkFrame(self)
        self.card1.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        self.lbl1_title = ctk.CTkLabel(self.card1, text='Grupos activos')
        self.lbl1_title.pack(padx=10, pady=(10, 2))
        self.lbl1_val = ctk.CTkLabel(self.card1, text='0', font=('', 24))
        self.lbl1_val.pack(padx=10, pady=(2, 10))

        self.card2 = ctk.CTkFrame(self)
        self.card2.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)
        self.lbl2_title = ctk.CTkLabel(self.card2, text='Investigadores activos')
        self.lbl2_title.pack(padx=10, pady=(10, 2))
        self.lbl2_val = ctk.CTkLabel(self.card2, text='0', font=('', 24))
        self.lbl2_val.pack(padx=10, pady=(2, 10))

        self.card3 = ctk.CTkFrame(self)
        self.card3.grid(row=0, column=2, sticky='nsew', padx=10, pady=10)
        self.lbl3_title = ctk.CTkLabel(self.card3, text='Productos activos')
        self.lbl3_title.pack(padx=10, pady=(10, 2))
        self.lbl3_val = ctk.CTkLabel(self.card3, text='0', font=('', 24))
        self.lbl3_val.pack(padx=10, pady=(2, 10))

        self.chart1 = ChartWidget(self)
        self.chart1.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
        self.chart2 = ChartWidget(self)
        self.chart2.grid(row=1, column=1, sticky='nsew', padx=10, pady=5)
        self.chart3 = ChartWidget(self)
        self.chart3.grid(row=1, column=2, sticky='nsew', padx=10, pady=5)

        self.btn_refresh = ctk.CTkButton(self, text='Actualizar', command=self.refresh)
        self.btn_refresh.grid(row=2, column=0, columnspan=3, pady=10)

    def refresh(self):
        pass