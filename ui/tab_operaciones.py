from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from processing.reportes import formatear_filas_vehiculos_activos, _formatear_clp


# =============================================================================
# PESTAÑA DE OPERACIONES (INGRESO, SALIDA Y VEHÍCULOS DENTRO)
# =============================================================================

class TabOperaciones(ttk.Frame):
    def __init__(self, parent, estacionamiento_service=None, on_cambio_estado=None):
        super().__init__(parent, padding=12)
        self.estacionamiento_service = estacionamiento_service
        self.on_cambio_estado = on_cambio_estado
        self._construir_widgets()

    def _construir_widgets(self):
        top_container = ttk.Frame(self)
        top_container.pack(fill=tk.X, pady=(0, 12))
        top_container.columnconfigure(0, weight=1)
        top_container.columnconfigure(1, weight=1)

        # --- Formulario de Ingreso ---
        frame_ingreso = ttk.LabelFrame(top_container, text="Registrar Ingreso de Vehículo", padding=12)
        frame_ingreso.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        frame_ingreso.columnconfigure(1, weight=1)

        ttk.Label(frame_ingreso, text="Patente:").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.ent_patente_ingreso = ttk.Entry(frame_ingreso)
        self.ent_patente_ingreso.grid(row=0, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=4)

        ttk.Label(frame_ingreso, text="Modalidad:").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.cmb_modalidad = ttk.Combobox(
            frame_ingreso,
            values=["Por minuto", "Diaria"],
            state="readonly",
        )
        self.cmb_modalidad.current(0)
        self.cmb_modalidad.grid(row=1, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=4)

        ttk.Label(frame_ingreso, text="Fecha/Hora Ingreso:").grid(row=2, column=0, sticky=tk.W, pady=4)
        self.ent_fecha_ingreso = ttk.Entry(frame_ingreso)
        self.ent_fecha_ingreso.grid(row=2, column=1, sticky="ew", padx=(8, 4), pady=4)
        ttk.Button(
            frame_ingreso,
            text="Ahora",
            width=7,
            command=lambda: self._fijar_ahora(self.ent_fecha_ingreso),
        ).grid(row=2, column=2, pady=4)

        ttk.Label(
            frame_ingreso,
            text="* Si posee suscripción mensual vigente, se aplicará automáticamente.",
            style="Subheader.TLabel",
        ).grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(4, 8))

        ttk.Button(
            frame_ingreso,
            text="Registrar Ingreso",
            style="Accent.TButton",
            command=self._registrar_ingreso,
        ).grid(row=4, column=0, columnspan=3, sticky="ew")

        # --- Formulario de Salida ---
        frame_salida = ttk.LabelFrame(top_container, text="Registrar Salida y Cobro", padding=12)
        frame_salida.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        frame_salida.columnconfigure(1, weight=1)

        ttk.Label(frame_salida, text="Patente:").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.ent_patente_salida = ttk.Entry(frame_salida)
        self.ent_patente_salida.grid(row=0, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=4)

        ttk.Label(frame_salida, text="Fecha/Hora Salida:").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.ent_fecha_salida = ttk.Entry(frame_salida)
        self.ent_fecha_salida.grid(row=1, column=1, sticky="ew", padx=(8, 4), pady=4)
        ttk.Button(
            frame_salida,
            text="Ahora",
            width=7,
            command=lambda: self._fijar_ahora(self.ent_fecha_salida),
        ).grid(row=1, column=2, pady=4)

        self.lbl_resultado_salida = ttk.Label(
            frame_salida,
            text="Seleccione un vehículo de la tabla o ingrese su patente.",
            style="Subheader.TLabel",
        )
        self.lbl_resultado_salida.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(10, 14))

        ttk.Button(
            frame_salida,
            text="Finalizar Estadía y Cobrar",
            style="Accent.TButton",
            command=self._registrar_salida,
        ).grid(row=4, column=0, columnspan=3, sticky="ew")

        self._fijar_ahora(self.ent_fecha_ingreso)
        self._fijar_ahora(self.ent_fecha_salida)

        # --- Tabla de Vehículos Dentro ---
        frame_tabla = ttk.LabelFrame(self, text="Vehículos Actualmente en el Estacionamiento", padding=10)
        frame_tabla.pack(fill=tk.BOTH, expand=True)

        columnas = ("patente", "fecha_ingreso", "modalidad")
        self.tree_activos = ttk.Treeview(frame_tabla, columns=columnas, show="headings")
        self.tree_activos.heading("patente", text="Patente")
        self.tree_activos.heading("fecha_ingreso", text="Fecha y Hora de Ingreso")
        self.tree_activos.heading("modalidad", text="Modalidad Asignada")

        self.tree_activos.column("patente", width=160, anchor=tk.CENTER)
        self.tree_activos.column("fecha_ingreso", width=220, anchor=tk.CENTER)
        self.tree_activos.column("modalidad", width=180, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tree_activos.yview)
        self.tree_activos.configure(yscrollcommand=scrollbar.set)

        self.tree_activos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_activos.bind("<<TreeviewSelect>>", self._al_seleccionar_fila)

    def _fijar_ahora(self, entry_widget):
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def _parsear_fecha(self, texto):
        valor = texto.strip()
        if not valor:
            return datetime.now()
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
            try:
                return datetime.strptime(valor, fmt)
            except ValueError:
                continue
        raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD HH:MM o YYYY-MM-DD HH:MM:SS.")

    def _al_seleccionar_fila(self, _event):
        seleccion = self.tree_activos.selection()
        if not seleccion:
            return
        valores = self.tree_activos.item(seleccion[0], "values")
        if valores:
            self.ent_patente_salida.delete(0, tk.END)
            self.ent_patente_salida.insert(0, valores[0])
            self._fijar_ahora(self.ent_fecha_salida)

    def _registrar_ingreso(self):
        if self.estacionamiento_service is None:
            messagebox.showwarning("Servicio no conectado", "El servicio de estacionamiento aún no está inicializado.")
            return
        try:
            patente = self.ent_patente_ingreso.get().strip().upper()
            modalidad_ui = self.cmb_modalidad.get().strip().lower()
            modalidad = "minuto" if "minuto" in modalidad_ui else "diaria"
            fecha_ingreso = self._parsear_fecha(self.ent_fecha_ingreso.get())

            estadia = self.estacionamiento_service.registrar_ingreso(
                patente=patente,
                modalidad=modalidad,
                fecha_ingreso=fecha_ingreso,
            )
            mod_final = getattr(estadia, "modalidad", modalidad)
            self.ent_patente_ingreso.delete(0, tk.END)
            self._fijar_ahora(self.ent_fecha_ingreso)
            messagebox.showinfo(
                "Ingreso Registrado",
                f"Vehículo {patente} ingresado correctamente.\nModalidad aplicada: {str(mod_final).capitalize()}",
            )
            if self.on_cambio_estado:
                self.on_cambio_estado()
        except Exception as exc:
            messagebox.showerror("Error al registrar ingreso", str(exc))

    def _registrar_salida(self):
        if self.estacionamiento_service is None:
            messagebox.showwarning("Servicio no conectado", "El servicio de estacionamiento aún no está inicializado.")
            return
        try:
            patente = self.ent_patente_salida.get().strip().upper()
            fecha_salida = self._parsear_fecha(self.ent_fecha_salida.get())

            resultado = self.estacionamiento_service.registrar_salida(
                patente=patente,
                fecha_salida=fecha_salida,
            )
            monto = resultado.get("monto", 0) if isinstance(resultado, dict) else getattr(resultado, "monto", 0)
            duracion = resultado.get("duracion", "-") if isinstance(resultado, dict) else "-"
            modalidad = resultado.get("modalidad", "-") if isinstance(resultado, dict) else "-"

            resumen_texto = (
                f"Salida {patente} | Modalidad: {str(modalidad).capitalize()} | "
                f"Duración: {duracion} | Total cobrado: {_formatear_clp(monto)}"
            )
            self.lbl_resultado_salida.config(text=resumen_texto)
            self.ent_patente_salida.delete(0, tk.END)
            messagebox.showinfo("Salida Registrada", resumen_texto)
            if self.on_cambio_estado:
                self.on_cambio_estado()
        except Exception as exc:
            messagebox.showerror("Error al registrar salida", str(exc))

    def cargar_vehiculos_activos(self):
        for item in self.tree_activos.get_children():
            self.tree_activos.delete(item)
        if self.estacionamiento_service is None:
            return
        try:
            activos = self.estacionamiento_service.listar_vehiculos_dentro()
            for fila in formatear_filas_vehiculos_activos(activos):
                self.tree_activos.insert("", tk.END, values=fila)
        except Exception as exc:
            messagebox.showerror("Error de consulta", f"No se pudieron cargar los vehículos dentro: {exc}")