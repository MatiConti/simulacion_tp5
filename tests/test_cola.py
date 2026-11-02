from models import Cola


def test_fifo_orden():
    cola = Cola(nombre="acreditacion")
    cola.encolar(1)
    cola.encolar(2)
    cola.encolar(3)
    assert cola.desencolar() == 1
    assert cola.desencolar() == 2
    assert cola.cantidad == 1


def test_desencolar_cola_vacia_devuelve_none():
    cola = Cola(nombre="entrevista")
    assert cola.desencolar() is None


def test_contains_y_quitar():
    cola = Cola(nombre="entrevista", tiempo_paciencia=5.0)
    cola.encolar(1)
    cola.encolar(2)
    assert 2 in cola
    cola.quitar(2)
    assert 2 not in cola
    assert cola.cantidad == 1
