import math

from generador import DistribucionExponencial, DistribucionUniforme, GeneradorCongruencial


def test_uniforme_en_rango_esperado():
    gen = GeneradorCongruencial()
    dist = DistribucionUniforme(gen, minimo=3, maximo=7)
    for _ in range(500):
        valor, rnd = dist.generar()
        assert 3 <= valor <= 7
        assert 0.0 <= rnd < 1.0


def test_uniforme_devuelve_el_rnd_usado():
    gen = GeneradorCongruencial()
    dist = DistribucionUniforme(gen, minimo=0, maximo=1)
    valor, rnd = dist.generar()
    assert valor == rnd  # con minimo=0, maximo=1, valor == rnd


def test_exponencial_siempre_positiva():
    gen = GeneradorCongruencial()
    dist = DistribucionExponencial(gen, media=20)
    for _ in range(500):
        valor, rnd = dist.generar()
        assert valor >= 0
        assert 0.0 <= rnd < 1.0


def test_exponencial_formula_transformada_inversa():
    gen = GeneradorCongruencial()
    dist = DistribucionExponencial(gen, media=2)
    rnd_esperado = GeneradorCongruencial().siguiente()
    valor, rnd = dist.generar()
    assert rnd == rnd_esperado
    assert valor == -2 * math.log(1 - rnd_esperado)
