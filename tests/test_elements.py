from oniref import Element


def test_diffusivity(water):
    assert water.thermal_diffusivity == (water.thermal_conductivity
                                         / water.specific_heat_capacity)


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
        "specificHeatCapacity": 1,
        "thermalConductivity": 1,
        "defaultMass": 1000,
        "molarMass": 18.01528,
        "lowTemp": 0,
        "highTemp": 100,
        "lowTempTransitionTarget": "Ice",
        "highTempTransitionTarget": "Steam"
    })
    assert result.low_transition == (0, "Ice")
    assert result.high_transition == (100, "Steam")
