import copy
from typing import Tuple

from polib import POFile, POEntry
from pytest import fixture
import yaml

from oniref import Element, Elements, Transition
from oniref.elements import State
from oniref.units import Q
from oniref.strings import KleiStrings


@fixture(name='water')
def water_fixture() -> Element:
    return Element('Water',
                   'STRINGS.ELEMENTS.WATER.NAME',
                   State.Liquid,
                   Q(4.179, 'DTU/g/°C'),
                   Q(0.609, 'DTU/(m s)/°C'),
                   Q(18.01528, 'g/mol'),
                   Q(1000, 'kg'))


@fixture(name='water_states')
def water_states_fixture(water) -> Tuple[Element, Element, Element]:
    water_cpy: Element = copy.deepcopy(water)
    ice = Element("Ice",
                  'STRINGS.ELEMENTS.ICE.NAME',
                  State.Solid,
                  Q(2.05, 'DTU/g/°C'),
                  Q(2.18, 'DTU/(m s)/°C'),
                  Q(18.01528, 'g/mol'),
                  Q(1100, 'kg'))
    steam = Element("Steam",
                    'STRINGS.ELEMENTS.STEAM.NAME',
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


@fixture(name='water_strings')
def water_strings_fixture() -> KleiStrings:
    return KleiStrings(
        {'STRINGS.ELEMENTS.WATER.NAME': 'Water <xml>(pretty)</xml>',
         'STRINGS.ELEMENTS.ICE.NAME': 'Ice (pretty)',
         'STRINGS.ELEMENTS.STEAM.NAME': 'Steam (pretty)'})


@fixture
def water_elements(water_states, water_strings) -> Elements:
    return Elements(water_states, water_strings)


def populate_elements(oni_install_path, water_states):
    elements_dir = (oni_install_path / 'OxygenNotIncluded_Data'
                    / 'StreamingAssets' / 'elements')
    elements_dir.mkdir(parents=True)

    def to_dict(elem):
        result = {'elementId': elem.name,
                  'state': elem.state.name,
                  'specificHeatCapacity':
                      elem.specific_heat_capacity.to('DTU/g/°C').m,
                  'thermalConductivity':
                      elem.thermal_conductivity.to('DTU/(m s)/°C').m,
                  'molarMass':
                      elem.molar_mass.to('g/mol').m,
                  'localizationID': elem.pretty_name}

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
        (elements_dir / name).write_text(
            yaml.dump({'elements': [to_dict(elem)]})
        )

    write_one('solid.yaml', water_states[0])
    write_one('liquid.yaml', water_states[1])
    write_one('gas.yaml', water_states[2])

    return oni_install_path


def populate_strings(oni_install_path, water_strings):
    strings_dir = (oni_install_path / 'OxygenNotIncluded_Data'
                   / 'StreamingAssets' / 'strings')
    strings_dir.mkdir(parents=True)
    po = POFile()

    for name, value in water_strings.items():
        po.append(POEntry(msgctxt=name,
                          msgid=value,
                          msgstr=''))

    po.save(strings_dir / 'strings_template.pot')


@fixture
def oni_install_dir(tmp_path, water_states, water_strings):
    result = tmp_path / 'oni'
    populate_elements(result, water_states)
    populate_strings(result, water_strings)
    return result
