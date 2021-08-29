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
        "highTempTransitionTarget": "Steam"
    })
    assert result.low_transition == Transition(Q(0.0, 'degC'), 'Ice')
    assert result.high_transition == Transition(Q(100.0, 'degC'), 'Steam')
