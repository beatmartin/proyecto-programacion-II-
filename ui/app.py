import tkinter as tk
from tkinter import ttk
from ui.tab_operaciones import TabOperaciones
from ui.tab_vehiculos import TabVehiculos
from ui.tab_historial import TabHistorial
from ui.tab_reportes import TabReportes


# =============================================================================
# APLICACIÓN PRINCIPAL TKINTER
# =============================================================================

class EstacionamientoApp(tk.Tk):
    def __init__(
        self,
        vehiculo_service=None,
        estacionamiento_service=None,
        suscripcion_service=None,
    ):
        super().__init__()
        self.vehiculo_service = vehiculo_service
        self.estacionamiento_service = estacionamiento_service
        self.suscripcion_service = suscripcion_service

        self.title("Sistema de Gestión y Cobro de Estacionamiento")
        self.geometry("1040x680")
        self.minsize(920, 600)

        self._configurar_estilos()
        self._construir_interfaz()

    def _configurar_estilos(self):
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure("TFrame", background="#f4f6f8")
        style.configure("TLabelframe", background="#f4f6f8", font=("Segoe UI", 10, "bold"))
        style.configure("TLabelframe.Label", background="#f4f6f8", foreground="#1f2937")
        style.configure("TLabel", background="#f4f6f8", foreground="#1f2937", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), foreground="#0f172a")
        style.configure("Subheader.TLabel", font=("Segoe UI", 9), foreground="#475569")
        style.configure("CardTitle.TLabel", font=("Segoe UI", 9, "bold"), foreground="#475569", background="#ffffff")
        style.configure("CardValue.TLabel", font=("Segoe UI", 15, "bold"), foreground="#0f172a", background="#ffffff")
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", rowheight=26, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

    def _construir_interfaz(self):
        header_frame = ttk.Frame(self, padding=(16, 12, 16, 6))
        header_frame.pack(fill=tk.X)

        ttk.Label(
            header_frame,
            text="Gestión y Cobro de Estacionamiento",
            style="Header.TLabel",
        ).pack(anchor=tk.W)
        ttk.Label(
            header_frame,
            text="Control de ingresos, salidas, suscripciones mensuales y recaudación",
            style="Subheader.TLabel",
        ).pack(anchor=tk.W)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=14, pady=(6, 8))

        self.tab_operaciones = TabOperaciones(
            self.notebook,
            estacionamiento_service=self.estacionamiento_service,
            on_cambio_estado=self.refrescar_vistas,
        )
        self.tab_vehiculos = TabVehiculos(
            self.notebook,
            vehiculo_service=self.vehiculo_service,
            suscripcion_service=self.suscripcion_service,
            on_cambio_estado=self.refrescar_vistas,
        )
        self.tab_historial = TabHistorial(
            self.notebook,
            estacionamiento_service=self.estacionamiento_service,
        )
        self.tab_reportes = TabReportes(
            self.notebook,
            estacionamiento_service=self.estacionamiento_service,
        )

        self.notebook.add(self.tab_operaciones, text="  Operaciones (Ingreso / Salida)  ")
        self.notebook.add(self.tab_vehiculos, text="  Vehículos y Suscripciones  ")
        self.notebook.add(self.tab_historial, text="  Historial y Consultas  ")
        self.notebook.add(self.tab_reportes, text="  Reportes de Recaudación  ")

        self.notebook.bind("<<NotebookTabChanged>>", lambda _e: self.refrescar_vistas())

        self.status_var = tk.StringVar(value="Sistema listo.")
        status_bar = ttk.Label(
            self,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(10, 4),
            font=("Segoe UI", 9),
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.refrescar_vistas()

    def actualizar_estado(self, mensaje):
        self.status_var.set(mensaje)

    def refrescar_vistas(self):
        self.tab_operaciones.cargar_vehiculos_activos()
        self.tab_vehiculos.cargar_datos()
        self.tab_historial.aplicar_filtros()
        self.tab_reportes.generar_reporte()