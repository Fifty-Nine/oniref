from pytest import fixture
from oniref import Element
from oniref.units import Q


@fixture
def water():
    return Element("Water",
                   Q(4.179, 'DTU/g/°C'),
                   Q(0.609, 'DTU/(m s)/°C'),
                   Q(18.01528, 'g/mol'),
                   Q(1000, 'g'))