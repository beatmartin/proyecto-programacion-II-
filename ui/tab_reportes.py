from datetime import datetime, time
import tkinter as tk
from tkinter import ttk, messagebox
from processing.reportes import (
    calcular_resumen_recaudacion,
    generar_filas_desglose_recaudacion,
    _formatear_clp,
)


# =============================================================================
# PESTAÑA DE REPORTES DE RECAUDACIÓN
# =============================================================================

class TabReportes(ttk.Frame):
    def __init__(self, parent, estacionamiento_service=None):
        super().__init__(parent, padding=12)
        self.estacionamiento_service = estacionamiento_service
        self._construir_widgets()

    def _construir_widgets(self):
        # --- Filtro por Período ---
        frame_periodo = ttk.LabelFrame(self, text="Período de Recaudación (Fecha de Registro de Pago)", padding=10)
        frame_periodo.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(frame_periodo, text="Desde (YYYY-MM-DD):").grid(row=0, column=0, padx=(0, 6), pady=4)
        self.ent_desde = ttk.Entry(frame_periodo, width=15)
        self.ent_desde.grid(row=0, column=1, padx=(0, 14), pady=4)

        ttk.Label(frame_periodo, text="Hasta (YYYY-MM-DD):").grid(row=0, column=2, padx=(0, 6), pady=4)
        self.ent_hasta = ttk.Entry(frame_periodo, width=15)
        self.ent_hasta.grid(row=0, column=3, padx=(0, 14), pady=4)

        ttk.Button(
            frame_periodo,
            text="Calcular Recaudación",
            style="Accent.TButton",
            command=self.generar_reporte,
        ).grid(row=0, column=4, padx=(0, 8), pady=4)

        ttk.Button(
            frame_periodo,
            text="Todo el Historial",
            command=self._limpiar_periodo,
        ).grid(row=0, column=5, pady=4)

        # --- Tarjetas de Resumen ---
        cards_frame = ttk.Frame(self)
        cards_frame.pack(fill=tk.X, pady=(0, 12))
        for idx in range(4):
            cards_frame.columnconfigure(idx, weight=1)

        self.var_total = tk.StringVar(value="$0")
        self.var_minuto = tk.StringVar(value="$0")
        self.var_diaria = tk.StringVar(value="$0")
        self.var_mensual = tk.StringVar(value="$0")

        tarjetas = [
            ("TOTAL RECAUDADO", self.var_total),
            ("MODALIDAD POR MINUTO", self.var_minuto),
            ("MODALIDAD DIARIA", self.var_diaria),
            ("SUSCRIPCIONES MENSUALES", self.var_mensual),
        ]
        for idx, (titulo, variable) in enumerate(tarjetas):
            card = tk.Frame(cards_frame, bg="#ffffff", bd=1, relief=tk.SOLID, padx=14, pady=12)
            card.grid(row=0, column=idx, sticky="nsew", padx=(0 if idx == 0 else 6, 0))
            ttk.Label(card, text=titulo, style="CardTitle.TLabel").pack(anchor=tk.W)
            ttk.Label(card, textvariable=variable, style="CardValue.TLabel").pack(anchor=tk.W, pady=(6, 0))

        # --- Tabla de Distribución por Modalidad ---
        frame_desglose = ttk.LabelFrame(self, text="Distribución de Ingresos por Modalidad", padding=10)
        frame_desglose.pack(fill=tk.BOTH, expand=True)

        columnas = ("modalidad", "cantidad", "recaudado", "porcentaje")
        self.tree_reporte = ttk.Treeview(frame_desglose, columns=columnas, show="headings")
        self.tree_reporte.heading("modalidad", text="Modalidad de Pago")
        self.tree_reporte.heading("cantidad", text="Cantidad de Pagos")
        self.tree_reporte.heading("recaudado", text="Monto Recaudado (CLP)")
        self.tree_reporte.heading("porcentaje", text="Participación (%)")

        self.tree_reporte.column("modalidad", width=200, anchor=tk.W)
        self.tree_reporte.column("cantidad", width=150, anchor=tk.CENTER)
        self.tree_reporte.column("recaudado", width=180, anchor=tk.E)
        self.tree_reporte.column("porcentaje", width=150, anchor=tk.CENTER)

        self.tree_reporte.pack(fill=tk.BOTH, expand=True)

    def _limpiar_periodo(self):
        self.ent_desde.delete(0, tk.END)
        self.ent_hasta.delete(0, tk.END)
        self.generar_reporte()

    def generar_reporte(self):
        for item in self.tree_reporte.get_children():
            self.tree_reporte.delete(item)

        if self.estacionamiento_service is None:
            return

        try:
            desde_str = self.ent_desde.get().strip()
            hasta_str = self.ent_hasta.get().strip()

            fecha_inicio = (
                datetime.combine(datetime.strptime(desde_str, "%Y-%m-%d").date(), time.min)
                if desde_str
                else None
            )
            fecha_fin = (
                datetime.combine(datetime.strptime(hasta_str, "%Y-%m-%d").date(), time.max)
                if hasta_str
                else None
            )

            pagos = self.estacionamiento_service.listar_pagos()
            resumen = calcular_resumen_recaudacion(
                pagos,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
            )

            self.var_total.set(_formatear_clp(resumen["total"]))
            self.var_minuto.set(_formatear_clp(resumen["minuto"]))
            self.var_diaria.set(_formatear_clp(resumen["diaria"]))
            self.var_mensual.set(_formatear_clp(resumen["mensual"]))

            for fila in generar_filas_desglose_recaudacion(resumen):
                self.tree_reporte.insert("", tk.END, values=fila)
        except ValueError:
            messagebox.showerror("Fecha inválida", "Ingrese las fechas en formato YYYY-MM-DD.")
        except Exception as exc:
            messagebox.showerror("Error en reporte", str(exc))