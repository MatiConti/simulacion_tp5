"""Exportación del vector de estado a una planilla Excel."""
from __future__ import annotations

from io import BytesIO

from openpyxl import Workbook

from models import FilaVectorEstado


def bytes_vector_estado(filas: list[FilaVectorEstado]) -> bytes:
    libro = Workbook()
    hoja = libro.active
    hoja.title = "Vector de estado"

    ids_operarios = sorted({oid for f in filas for oid in f.operarios})
    ids_representantes = sorted({rid for f in filas for rid in f.representantes})
    ids_invitados = sorted({iid for f in filas for iid in f.invitados})
    claves_rnd = sorted({k for f in filas for k in f.numeros_aleatorios})

    encabezados = ["Fila", "Hora", "Evento", "Próximos eventos"]
    encabezados += [f"Operario {i}" for i in ids_operarios]
    encabezados += [f"Representante {i}" for i in ids_representantes]
    encabezados += [f"Invitado {i}" for i in ids_invitados]
    encabezados += [f"RND {k}" for k in claves_rnd]
    hoja.append(encabezados)

    for f in filas:
        fila_excel = [f.numero_fila, f.hora_simulada, f.nombre_evento, "; ".join(f.proximos_eventos)]
        fila_excel += [_estado_servidor(f.operarios.get(i)) for i in ids_operarios]
        fila_excel += [_estado_servidor(f.representantes.get(i)) for i in ids_representantes]
        fila_excel += [f.invitados.get(i, {}).get("estado", "") for i in ids_invitados]
        fila_excel += [f.numeros_aleatorios.get(k, "") for k in claves_rnd]
        hoja.append(fila_excel)

    buffer = BytesIO()
    libro.save(buffer)
    return buffer.getvalue()


def _estado_servidor(info: dict | None) -> str:
    if info is None:
        return ""
    return "ocupado" if info["ocupado"] else "libre"
