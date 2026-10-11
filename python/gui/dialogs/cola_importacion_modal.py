# -*- coding: utf-8 -*-
import threading, os
from typing import List
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from gui.styles import COLORS, RADIUS, SPACING, CONTROL_HEIGHT, font, button, entry, boton_primario, boton_secundario

class ColaImportacionModal(ctk.CTkToplevel):
    def __init__(self, parent, app_ref):
        super().__init__(parent)
        self._app = app_ref
        self._processing = False
        self._cancel_requested = False
        self.title('Cola de importacion - FIFO')
        self.geometry('640x560')
        self.minsize(580, 480)
        self.configure(fg_color=COLORS['bg'])
        self.transient(parent)
        self.grab_set()
        self.bind('<Escape>', lambda e: self._on_close())
        self.protocol('WM_DELETE_WINDOW', self._on_close)
        self._center_window(640, 560)
        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        self.card = ctk.CTkFrame(self, fg_color=COLORS['surface'], corner_radius=RADIUS['card'], border_width=1, border_color=COLORS['border'])
        self.card.pack(fill='both', expand=True, padx=SPACING['md'], pady=SPACING['md'])
        hdr = ctk.CTkFrame(self.card, fg_color='transparent')
        hdr.pack(fill='x', padx=SPACING['lg'], pady=(SPACING['lg'], SPACING['sm']))
        bar = ctk.CTkFrame(hdr, width=6, height=40, fg_color=COLORS['primary'], corner_radius=3)
        bar.pack(side='left', padx=(0, SPACING['md']))
        bar.pack_propagate(False)
        ht = ctk.CTkFrame(hdr, fg_color='transparent')
        ht.pack(side='left', fill='x', expand=True)
        ctk.CTkLabel(ht, text='Cola de importacion', font=font('heading'), text_color=COLORS['ink'], anchor='w').pack(fill='x', anchor='w')
        ctk.CTkLabel(ht, text='Orden FIFO - dequeue() en segundo plano', font=font('small'), text_color=COLORS['muted'], anchor='w').pack(fill='x', anchor='w')
        bf = ctk.CTkFrame(hdr, fg_color=COLORS['accent_soft'], corner_radius=RADIUS['badge'])
        bf.pack(side='right')
        self.badge_lbl = ctk.CTkLabel(bf, text='0 en cola', font=font('badge'), text_color=COLORS['primary'])
        self.badge_lbl.pack(padx=SPACING['sm'], pady=4)
        ctk.CTkFrame(self.card, height=1, fg_color=COLORS['border'], corner_radius=0).pack(fill='x', padx=SPACING['lg'], pady=(0, SPACING['sm']))
        af = ctk.CTkFrame(self.card, fg_color=COLORS['surface_alt'], corner_radius=8)
        af.pack(fill='x', padx=SPACING['lg'], pady=(0, SPACING['sm']))
        ai = ctk.CTkFrame(af, fg_color='transparent')
        ai.pack(fill='x', padx=SPACING['md'], pady=SPACING['sm'])
        ctk.CTkLabel(ai, text='Agregar a la cola:', font=font('body_bold'), text_color=COLORS['ink'], anchor='w').pack(fill='x', anchor='w', pady=(0, SPACING['xs']))
        ur = ctk.CTkFrame(ai, fg_color='transparent')
        ur.pack(fill='x', pady=(0, SPACING['xs']))
        self.url_entry = entry(ur, placeholder_text='https://scienti.minciencias.gov.co/gruplac/...', width=420)
        self.url_entry.pack(side='left', fill='x', expand=True, padx=(0, SPACING['xs']))
        self.url_entry.bind('<Return>', lambda e: self._enqueue_url())
        self.btn_add_url = boton_primario(ur, text='+ URL', command=self._enqueue_url, height=CONTROL_HEIGHT)
        self.btn_add_url.pack(side='left')
        cr = ctk.CTkFrame(ai, fg_color='transparent')
        cr.pack(fill='x')
        self.btn_add_csv = boton_secundario(cr, text='Agregar CSV/PDF...', command=self._enqueue_csv, height=CONTROL_HEIGHT)
        self.btn_add_csv.pack(side='left', padx=(0, SPACING['xs']))
        self.add_status_lbl = ctk.CTkLabel(cr, text='', font=font('small'), text_color=COLORS['success'], anchor='w')
        self.add_status_lbl.pack(side='left', fill='x', expand=True)
        lh = ctk.CTkFrame(self.card, fg_color='transparent')
        lh.pack(fill='x', padx=SPACING['lg'], pady=(SPACING['xs'], SPACING['xs']))
        ctk.CTkLabel(lh, text='Pendientes (FIFO):', font=font('small_bold'), text_color=COLORS['ink_soft'], anchor='w').pack(side='left', fill='x', expand=True)
        self.btn_clear_queue = button(lh, text='Vaciar cola', variant='danger', command=self._clear_queue, height=28)
        self.btn_clear_queue.pack(side='right')
        self.items_frame = ctk.CTkScrollableFrame(self.card, fg_color=COLORS['surface'], corner_radius=6, border_width=1, border_color=COLORS['border'], height=160)
        self.items_frame.pack(fill='both', expand=True, padx=SPACING['lg'], pady=(0, SPACING['sm']))
        pf = ctk.CTkFrame(self.card, fg_color='transparent')
        pf.pack(fill='x', padx=SPACING['lg'], pady=(0, SPACING['xs']))
        self.progress_lbl = ctk.CTkLabel(pf, text='', font=font('small'), text_color=COLORS['muted'], anchor='w')
        self.progress_lbl.pack(fill='x', anchor='w')
        self.progress_bar = ctk.CTkProgressBar(pf, mode='determinate', height=6, corner_radius=3, progress_color=COLORS['primary'], fg_color=COLORS['border'])
        self.progress_bar.set(0)
        acts = ctk.CTkFrame(self.card, fg_color='transparent')
        acts.pack(fill='x', padx=SPACING['lg'], pady=(0, SPACING['lg']))
        self.btn_process = boton_primario(acts, text='Procesar cola', command=self._start_processing, height=CONTROL_HEIGHT)
        self.btn_process.pack(side='left', padx=(0, SPACING['sm']))
        self.btn_cancel_proc = boton_secundario(acts, text='Cancelar', command=self._cancel_processing, height=CONTROL_HEIGHT)
        self.btn_cancel_proc.pack(side='left')
        self.btn_cancel_proc.configure(state='disabled')
        button(acts, text='Cerrar', variant='tertiary', command=self._on_close, height=CONTROL_HEIGHT).pack(side='right')

    def _enqueue_url(self):
        url = self.url_entry.get().strip()
        if not url:
            self._flash('Ingresa una URL primero.', COLORS['danger']); return
        if not (url.startswith('http://') or url.startswith('https://')):
            self._flash('La URL debe iniciar con http:// o https://', COLORS['danger']); return
        self._app.import_queue.enqueue({'tipo': 'url', 'valor': url, 'etiqueta': url[:60]})
        self.url_entry.delete(0, 'end')
        self._flash('URL agregada a la cola.', COLORS['success'])
        self._refresh_list(); self._app._refresh_status_bar()

    def _enqueue_csv(self):
        path = filedialog.askopenfilename(title='Seleccionar CSV o PDF',
            filetypes=[('Archivos', '*.csv;*.pdf'), ('CSV', '*.csv'), ('PDF', '*.pdf'), ('Todos', '*.*')], parent=self)
        if not path: return
        nombre = os.path.basename(path)
        self._app.import_queue.enqueue({'tipo': 'csv', 'valor': path, 'etiqueta': nombre})
        self._flash(nombre + ' agregado.', COLORS['success'])
        self._refresh_list(); self._app._refresh_status_bar()

    def _flash(self, msg, color=''):
        self.add_status_lbl.configure(text=msg, text_color=color or COLORS['muted'])
        self.after(3000, lambda: self.add_status_lbl.configure(text=''))

    def _refresh_list(self):
        for w in self.items_frame.winfo_children():
            w.destroy()
        queue = self._app.import_queue
        n = len(queue)
        self.badge_lbl.configure(text=str(n) + ' en cola')
        try:
            self.btn_clear_queue.configure(state='normal' if n > 0 else 'disabled')
            self.btn_process.configure(state='normal' if n > 0 and not self._processing else 'disabled')
        except Exception:
            pass
        if n == 0:
            ctk.CTkLabel(self.items_frame, text='La cola esta vacia. Agrega URLs o archivos CSV/PDF.',
                         font=font('small'), text_color=COLORS['muted'], anchor='center').pack(expand=True, pady=SPACING['lg'])
            return
        for idx, item in enumerate(queue, start=1):
            self._build_row(idx, item)

    def _build_row(self, idx, item):
        row = ctk.CTkFrame(self.items_frame, fg_color=COLORS['surface_alt'], corner_radius=6, border_width=1, border_color=COLORS['border_subtle'])
        row.pack(fill='x', pady=2, padx=2)
        pb = ctk.CTkFrame(row, width=26, height=26, fg_color=COLORS['primary'], corner_radius=13)
        pb.pack(side='left', padx=(SPACING['sm'], SPACING['xs']), pady=6)
        pb.pack_propagate(False)
        ctk.CTkLabel(pb, text=str(idx), font=font('badge'), text_color='#FFFFFF').place(relx=0.5, rely=0.5, anchor='center')
        tipo = item.get('tipo', 'url')
        ctk.CTkLabel(row, text='URL' if tipo == 'url' else 'CSV', font=font('badge'), text_color=COLORS['primary'], width=30).pack(side='left', padx=(0, SPACING['xs']))
        ctk.CTkLabel(row, text=item.get('etiqueta', item.get('valor', '')), font=font('small'), text_color=COLORS['ink_soft'], anchor='w').pack(side='left', fill='x', expand=True, padx=(0, SPACING['sm']))
        colors_map = {'url': (COLORS['accent_soft'], COLORS['primary']), 'csv': (COLORS['success_soft'], COLORS['success'])}
        bg, fg = colors_map.get(tipo, (COLORS['surface_subtle'], COLORS['muted']))
        badge = ctk.CTkFrame(row, fg_color=bg, corner_radius=RADIUS['badge'])
        badge.pack(side='right', padx=SPACING['sm'], pady=6)
        ctk.CTkLabel(badge, text=tipo.upper(), font=font('badge'), text_color=fg).pack(padx=SPACING['xs'], pady=2)

    def _start_processing(self):
        if self._processing or self._app.import_queue.is_empty(): return
        self._processing = True; self._cancel_requested = False
        self.btn_process.configure(state='disabled')
        self.btn_cancel_proc.configure(state='normal')
        self.btn_add_url.configure(state='disabled')
        self.btn_add_csv.configure(state='disabled')
        total = len(self._app.import_queue)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill='x', pady=(SPACING['xs'], 0))
        threading.Thread(target=self._process_worker, args=(total,), daemon=True).start()

    def _process_worker(self, total):
        exitosos = 0; fallidos = 0; detalle = []; procesado = 0
        while not self._app.import_queue.is_empty():
            if self._cancel_requested: break
            item = self._app.import_queue.dequeue()
            if item is None: break
            procesado += 1
            etiqueta = item.get('etiqueta', item.get('valor', ''))
            self.after(0, self._update_progress, procesado, total, etiqueta)
            tipo = item.get('tipo', 'url'); valor = item.get('valor', '')
            try:
                if tipo == 'url': self._process_url(valor)
                elif tipo == 'csv': self._process_csv(valor)
                exitosos += 1
            except Exception as exc:
                fallidos += 1; detalle.append(etiqueta + ': ' + str(exc))
            self.after(0, self._refresh_list)
            self.after(0, self._app._refresh_status_bar)
        self.after(0, self._on_done, exitosos, fallidos, detalle, procesado, self._cancel_requested)

    def _process_url(self, url):
        from scraping import scienti
        datos = scienti.download_group(url)
        if not datos or (isinstance(datos, dict) and 'error' in datos):
            err = datos.get('error', 'Error') if isinstance(datos, dict) else 'Sin datos'
            raise RuntimeError(err)
        done = threading.Event(); res = {}
        def _go():
            try: self._app.process_downloaded_data(datos); res['ok'] = True
            except Exception as e: res['error'] = str(e)
            finally: done.set()
        self.after(0, _go); done.wait(timeout=60)
        if 'error' in res: raise RuntimeError(res['error'])

    def _process_csv(self, path):
        done = threading.Event(); res = {}
        def _go():
            try: self._app.load_from_csv(path); res['ok'] = True
            except Exception as e: res['error'] = str(e)
            finally: done.set()
        self.after(0, _go); done.wait(timeout=30)
        if 'error' in res: raise RuntimeError(res['error'])

    def _update_progress(self, procesado, total, etiqueta):
        ratio = procesado / max(total, 1)
        self.progress_bar.set(ratio)
        self.progress_lbl.configure(text='Procesando ' + str(procesado) + ' de ' + str(total) + '...  ' + etiqueta[:48], text_color=COLORS['primary'])
        try:
            nq = len(self._app.import_queue)
            self._app.status_count_lbl.configure(text='Procesando ' + str(procesado) + ' de ' + str(total) + ' - Cola: ' + str(nq))
        except Exception:
            pass

    def _on_done(self, exitosos, fallidos, detalle, procesado, cancelado):
        self._processing = False
        nq = len(self._app.import_queue)
        self.btn_process.configure(state='normal' if nq > 0 else 'disabled')
        self.btn_cancel_proc.configure(state='disabled')
        self.btn_add_url.configure(state='normal'); self.btn_add_csv.configure(state='normal')
        self.progress_bar.set(1 if exitosos > 0 else 0)
        estado = 'cancelado' if cancelado else 'completado'
        self.progress_lbl.configure(
            text=('Cancelado: ' if cancelado else 'Completado: ') + str(exitosos) + ' exitosos, ' + str(fallidos) + ' fallidos.',
            text_color=COLORS['success'] if fallidos == 0 else COLORS['warning'])
        resumen = 'Procesamiento ' + estado + '.\n\nExitosos: ' + str(exitosos) + '\nFallidos: ' + str(fallidos)
        if detalle:
            resumen += '\n\nErrores:\n' + '\n'.join(detalle[:5])
            if len(detalle) > 5: resumen += '\n... y ' + str(len(detalle)-5) + ' mas.'
        self._refresh_list(); self._app._refresh_status_bar()
        messagebox.showinfo('Resultado de la cola', resumen, parent=self)

    def _cancel_processing(self):
        self._cancel_requested = True
        self.btn_cancel_proc.configure(state='disabled')
        self.progress_lbl.configure(text='Cancelando...', text_color=COLORS['warning'])

    def _clear_queue(self):
        if self._processing:
            messagebox.showwarning('En proceso', 'No puedes vaciar la cola mientras se esta procesando.', parent=self); return
        if not messagebox.askyesno('Vaciar cola', 'Deseas eliminar todos los elementos pendientes?', parent=self): return
        self._app.import_queue.clear()
        self._refresh_list(); self._app._refresh_status_bar()
        self.progress_lbl.configure(text=''); self.progress_bar.set(0)

    def _on_close(self):
        if self._processing:
            if not messagebox.askyesno('Cerrar', 'Importacion en curso. Cancelar y cerrar?', parent=self): return
            self._cancel_requested = True
        self.grab_release(); self.destroy()

    def _center_window(self, w, h):
        self.update_idletasks()
        try:
            px = self._app.winfo_x(); py = self._app.winfo_y()
            pw = self._app.winfo_width(); ph = self._app.winfo_height()
            x = px + max(0, (pw - w) // 2); y = py + max(0, (ph - h) // 2)
            self.geometry(str(w) + 'x' + str(h) + '+' + str(x) + '+' + str(y))
        except Exception:
            self.geometry(str(w) + 'x' + str(h))
