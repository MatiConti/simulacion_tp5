"""Definición de las columnas del vector de estado.

La usan tanto la tabla de la interfaz como la exportación a Excel, para que
las dos muestren exactamente lo mismo. Cada columna tiene un grupo (encabezado
de primer nivel: evento, objeto o acumuladores), un nombre (segundo nivel) y
una función que saca el valor de una fila.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from models import FilaVectorEstado

# Formato de cada columna: "rnd" (4 decimales), "num" (2 decimales), "txt"
_RND, _NUM, _TXT = "rnd", "num", "txt"


@dataclass(frozen=True)
class Columna:
    grupo: str
    nombre: str
    obtener: Callable[[FilaVectorEstado], Any]
    formato: str = _TXT


def _campo(seccion: str, clave: str) -> Callable[[FilaVectorEstado], Any]:
    return lambda f: getattr(f, seccion).get(clave)


def _campo_de(seccion: str, id_objeto: int, clave: str) -> Callable[[FilaVectorEstado], Any]:
    def obtener(f: FilaVectorEstado) -> Any:
        info = getattr(f, seccion).get(id_objeto)
        return info.get(clave) if info else None

    return obtener


_COLUMNAS_INVITADO = [
    ("tipo", "Tipo", _TXT),
    ("estado", "Estado", _TXT),
    ("hora_llegada", "Hora llegada", _NUM),
    ("p", "P", _TXT),
    ("fin_estacionamiento", "Fin estacionam.", _NUM),
    ("hora_inicio_sala", "Ingreso sala", _NUM),
    ("rnd_sala", "RND perm. sala", _RND),
    ("tiempo_sala", "Perm. sala", _NUM),
    ("fin_sala", "Fin perm. sala", _NUM),
    ("hora_llegada_cola_entrevista", "Llegada cola entrev.", _NUM),
    ("limite_espera", "Límite espera (abandono)", _NUM),
]


def calcular_columnas(filas: list[FilaVectorEstado]) -> list[Columna]:
    ids_operarios = sorted({i for f in filas for i in f.operarios})
    ids_representantes = sorted({i for f in filas for i in f.representantes})
    ids_invitados = sorted({i for f in filas for i in f.invitados})

    columnas = [
        Columna("Evento", "Fila", lambda f: f.numero_fila),
        Columna("Evento", "Reloj", lambda f: f.hora_simulada, _NUM),
        Columna("Evento", "Evento", lambda f: f.nombre_evento),
        Columna("Evento", "Invitado", lambda f: f.invitado_evento_id),
        Columna("Evento", "Próximo evento", lambda f: f.proximo_evento),
        Columna("Llegada invitado con auto", "RND", _campo("llegada_auto", "rnd"), _RND),
        Columna("Llegada invitado con auto", "Entre llegadas", _campo("llegada_auto", "tiempo"), _NUM),
        Columna("Llegada invitado con auto", "Próxima llegada", _campo("llegada_auto", "proxima"), _NUM),
        Columna("Llegada invitado peatón", "Próxima llegada", _campo("llegada_peaton", "proxima"), _NUM),
    ]
    for i in ids_operarios:
        grupo = f"Operario {i}"
        columnas += [
            Columna(grupo, "Estado", _campo_de("operarios", i, "estado")),
            Columna(grupo, "Invitado", _campo_de("operarios", i, "invitado")),
            Columna(grupo, "RND", _campo_de("operarios", i, "rnd"), _RND),
            Columna(grupo, "T. acreditación", _campo_de("operarios", i, "tiempo"), _NUM),
            Columna(grupo, "Fin acreditación", _campo_de("operarios", i, "fin"), _NUM),
            Columna(grupo, "Ocio acum.", _campo_de("operarios", i, "ocio"), _NUM),
        ]
    for i in ids_representantes:
        grupo = f"Representante {i}"
        columnas += [
            Columna(grupo, "Estado", _campo_de("representantes", i, "estado")),
            Columna(grupo, "Invitado", _campo_de("representantes", i, "invitado")),
            Columna(grupo, "Duración entrev. (Euler)", _campo_de("representantes", i, "duracion"), _NUM),
            Columna(grupo, "Fin entrevista", _campo_de("representantes", i, "fin"), _NUM),
        ]
    columnas += [
        Columna("Colas", "Acreditación", _campo("colas", "acreditacion")),
        Columna("Colas", "Entrevista", _campo("colas", "entrevista")),
        Columna("Acumuladores", "Máx. tiempo en sala", _campo("acumuladores", "maximo_tiempo_en_sala"), _NUM),
        Columna("Acumuladores", "Llegados a entrevista", _campo("acumuladores", "cantidad_invitados_a_entrevista")),
        Columna("Acumuladores", "Con encuesta", _campo("acumuladores", "cantidad_entrevistas_completas")),
        Columna("Acumuladores", "Sin encuesta", _campo("acumuladores", "cantidad_abandonos_entrevista")),
        Columna("Acumuladores", "% sin encuesta", _campo("acumuladores", "porcentaje_abandono_entrevista"), _NUM),
        Columna("Acumuladores", "Ocio total operarios", _campo("acumuladores", "ocio_total_operarios"), _NUM),
    ]
    for i in ids_invitados:
        grupo = f"Invitado {i}"
        columnas += [Columna(grupo, nombre, _campo_de("invitados", i, clave), fmt) for clave, nombre, fmt in _COLUMNAS_INVITADO]
    return columnas


def texto_celda(columna: Columna, fila: FilaVectorEstado) -> str:
    valor = columna.obtener(fila)
    if valor is None:
        return ""
    if columna.formato == _RND:
        return f"{valor:.4f}"
    if columna.formato == _NUM:
        return f"{valor:.2f}"
    return str(valor)


def grupos_consecutivos(columnas: list[Columna]) -> list[tuple[str, int]]:
    """Agrupa columnas contiguas del mismo grupo: [(grupo, cantidad), ...]."""
    grupos: list[tuple[str, int]] = []
    for c in columnas:
        if grupos and grupos[-1][0] == c.grupo:
            grupos[-1] = (c.grupo, grupos[-1][1] + 1)
        else:
            grupos.append((c.grupo, 1))
    return grupos
