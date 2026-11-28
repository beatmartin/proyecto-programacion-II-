from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from processing.filtros import filtrar_suscripciones_vigentes, _obtener_valor
from processing.reportes import _formatear_fecha_str, _formatear_clp


# =============================================================================
# PESTAÑA DE VEHÍCULOS Y SUSCRIPCIONES MENSUALES
# =============================================================================

class TabVehiculos(ttk.Frame):
    def __init__(
        self,
        parent,
        vehiculo_service=None,
        suscripcion_service=None,
        on_cambio_estado=None,
    ):
        super().__init__(parent, padding=12)
        self.vehiculo_service = vehiculo_service
        self.suscripcion_service = suscripcion_service
        self.on_cambio_estado = on_cambio_estado
        self._construir_widgets()

    def _construir_widgets(self):
        top_container = ttk.Frame(self)
        top_container.pack(fill=tk.X, pady=(0, 12))
        top_container.columnconfigure(0, weight=1)
        top_container.columnconfigure(1, weight=1)

        # --- Registro y Consulta de Vehículo ---
        frame_vehiculo = ttk.LabelFrame(top_container, text="Registrar / Consultar Vehículo", padding=12)
        frame_vehiculo.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        frame_vehiculo.columnconfigure(1, weight=1)

        ttk.Label(frame_vehiculo, text="Patente:").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.ent_patente = ttk.Entry(frame_vehiculo)
        self.ent_patente.grid(row=0, column=1, sticky="ew", padx=(8, 4), pady=4)
        ttk.Button(
            frame_vehiculo,
            text="Buscar",
            width=8,
            command=self._consultar_vehiculo,
        ).grid(row=0, column=2, pady=4)

        ttk.Label(frame_vehiculo, text="Responsable:").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.ent_responsable = ttk.Entry(frame_vehiculo)
        self.ent_responsable.grid(row=1, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=4)

        ttk.Label(frame_vehiculo, text="Contacto (Tel/Email):").grid(row=2, column=0, sticky=tk.W, pady=4)
        self.ent_contacto = ttk.Entry(frame_vehiculo)
        self.ent_contacto.grid(row=2, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=4)

        ttk.Button(
            frame_vehiculo,
            text="Guardar Vehículo",
            style="Accent.TButton",
            command=self._registrar_vehiculo,
        ).grid(row=3, column=0, columnspan=3, sticky="ew", pady=(10, 0))

        # --- Contratación de Suscripción Mensual ---
        frame_suscripcion = ttk.LabelFrame(
            top_container,
            text="Contratar Suscripción Mensual (30 días)",
            padding=12,
        )
        frame_suscripcion.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        frame_suscripcion.columnconfigure(1, weight=1)

        ttk.Label(frame_suscripcion, text="Patente Vehículo:").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.ent_patente_sus = ttk.Entry(frame_suscripcion)
        self.ent_patente_sus.grid(row=0, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=4)

        ttk.Label(frame_suscripcion, text="Fecha/Hora Inicio:").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.ent_inicio_sus = ttk.Entry(frame_suscripcion)
        self.ent_inicio_sus.grid(row=1, column=1, sticky="ew", padx=(8, 4), pady=4)
        ttk.Button(
            frame_suscripcion,
            text="Ahora",
            width=7,
            command=self._fijar_ahora_suscripcion,
        ).grid(row=1, column=2, pady=4)

        ttk.Label(
            frame_suscripcion,
            text="* Vigencia: 30 días consecutivos desde inicio (inclusive) hasta término (exclusive).",
            style="Subheader.TLabel",
        ).grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(4, 10))

        ttk.Button(
            frame_suscripcion,
            text="Contratar Suscripción y Registrar Pago",
            style="Accent.TButton",
            command=self._contratar_suscripcion,
        ).grid(row=3, column=0, columnspan=3, sticky="ew")

        self._fijar_ahora_suscripcion()

        # --- Tablas Inferiores (Vehículos y Suscripciones Vigentes) ---
        bottom_container = ttk.Frame(self)
        bottom_container.pack(fill=tk.BOTH, expand=True)
        bottom_container.columnconfigure(0, weight=1)
        bottom_container.columnconfigure(1, weight=1)
        bottom_container.rowconfigure(0, weight=1)

        frame_lista_veh = ttk.LabelFrame(bottom_container, text="Vehículos Registrados", padding=8)
        frame_lista_veh.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self.tree_vehiculos = ttk.Treeview(
            frame_lista_veh,
            columns=("patente", "responsable", "contacto"),
            show="headings",
        )
        self.tree_vehiculos.heading("patente", text="Patente")
        self.tree_vehiculos.heading("responsable", text="Responsable")
        self.tree_vehiculos.heading("contacto", text="Contacto")
        self.tree_vehiculos.column("patente", width=100, anchor=tk.CENTER)
        self.tree_vehiculos.column("responsable", width=160)
        self.tree_vehiculos.column("contacto", width=150)
        self.tree_vehiculos.pack(fill=tk.BOTH, expand=True)
        self.tree_vehiculos.bind("<<TreeviewSelect>>", self._seleccionar_vehiculo)

        frame_lista_sus = ttk.LabelFrame(bottom_container, text="Suscripciones Vigentes (Hoy)", padding=8)
        frame_lista_sus.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        self.tree_suscripciones = ttk.Treeview(
            frame_lista_sus,
            columns=("patente", "inicio", "termino", "monto"),
            show="headings",
        )
        self.tree_suscripciones.heading("patente", text="Patente")
        self.tree_suscripciones.heading("inicio", text="Inicio")
        self.tree_suscripciones.heading("termino", text="Término")
        self.tree_suscripciones.heading("monto", text="Monto")
        self.tree_suscripciones.column("patente", width=95, anchor=tk.CENTER)
        self.tree_suscripciones.column("inicio", width=125, anchor=tk.CENTER)
        self.tree_suscripciones.column("termino", width=125, anchor=tk.CENTER)
        self.tree_suscripciones.column("monto", width=95, anchor=tk.E)
        self.tree_suscripciones.pack(fill=tk.BOTH, expand=True)

    def _fijar_ahora_suscripcion(self):
        self.ent_inicio_sus.delete(0, tk.END)
        self.ent_inicio_sus.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def _seleccionar_vehiculo(self, _event):
        seleccion = self.tree_vehiculos.selection()
        if not seleccion:
            return
        valores = self.tree_vehiculos.item(seleccion[0], "values")
        if valores:
            self.ent_patente_sus.delete(0, tk.END)
            self.ent_patente_sus.insert(0, valores[0])

    def _registrar_vehiculo(self):
        if self.vehiculo_service is None:
            messagebox.showwarning("Servicio no conectado", "El servicio de vehículos aún no está inicializado.")
            return
        try:
            patente = self.ent_patente.get().strip().upper()
            responsable = self.ent_responsable.get().strip()
            contacto = self.ent_contacto.get().strip()

            self.vehiculo_service.registrar_vehiculo(
                patente=patente,
                responsable=responsable,
                contacto=contacto,
            )
            self.ent_patente.delete(0, tk.END)
            self.ent_responsable.delete(0, tk.END)
            self.ent_contacto.delete(0, tk.END)
            messagebox.showinfo("Vehículo Registrado", f"Vehículo {patente} guardado correctamente.")
            if self.on_cambio_estado:
                self.on_cambio_estado()
        except Exception as exc:
            messagebox.showerror("Error al registrar vehículo", str(exc))

    def _consultar_vehiculo(self):
        if self.vehiculo_service is None:
            return
        try:
            patente = self.ent_patente.get().strip().upper()
            vehiculo = self.vehiculo_service.buscar_por_patente(patente)
            if not vehiculo:
                messagebox.showinfo("Sin resultados", f"No existe un vehículo registrado con patente {patente}.")
                return
            resp = _obtener_valor(vehiculo, "responsable", default="-")
            cont = _obtener_valor(vehiculo, "contacto", default="-")
            self.ent_responsable.delete(0, tk.END)
            self.ent_responsable.insert(0, str(resp))
            self.ent_contacto.delete(0, tk.END)
            self.ent_contacto.insert(0, str(cont))
        except Exception as exc:
            messagebox.showerror("Error de búsqueda", str(exc))

    def _contratar_suscripcion(self):
        if self.suscripcion_service is None:
            messagebox.showwarning("Servicio no conectado", "El servicio de suscripciones aún no está inicializado.")
            return
        try:
            patente = self.ent_patente_sus.get().strip().upper()
            texto_fecha = self.ent_inicio_sus.get().strip()
            fecha_inicio = None
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
                try:
                    fecha_inicio = datetime.strptime(texto_fecha, fmt)
                    break
                except ValueError:
                    continue
            if fecha_inicio is None:
                raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD HH:MM o YYYY-MM-DD HH:MM:SS.")

            suscripcion = self.suscripcion_service.contratar_suscripcion(
                patente=patente,
                fecha_inicio=fecha_inicio,
            )
            termino = _formatear_fecha_str(_obtener_valor(suscripcion, "fecha_termino"))
            monto = _formatear_clp(_obtener_valor(suscripcion, "monto", default=0))
            self.ent_patente_sus.delete(0, tk.END)
            self._fijar_ahora_suscripcion()
            messagebox.showinfo(
                "Suscripción Contratada",
                f"Suscripción mensual activa para {patente}.\nVigente hasta: {termino}\nPago registrado: {monto}",
            )
            if self.on_cambio_estado:
                self.on_cambio_estado()
        except Exception as exc:
            messagebox.showerror("Error en suscripción", str(exc))

    def cargar_datos(self):
        for item in self.tree_vehiculos.get_children():
            self.tree_vehiculos.delete(item)
        for item in self.tree_suscripciones.get_children():
            self.tree_suscripciones.delete(item)

        if self.vehiculo_service is not None:
            try:
                for v in self.vehiculo_service.listar_vehiculos():
                    self.tree_vehiculos.insert(
                        "",
                        tk.END,
                        values=(
                            str(_obtener_valor(v, "patente", default="-")).upper(),
                            _obtener_valor(v, "responsable", default="-"),
                            _obtener_valor(v, "contacto", default="-"),
                        ),
                    )
            except Exception as exc:
                messagebox.showerror("Error", f"No se pudieron cargar vehículos: {exc}")

        if self.suscripcion_service is not None:
            try:
                todas = self.suscripcion_service.listar_suscripciones()
                vigentes = filtrar_suscripciones_vigentes(todas, datetime.now())
                for s in vigentes:
                    self.tree_suscripciones.insert(
                        "",
                        tk.END,
                        values=(
                            str(_obtener_valor(s, "patente", "vehiculo.patente", default="-")).upper(),
                            _formatear_fecha_str(_obtener_valor(s, "fecha_inicio")),
                            _formatear_fecha_str(_obtener_valor(s, "fecha_termino")),
                            _formatear_clp(_obtener_valor(s, "monto", default=0)),
                        ),
                    )
            except Exception as exc:
                messagebox.showerror("Error", f"No se pudieron cargar suscripciones: {exc}")