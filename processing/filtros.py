from datetime import datetime


# =============================================================================
# UTILIDADES INTERNAS DE LECTURA INMUTABLE
# =============================================================================

def _obtener_valor(registro, *claves, default=None):
    for clave in claves:
        actual = registro
        encontrado = True
        for parte in clave.split("."):
            if isinstance(actual, dict) and parte in actual:
                actual = actual[parte]
            elif hasattr(actual, parte):
                actual = getattr(actual, parte)
            else:
                encontrado = False
                break
        if encontrado and actual is not None:
            return actual
    return default


def _normalizar_fecha(valor):
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor
    if isinstance(valor, str):
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                return datetime.strptime(valor.strip(), fmt)
            except ValueError:
                continue
    return None


# =============================================================================
# FUNCIONES PURAS DE FILTRADO (FILTER + LAMBDA)
# =============================================================================

def filtrar_suscripciones_vigentes(suscripciones, fecha_referencia):
    if not isinstance(fecha_referencia, datetime):
        raise ValueError("fecha_referencia debe ser una instancia de datetime.")

    def _esta_vigente(suscripcion):
        inicio = _normalizar_fecha(_obtener_valor(suscripcion, "fecha_inicio"))
        termino = _normalizar_fecha(_obtener_valor(suscripcion, "fecha_termino"))
        if inicio is None or termino is None:
            return False
        return inicio <= fecha_referencia < termino

    return list(filter(lambda s: _esta_vigente(s), suscripciones))


def filtrar_historial_estadias(
    estadias,
    patente="",
    modalidad="Todas",
    fecha_inicio=None,
    fecha_fin=None,
):
    patente_norm = patente.strip().upper()
    modalidad_norm = modalidad.strip().lower()

    def _cumple_criterios(estadia):
        pat_reg = str(_obtener_valor(estadia, "patente", "vehiculo.patente", default="")).upper()
        mod_reg = str(_obtener_valor(estadia, "modalidad", "tipo_modalidad", default="")).lower()
        ingreso = _normalizar_fecha(_obtener_valor(estadia, "fecha_ingreso"))

        if patente_norm and patente_norm not in pat_reg:
            return False
        if modalidad_norm and modalidad_norm != "todas" and mod_reg != modalidad_norm:
            return False
        if fecha_inicio and (ingreso is None or ingreso < fecha_inicio):
            return False
        if fecha_fin and (ingreso is None or ingreso > fecha_fin):
            return False
        return True

    return list(filter(lambda e: _cumple_criterios(e), estadias))


def filtrar_pagos_por_periodo(
    pagos,
    patente="",
    modalidad="Todas",
    fecha_inicio=None,
    fecha_fin=None,
):
    patente_norm = patente.strip().upper()
    modalidad_norm = modalidad.strip().lower()

    def _cumple_pago(pago):
        pat_reg = str(
            _obtener_valor(
                pago,
                "patente",
                "estadia.patente",
                "estadia.vehiculo.patente",
                "suscripcion.patente",
                "suscripcion.vehiculo.patente",
                default="",
            )
        ).upper()
        mod_reg = str(_obtener_valor(pago, "modalidad", "tipo_modalidad", default="")).lower()
        fecha_pago = _normalizar_fecha(_obtener_valor(pago, "fecha_pago", "fecha_registro"))

        if patente_norm and patente_norm not in pat_reg:
            return False
        if modalidad_norm and modalidad_norm != "todas" and mod_reg != modalidad_norm:
            return False
        if fecha_inicio and (fecha_pago is None or fecha_pago < fecha_inicio):
            return False
        if fecha_fin and (fecha_pago is None or fecha_pago > fecha_fin):
            return False
        return True

    return list(filter(lambda p: _cumple_pago(p), pagos))