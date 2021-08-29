import copy
from typing import Tuple

from pytest import fixture
import yaml

from oniref import Element
from oniref.units import Q


@fixture(name='water')
def water_fixture() -> Element:
    return Element("Water",
                   Q(4.179, 'DTU/g/°C'),
                   Q(0.609, 'DTU/(m s)/°C'),
                   Q(18.01528, 'g/mol'),
                   Q(1000, 'kg'))


@fixture(name='water_states')
def water_states_fixture(water) -> Tuple[Element, Element, Element]:
    water = copy.deepcopy(water)
    ice = Element("Ice",
                  Q(2.05, 'DTU/g/°C'),
                  Q(2.18, 'DTU/(m s)/°C'),
                  Q(18.01528, 'g/mol'),
                  Q(1100, 'kg'))
    steam = Element("Steam",
                    Q(4.179, 'DTU/g/°C'),
                    Q(0.184, 'DTU/(m s)/°C'),
                    Q(18.01528, 'g/mol'),
                    None)

    water.low_transition = (0, ice.name)
    water.high_transition = (100, steam.name)
    ice.high_transition = (0, water.name)
    steam.low_transition = (100, water.name)

    return (ice, water, steam)


@fixture
def klei_definitions_dir(tmp_path, water_states):
    def to_dict(elem):
        result = {'elementId': elem.name,
                  'specificHeatCapacity':
                      elem.specific_heat_capacity.to('DTU/g/°C').m,
                  'thermalConductivity':
                      elem.thermal_conductivity.to('DTU/(m s)/°C').m,
                  'molarMass':
                      elem.molar_mass.to('g/mol').m}

        if elem.mass_per_tile is not None:
            result['maxMass'] = elem.mass_per_tile.to('kg').m

        if elem.low_transition is not None:
            result['lowTemp'] = elem.low_transition[0]
            result['lowTempTransitionTarget'] = elem.low_transition[1]

        if elem.high_transition is not None:
            result['highTemp'] = elem.high_transition[0]
            result['highTempTransitionTarget'] = elem.high_transition[1]

        return result

    def write_one(name, elem):
        (tmp_path / name).write_text(
            yaml.dump({'elements': [to_dict(elem)]})
        )

    write_one('solid.yaml', water_states[0])
    write_one('liquid.yaml', water_states[1])
    write_one('gas.yaml', water_states[2])

    return tmp_path
