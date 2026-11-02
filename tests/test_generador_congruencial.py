from generador import GeneradorCongruencial


def test_primer_valor_con_parametros_del_tp():
    gen = GeneradorCongruencial()
    # x1 = (1714*1234 + 1221) mod 3922
    assert gen.siguiente() == ((1714 * 1234 + 1221) % 3922) / 3922


def test_valores_quedan_en_rango_0_1():
    gen = GeneradorCongruencial()
    for _ in range(1000):
        valor = gen.siguiente()
        assert 0.0 <= valor < 1.0


def test_misma_semilla_misma_secuencia():
    gen_a = GeneradorCongruencial()
    gen_b = GeneradorCongruencial()
    secuencia_a = [gen_a.siguiente() for _ in range(20)]
    secuencia_b = [gen_b.siguiente() for _ in range(20)]
    assert secuencia_a == secuencia_b


def test_generador_es_compartible_entre_variables():
    # Dos "variables" que usan el mismo objeto generador no deben repetir valores
    gen = GeneradorCongruencial()
    primero = gen.siguiente()
    segundo = gen.siguiente()
    assert primero != segundo
