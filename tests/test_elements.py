import re

import pytest

from oniref import Element, Transition
from oniref.units import Q


def test_diffusivity(water):
    assert water.thermal_diffusivity == (water.thermal_conductivity
                                         / (water.specific_heat_capacity
                                            * water.density))


def test_diffusivity_missing_shc(water):
    water.specific_heat_capacity = Q(0, 'DTU/g/degC')
    assert water.thermal_diffusivity is None


def test_density(water):
    assert water.density == Q(1000, "kg / m^3")


def test_density_no_mpt(water):
    water.mass_per_tile = None
    assert water.density is None


def test_from_klei_simple(water):
    assert water == Element.from_klei({
        "elementId": "Water",
        "maxMass": 1000,
        "liquidCompression": 1.01,
        "speed": 125,
        "minHorizontalFlow": 0.01,
        "minVerticalFlow": 0.01,
        "specificHeatCapacity": 4.179,
        "thermalConductivity": 0.609,
        "solidSurfaceAreaMultiplier": 1,
        "liquidSurfaceAreaMultiplier": 25,
        "gasSurfaceAreaMultiplier": 1,
        "convertId": "DirtyWater",
        "defaultTemperature": 300,
        "defaultMass": 1000,
        "molarMass": 18.01528,
        "toxicity": 0,
        "lightAbsorptionFactor": 0.25,
        "radiationAbsorptionFactor": 0.8,
        "radiationPer1000Mass": 0,
        "tags": ["AnyWater"],
        "isDisabled": False,
        "state": "Liquid",
        "localizationID": "STRINGS.ELEMENTS.WATER.NAME",
        "dlcId": ""
    })


def test_from_klei_transitions():
    result = Element.from_klei({
        "elementId": "Water",
        "state": "Liquid",
        "specificHeatCapacity": 1,
        "thermalConductivity": 1,
        "defaultMass": 1000,
        "molarMass": 18.01528,
        "lowTemp": Q(0.0, 'degC').to('degK').m,
        "highTemp": Q(100.0, 'degC').to('degK').m,
        "lowTempTransitionTarget": "Ice",
        "highTempTransitionTarget": "Steam",
        "localizationID": "STRINGS.ELEMENTS.WATER.NAME"
    })
    assert result.low_transition == Transition(Q(0.0, 'degC'), 'Ice')
    assert result.high_transition == Transition(Q(100.0, 'degC'), 'Steam')


def test_elements_as_container(water_elements):
    assert len(water_elements) == 3

    as_list = []
    for elem in water_elements:
        as_list.append(elem)

    assert len(as_list) == 3
    assert water_elements['Ice'] in as_list
    assert water_elements['Water'] in as_list
    assert water_elements['Steam'] in as_list


def test_find_element_string(water_elements):
    assert water_elements.find('DirtyWater') == []
    assert water_elements.find('Wat') == [water_elements['Water']]
    assert water_elements.find('Wat')[0] is water_elements['Water']


def test_find_element_regex(water_elements):
    assert water_elements.find(re.compile('DirtyWater')) == []
    assert water_elements.find(re.compile('Wat')) == [water_elements['Water']]
    assert water_elements.find(re.compile('Wat'))[0] is water_elements['Water']

    found = water_elements.find(re.compile('^Steam|Water|Ice$'))
    assert len(found) == 3
    for elem in water_elements:
        assert elem in found


def test_find_pretty_string(water_elements):
    assert water_elements.find('Water (pretty)') == [water_elements['Water']]
    assert water_elements.find('Water (pretty)')[0] is water_elements['Water']


def test_find_pretty_regex(water_elements):
    found = water_elements.find(re.compile('pretty'))
    assert len(found) == 3
    for elem in water_elements:
        assert elem in found


def test_find_bad_type(water_elements):
    with pytest.raises(TypeError):
        water_elements.find(None)


def test_elements_index_bad_type(water_elements):
    with pytest.raises(TypeError):
        _ = water_elements[None]
