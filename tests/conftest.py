import copy
from typing import Tuple

from pytest import fixture
import yaml

from oniref import Element, Transition
from oniref.elements import State
from oniref.units import Q


@fixture(name='water')
def water_fixture() -> Element:
    return Element("Water",
                   State.Liquid,
                   Q(4.179, 'DTU/g/°C'),
                   Q(0.609, 'DTU/(m s)/°C'),
                   Q(18.01528, 'g/mol'),
                   Q(1000, 'kg'))


@fixture(name='water_states')
def water_states_fixture(water) -> Tuple[Element, Element, Element]:
    water_cpy: Element = copy.deepcopy(water)
    ice = Element("Ice",
                  State.Solid,
                  Q(2.05, 'DTU/g/°C'),
                  Q(2.18, 'DTU/(m s)/°C'),
                  Q(18.01528, 'g/mol'),
                  Q(1100, 'kg'))
    steam = Element("Steam",
                    State.Gas,
                    Q(4.179, 'DTU/g/°C'),
                    Q(0.184, 'DTU/(m s)/°C'),
                    Q(18.01528, 'g/mol'),
                    None)

    water_cpy.low_transition = Transition(Q(0.0, 'degC'), ice)
    water_cpy.high_transition = Transition(Q(100.0, 'degC'), steam)
    ice.high_transition = Transition(Q(0.0, 'degC'), water_cpy)
    steam.low_transition = Transition(Q(100.0, 'degC'), water_cpy)

    return (ice, water_cpy, steam)


@fixture
def klei_definitions_dir(tmp_path, water_states):
    def to_dict(elem):
        result = {'elementId': elem.name,
                  'state': elem.state.name,
                  'specificHeatCapacity':
                      elem.specific_heat_capacity.to('DTU/g/°C').m,
                  'thermalConductivity':
                      elem.thermal_conductivity.to('DTU/(m s)/°C').m,
                  'molarMass':
                      elem.molar_mass.to('g/mol').m}

        if elem.mass_per_tile is not None:
            result['maxMass'] = elem.mass_per_tile.to('kg').m

        if elem.low_transition is not None:
            result['lowTemp'] = elem.low_transition.temperature.to('degK').m
            result['lowTempTransitionTarget'] = elem.low_transition.target.name

        if elem.high_transition is not None:
            result['highTemp'] = elem.high_transition.temperature.to('degK').m
            result['highTempTransitionTarget'] = \
                elem.high_transition.target.name

        return result

    def write_one(name, elem):
        (tmp_path / name).write_text(
            yaml.dump({'elements': [to_dict(elem)]})
        )

    write_one('solid.yaml', water_states[0])
    write_one('liquid.yaml', water_states[1])
    write_one('gas.yaml', water_states[2])

    return tmp_path
