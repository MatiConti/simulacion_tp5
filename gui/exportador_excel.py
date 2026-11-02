"""Exportación del vector de estado (y las integraciones de Euler) a Excel."""
from __future__ import annotations

from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

from generador import PasoIntegracion
from models import FilaVectorEstado

from .columnas_vector import calcular_columnas, grupos_consecutivos

_RELLENO_ENCABEZADO = PatternFill("solid", fgColor="0B2545")
_FUENTE_ENCABEZADO = Font(bold=True, color="FFFFFF")


def _estilo_encabezado(celda) -> None:
    celda.fill = _RELLENO_ENCABEZADO
    celda.font = _FUENTE_ENCABEZADO
    celda.alignment = Alignment(horizontal="center")


def bytes_vector_estado(
    filas: list[FilaVectorEstado],
    integraciones: dict[int, list[PasoIntegracion]] | None = None,
) -> bytes:
    """Arma el Excel con las filas pedidas (las mismas que se ven en pantalla).

    Hoja 1: vector de estado con encabezado de dos niveles (objeto / atributo).
    Hoja 2: integraciones de Euler, identificadas por número de invitado.
    """
    libro = Workbook()
    hoja = libro.active
    hoja.title = "Vector de estado"

    columnas = calcular_columnas(filas)
    columna_excel = 1
    for grupo, cantidad in grupos_consecutivos(columnas):
        hoja.cell(row=1, column=columna_excel, value=grupo)
        if cantidad > 1:
            hoja.merge_cells(start_row=1, start_column=columna_excel, end_row=1, end_column=columna_excel + cantidad - 1)
        _estilo_encabezado(hoja.cell(row=1, column=columna_excel))
        columna_excel += cantidad
    for j, c in enumerate(columnas, start=1):
        _estilo_encabezado(hoja.cell(row=2, column=j, value=c.nombre))

    for f in filas:
        hoja.append([c.obtener(f) for c in columnas])
    hoja.freeze_panes = "A3"

    if integraciones:
        hoja_euler = libro.create_sheet("Integración Euler")
        hoja_euler.append(["Invitado", "P", "t", "D", "dD/dt", "D (t+h)"])
        for celda in hoja_euler[1]:
            _estilo_encabezado(celda)
        for invitado_id, pasos in sorted(integraciones.items()):
            for paso in pasos:
                hoja_euler.append([invitado_id, paso.derivada * 5, paso.t, paso.d, paso.derivada, paso.d_siguiente])
        hoja_euler.freeze_panes = "A2"

    buffer = BytesIO()
    libro.save(buffer)
    return buffer.getvalue()
