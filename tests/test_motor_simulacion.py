import time

import pytest

from models import TipoInvitado
from simulacion import MotorSimulacion, ParametrosSimulacion


def _simular(**kwargs) -> MotorSimulacion:
    motor = MotorSimulacion(ParametrosSimulacion(**kwargs))
    motor.ejecutar()
    return motor


def test_p_se_toma_de_los_parametros():
    motor = _simular(p_con_auto=40, p_peaton=25)
    for invitado in motor.invitados.values():
        esperado = 40 if invitado.tipo is TipoInvitado.CON_AUTO else 25
        assert invitado.p == esperado


def test_entrevista_dura_50_min_por_defecto_para_ambos_tipos():
    motor = _simular()
    duraciones = {
        inv.tipo: inv.hora_fin_entrevista - inv.hora_inicio_entrevista
        for inv in motor.invitados.values()
        if inv.hora_fin_entrevista is not None
    }
    assert set(duraciones) == {TipoInvitado.CON_AUTO, TipoInvitado.PEATON}
    for duracion in duraciones.values():
        assert duracion == pytest.approx(50.0)


def test_ultima_fila_es_la_del_instante_x():
    motor = _simular(tiempo_max=300)
    final = motor.filas[-1]
    assert motor.motivo_corte == "tiempo_max"
    assert final.es_fila_final
    assert final.hora_simulada == 300
    assert all(f.hora_simulada <= 300 for f in motor.filas)


def test_corta_por_iteraciones():
    motor = _simular(tiempo_max=10**9, iteraciones_max=500)
    assert motor.motivo_corte == "iteraciones_max"
    assert motor.filas[-1].numero_fila == 500
    assert motor.filas[-1].es_fila_final


def test_ocio_cerrado_en_x_y_acotado():
    motor = _simular(tiempo_max=480)
    for operario in motor.operarios:
        assert 0 <= operario.tiempo_ocioso_acumulado <= 480
    assert motor.filas[-1].acumuladores["ocio_total_operarios"] == pytest.approx(
        sum(o.tiempo_ocioso_acumulado for o in motor.operarios)
    )


def test_conteo_encuestas_y_porcentaje():
    motor = _simular(tiempo_max=480)
    ac = motor.acumuladores
    con = sum(1 for i in motor.invitados.values() if i.estado.value == "retirado_con_encuesta")
    sin = sum(1 for i in motor.invitados.values() if i.estado.value == "retirado_sin_encuesta")
    assert (ac.cantidad_entrevistas_completas, ac.cantidad_abandonos_entrevista) == (con, sin)
    assert ac.porcentaje_abandono_entrevista == pytest.approx(100 * sin / (con + sin))


def test_vector_solo_muestra_invitados_presentes():
    motor = _simular(tiempo_max=480)
    for fila in motor.filas:
        for invitado_id, info in fila.invitados.items():
            if info["estado"].startswith("retirado"):
                # solo en la fila del evento en que se retira
                assert invitado_id == fila.invitado_evento_id


def test_rnd_se_muestra_en_la_fila_en_que_se_genera():
    motor = _simular(tiempo_max=60)
    llegadas = [f for f in motor.filas if f.nombre_evento == "llegada_invitado_auto"]
    assert llegadas and all(f.llegada_auto["rnd"] is not None for f in llegadas)
    otras = [f for f in motor.filas if f.nombre_evento == "llegada_invitado_peaton"]
    assert all(f.llegada_auto["rnd"] is None for f in otras)


def test_100000_iteraciones_en_tiempo_razonable():
    inicio = time.perf_counter()
    motor = _simular(tiempo_max=10**9, iteraciones_max=100_000)
    assert len(motor.filas) == 100_001  # + fila de inicialización
    assert time.perf_counter() - inicio < 60
