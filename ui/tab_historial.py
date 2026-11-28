from datetime import datetime, time
import tkinter as tk
from tkinter import ttk, messagebox
from processing.filtros import filtrar_historial_estadias, filtrar_pagos_por_periodo
from processing.reportes import formatear_filas_estadias, formatear_filas_pagos


# =============================================================================
# PESTAÑA DE HISTORIAL DE ESTADÍAS Y PAGOS
# =============================================================================

class TabHistorial(ttk.Frame):
    def __init__(self, parent, estacionamiento_service=None):
        super().__init__(parent, padding=12)
        self.estacionamiento_service = estacionamiento_service
        self._construir_widgets()

    def _construir_widgets(self):
        # --- Barra de Búsqueda y Filtros ---
        frame_filtros = ttk.LabelFrame(self, text="Filtros de Búsqueda", padding=10)
        frame_filtros.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame_filtros, text="Patente:").grid(row=0, column=0, padx=(0, 4), pady=4)
        self.ent_patente = ttk.Entry(frame_filtros, width=14)
        self.ent_patente.grid(row=0, column=1, padx=(0, 12), pady=4)

        ttk.Label(frame_filtros, text="Modalidad:").grid(row=0, column=2, padx=(0, 4), pady=4)
        self.cmb_modalidad = ttk.Combobox(
            frame_filtros,
            values=["Todas", "Minuto", "Diaria", "Mensual"],
            state="readonly",
            width=12,
        )
        self.cmb_modalidad.current(0)
        self.cmb_modalidad.grid(row=0, column=3, padx=(0, 12), pady=4)

        ttk.Label(frame_filtros, text="Desde (YYYY-MM-DD):").grid(row=0, column=4, padx=(0, 4), pady=4)
        self.ent_desde = ttk.Entry(frame_filtros, width=13)
        self.ent_desde.grid(row=0, column=5, padx=(0, 12), pady=4)

        ttk.Label(frame_filtros, text="Hasta (YYYY-MM-DD):").grid(row=0, column=6, padx=(0, 4), pady=4)
        self.ent_hasta = ttk.Entry(frame_filtros, width=13)
        self.ent_hasta.grid(row=0, column=7, padx=(0, 12), pady=4)

        ttk.Button(
            frame_filtros,
            text="Filtrar",
            style="Accent.TButton",
            command=self.aplicar_filtros,
        ).grid(row=0, column=8, padx=(0, 6), pady=4)

        ttk.Button(
            frame_filtros,
            text="Limpiar",
            command=self._limpiar_filtros,
        ).grid(row=0, column=9, pady=4)

        # --- Sub-pestañas para Estadías y Pagos ---
        sub_notebook = ttk.Notebook(self)
        sub_notebook.pack(fill=tk.BOTH, expand=True)

        frame_estadias = ttk.Frame(sub_notebook, padding=8)
        frame_pagos = ttk.Frame(sub_notebook, padding=8)

        sub_notebook.add(frame_estadias, text="  Historial de Estadías  ")
        sub_notebook.add(frame_pagos, text="  Historial de Pagos  ")

        cols_estadias = ("id", "patente", "ingreso", "salida", "modalidad", "estado", "monto")
        self.tree_estadias = ttk.Treeview(frame_estadias, columns=cols_estadias, show="headings")
        encabezados_est = {
            "id": ("ID", 50),
            "patente": ("Patente", 100),
            "ingreso": ("Ingreso", 145),
            "salida": ("Salida", 145),
            "modalidad": ("Modalidad", 105),
            "estado": ("Estado", 95),
            "monto": ("Cobro Estadía", 110),
        }
        for col, (texto, ancho) in encabezados_est.items():
            self.tree_estadias.heading(col, text=texto)
            self.tree_estadias.column(col, width=ancho, anchor=tk.CENTER)

        scroll_est = ttk.Scrollbar(frame_estadias, orient=tk.VERTICAL, command=self.tree_estadias.yview)
        self.tree_estadias.configure(yscrollcommand=scroll_est.set)
        self.tree_estadias.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_est.pack(side=tk.RIGHT, fill=tk.Y)

        cols_pagos = ("id", "fecha_pago", "patente", "origen", "modalidad", "monto")
        self.tree_pagos = ttk.Treeview(frame_pagos, columns=cols_pagos, show="headings")
        encabezados_pag = {
            "id": ("ID", 50),
            "fecha_pago": ("Fecha Registro Pago", 160),
            "patente": ("Patente", 110),
            "origen": ("Concepto", 120),
            "modalidad": ("Modalidad", 115),
            "monto": ("Monto Pagado", 120),
        }
        for col, (texto, ancho) in encabezados_pag.items():
            self.tree_pagos.heading(col, text=texto)
            self.tree_pagos.column(col, width=ancho, anchor=tk.CENTER)

        scroll_pag = ttk.Scrollbar(frame_pagos, orient=tk.VERTICAL, command=self.tree_pagos.yview)
        self.tree_pagos.configure(yscrollcommand=scroll_pag.set)
        self.tree_pagos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_pag.pack(side=tk.RIGHT, fill=tk.Y)

    def _parsear_rango_fechas(self):
        desde_str = self.ent_desde.get().strip()
        hasta_str = self.ent_hasta.get().strip()
        fecha_inicio = None
        fecha_fin = None

        if desde_str:
            fecha_inicio = datetime.combine(
                datetime.strptime(desde_str, "%Y-%m-%d").date(),
                time.min,
            )
        if hasta_str:
            fecha_fin = datetime.combine(
                datetime.strptime(hasta_str, "%Y-%m-%d").date(),
                time.max,
            )
        return fecha_inicio, fecha_fin

    def _limpiar_filtros(self):
        self.ent_patente.delete(0, tk.END)
        self.cmb_modalidad.current(0)
        self.ent_desde.delete(0, tk.END)
        self.ent_hasta.delete(0, tk.END)
        self.aplicar_filtros()

    def aplicar_filtros(self):
        for item in self.tree_estadias.get_children():
            self.tree_estadias.delete(item)
        for item in self.tree_pagos.get_children():
            self.tree_pagos.delete(item)

        if self.estacionamiento_service is None:
            return

        try:
            fecha_inicio, fecha_fin = self._parsear_rango_fechas()
            patente = self.ent_patente.get()
            modalidad = self.cmb_modalidad.get()

            estadias = self.estacionamiento_service.listar_historial_estadias()
            estadias_filtradas = filtrar_historial_estadias(
                estadias,
                patente=patente,
                modalidad=modalidad,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
            )
            for fila in formatear_filas_estadias(estadias_filtradas):
                self.tree_estadias.insert("", tk.END, values=fila)

            pagos = self.estacionamiento_service.listar_pagos()
            pagos_filtrados = filtrar_pagos_por_periodo(
                pagos,
                patente=patente,
                modalidad=modalidad,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
            )
            for fila in formatear_filas_pagos(pagos_filtrados):
                self.tree_pagos.insert("", tk.END, values=fila)
        except ValueError:
            messagebox.showerror("Fecha inválida", "Las fechas de filtro deben tener formato YYYY-MM-DD.")
        except Exception as exc:
            messagebox.showerror("Error al consultar historial", str(exc))