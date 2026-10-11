
    def download_scienti(self):
        try:
            from tkinter import simpledialog, filedialog, messagebox
            from scraping import scienti
            url = simpledialog.askstring('SCIENTI', 'Ingrese la URL del grupo:')
            if not url:
                return
            datos = scienti.download_group(url)
            if not datos:
                raise Exception('Sin datos')
            for g in datos.get('grupos', []):
                try:
                    self.grupo_crud.crear(g)
                except Exception:
                    pass
            for i in datos.get('investigadores', []):
                try:
                    self.inv_crud.crear(i)
                except Exception:
                    pass
            for p in datos.get('productos', []):
                try:
                    self.prod_crud.crear(p)
                except Exception:
                    pass
            self.save_data()
            try:
                messagebox.showinfo('Éxito', 'Datos descargados')
            except Exception:
                pass
        except Exception:
            try:
                from tkinter import filedialog, messagebox
                path = filedialog.askopenfilename(filetypes=[('CSV', '*.csv')])
                if not path:
                    return
                from scraping import scienti
                datos = scienti.download_from_csv(path)
                if not datos:
                    return
                for g in datos.get('grupos', []):
                    try:
                        self.grupo_crud.crear(g)
                    except Exception:
                        pass
                for i in datos.get('investigadores', []):
                    try:
                        self.inv_crud.crear(i)
                    except Exception:
                        pass
                for p in datos.get('productos', []):
                    try:
                        self.prod_crud.crear(p)
                    except Exception:
                        pass
                self.save_data()
                try:
                    messagebox.showinfo('Éxito', 'Cargado desde CSV')
                except Exception:
                    pass
            except Exception:
                pass

    def load_csv(self):
        try:
            from tkinter import filedialog, messagebox
            path = filedialog.askopenfilename(filetypes=[('CSV', '*.csv')])
            if not path:
                return
            from scraping import scienti
            datos = scienti.download_from_csv(path)
            if not datos:
                return
            for g in datos.get('grupos', []):
                try:
                    self.grupo_crud.crear(g)
                except Exception:
                    pass
            for i in datos.get('investigadores', []):
                try:
                    self.inv_crud.crear(i)
                except Exception:
                    pass
            for p in datos.get('productos', []):
                try:
                    self.prod_crud.crear(p)
                except Exception:
                    pass
            self.save_data()
            try:
                messagebox.showinfo('Éxito', 'Cargado desde CSV')
            except Exception:
                pass
        except Exception:
            pass

    def about(self):
        try:
            from tkinter import messagebox
            messagebox.showinfo('Acerca de', 'PEA-i - Programa Estadístico de Análisis de Investigación')
        except Exception:
            pass

    def load_tabs_data(self):
        try:
            self.grupos_tab.refresh()
            self.investigadores_tab.refresh()
            self.productos_tab.refresh()
            self.estadisticas_tab.refresh()
        except Exception:
            pass