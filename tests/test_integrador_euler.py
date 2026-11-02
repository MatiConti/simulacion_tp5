import pytest

from generador import integrar_duracion_entrevista


@pytest.mark.parametrize("p", [100, 70])
def test_duracion_converge_a_5_unidades(p):
    t, _ = integrar_duracion_entrevista(p=p, h=0.1)
    assert t == pytest.approx(5.0, abs=0.15)


def test_pasos_arrancan_en_cero_y_terminan_en_d_mayor_o_igual_a_p():
    p = 100
    _, pasos = integrar_duracion_entrevista(p=p, h=0.1)
    assert pasos[0].t == 0.0
    assert pasos[0].d == 0.0
    assert pasos[-1].d >= p


def test_h_mas_chico_da_mas_pasos_intermedios():
    _, pasos_grueso = integrar_duracion_entrevista(p=100, h=1.0)
    _, pasos_fino = integrar_duracion_entrevista(p=100, h=0.01)
    assert len(pasos_fino) > len(pasos_grueso)
