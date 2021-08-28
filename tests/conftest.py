from pytest import fixture
from oniref import Element
from oniref.units import Q


@fixture
def water():
    return Element("Water",
                   Q(4.179, 'DTU/g/°C'),
                   Q(0.184, 'DTU/(m s)/°C'),
                   Q(18.01528, 'g/mol'))
