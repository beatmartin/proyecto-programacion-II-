from functools import reduce
from processing.filtros import (
    _obtener_valor,
    _normalizar_fecha,
    filtrar_pagos_por_periodo,
)


# =============================================================================
# FORMATEO FUNCIONAL PARA TABLAS (MAP + LAMBDA)
# =============================================================================

def _formatear_fecha_str(valor):
    fecha = _normalizar_fecha(valor)
    return fecha.strftime("%Y-%m-%d %H:%M") if fecha else "-"


def _formatear_clp(monto):
    valor = int(round(float(monto or 0)))
    return f"${valor:,}".replace(",", ".")


def formatear_filas_vehiculos_activos(estadias_activas):
    return list(
        map(
            lambda e: (
                str(_obtener_valor(e, "patente", "vehiculo.patente", default="-")).upper(),
                _formatear_fecha_str(_obtener_valor(e, "fecha_ingreso")),
                str(_obtener_valor(e, "modalidad", "tipo_modalidad", default="-")).capitalize(),
            ),
            estadias_activas,
        )
    )


def formatear_filas_estadias(estadias):
    estadias_ordenadas = sorted(
        estadias,
        key=lambda e: _normalizar_fecha(_obtener_valor(e, "fecha_ingreso")) or _normalizar_fecha("1970-01-01"),
        reverse=True,
    )
    return list(
        map(
            lambda e: (
                _obtener_valor(e, "id", default="-"),
                str(_obtener_valor(e, "patente", "vehiculo.patente", default="-")).upper(),
                _formatear_fecha_str(_obtener_valor(e, "fecha_ingreso")),
                _formatear_fecha_str(_obtener_valor(e, "fecha_salida")),
                str(_obtener_valor(e, "modalidad", "tipo_modalidad", default="-")).capitalize(),
                "Activa" if _obtener_valor(e, "fecha_salida") is None else "Finalizada",
                _formatear_clp(_obtener_valor(e, "monto", "monto_cobrado", "pago.monto", default=0)),
            ),
            estadias_ordenadas,
        )
    )


def formatear_filas_pagos(pagos):
    pagos_ordenados = sorted(
        pagos,
        key=lambda p: _normalizar_fecha(_obtener_valor(p, "fecha_pago", "fecha_registro")) or _normalizar_fecha("1970-01-01"),
        reverse=True,
    )
    return list(
        map(
            lambda p: (
                _obtener_valor(p, "id", default="-"),
                _formatear_fecha_str(_obtener_valor(p, "fecha_pago", "fecha_registro")),
                str(
                    _obtener_valor(
                        p,
                        "patente",
                        "estadia.patente",
                        "estadia.vehiculo.patente",
                        "suscripcion.patente",
                        "suscripcion.vehiculo.patente",
                        default="-",
                    )
                ).upper(),
                "Suscripción" if _obtener_valor(p, "suscripcion_id", "suscripcion") is not None else "Estadía",
                str(_obtener_valor(p, "modalidad", "tipo_modalidad", default="-")).capitalize(),
                _formatear_clp(_obtener_valor(p, "monto", default=0)),
            ),
            pagos_ordenados,
        )
    )


# =============================================================================
# CÁLCULO FUNCIONAL DE RECAUDACIÓN (FILTER + REDUCE + LAMBDA)
# =============================================================================

def calcular_resumen_recaudacion(pagos, fecha_inicio=None, fecha_fin=None):
    pagos_periodo = filtrar_pagos_por_periodo(
        pagos,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )

    def _sumar_montos(coleccion):
        return reduce(
            lambda acc, p: acc + int(round(float(_obtener_valor(p, "monto", default=0)))),
            coleccion,
            0,
        )

    pagos_minuto = list(
        filter(
            lambda p: str(_obtener_valor(p, "modalidad", "tipo_modalidad", default="")).lower() in ("minuto", "por minuto"),
            pagos_periodo,
        )
    )
    pagos_diaria = list(
        filter(
            lambda p: str(_obtener_valor(p, "modalidad", "tipo_modalidad", default="")).lower() == "diaria",
            pagos_periodo,
        )
    )
    pagos_mensual = list(
        filter(
            lambda p: str(_obtener_valor(p, "modalidad", "tipo_modalidad", default="")).lower() == "mensual",
            pagos_periodo,
        )
    )

    total_general = _sumar_montos(pagos_periodo)
    total_minuto = _sumar_montos(pagos_minuto)
    total_diaria = _sumar_montos(pagos_diaria)
    total_mensual = _sumar_montos(pagos_mensual)

    return {
        "total": total_general,
        "minuto": total_minuto,
        "diaria": total_diaria,
        "mensual": total_mensual,
        "cantidad_total": len(pagos_periodo),
        "cantidad_minuto": len(pagos_minuto),
        "cantidad_diaria": len(pagos_diaria),
        "cantidad_mensual": len(pagos_mensual),
    }


def generar_filas_desglose_recaudacion(resumen):
    total = resumen.get("total", 0)
    categorias = [
        ("Por minuto", resumen.get("cantidad_minuto", 0), resumen.get("minuto", 0)),
        ("Diaria", resumen.get("cantidad_diaria", 0), resumen.get("diaria", 0)),
        ("Mensual", resumen.get("cantidad_mensual", 0), resumen.get("mensual", 0)),
    ]
    return list(
        map(
            lambda item: (
                item[0],
                item[1],
                _formatear_clp(item[2]),
                f"{(item[2] / total * 100):.1f}%" if total > 0 else "0.0%",
            ),
            categorias,
        )
    )