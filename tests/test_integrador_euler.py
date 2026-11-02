import pytest

from generador import integrar_duracion_entrevista


@pytest.mark.parametrize("p", [100, 70])
@pytest.mark.parametrize("h", [0.1, 0.01, 0.5])
def test_duracion_es_exactamente_5_unidades_si_h_divide_a_5(p, h):
    # dD/dt = P/5 -> D = P*t/5, así que D llega a P en t = 5, para cualquier P.
    # Antes, por error de redondeo, P=70 con h=0.1 daba 5.1 (un paso de más).
    t, _ = integrar_duracion_entrevista(p=p, h=h)
    assert t == 5.0


def test_mismo_resultado_para_ambos_tipos_de_invitado():
    t_auto, _ = integrar_duracion_entrevista(p=100, h=0.1)
    t_peaton, _ = integrar_duracion_entrevista(p=70, h=0.1)
    assert t_auto == t_peaton


def test_con_h_que_no_divide_a_5_corta_en_el_primer_paso_con_d_mayor_o_igual_a_p():
    t, pasos = integrar_duracion_entrevista(p=100, h=0.3)
    assert t == pytest.approx(5.1)  # 17 pasos: 16*0.3 = 4.8 < 5 <= 5.1
    assert pasos[-1].d >= 100
    assert pasos[-2].d < 100


def test_pasos_aplican_formula_de_euler():
    _, pasos = integrar_duracion_entrevista(p=100, h=0.1)
    assert pasos[0].t == 0.0
    assert pasos[0].d == 0.0
    for paso in pasos[:-1]:
        assert paso.derivada == 20
        assert paso.d_siguiente == pytest.approx(paso.d + 0.1 * paso.derivada)
    assert pasos[-1].d >= 100


def test_h_mas_chico_da_mas_pasos_intermedios():
    _, pasos_grueso = integrar_duracion_entrevista(p=100, h=1.0)
    _, pasos_fino = integrar_duracion_entrevista(p=100, h=0.01)
    assert len(pasos_fino) > len(pasos_grueso)


def test_h_invalido():
    with pytest.raises(ValueError):
        integrar_duracion_entrevista(p=100, h=0)
