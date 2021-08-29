from io import StringIO
import pytest
import yaml

import oniref.elements as OE
from oniref.units import Q


def test_load_simple():
    contents = StringIO(
        yaml.dump(
            {"elements": [{"elementId": "Unobtanium",
                           "maxMass": 1234,
                           "specificHeatCapacity": 100,
                           "thermalConductivity": 1,
                           "molarMass": 1111,
                           "unexpected_key": "ayy"}]}
        )
    )

    result = OE.load_klei_definitions_from_file(contents)
    assert result == [
        OE.Element(
            "Unobtanium",
            specific_heat_capacity=Q(100, "DTU/g/degC"),
            thermal_conductivity=Q(1, "DTU/(m s)/degC"),
            molar_mass=Q(1111, "g/mol"),
            mass_per_tile=Q(1234, "kg")
        )
    ]


def test_missing_name():
    contents = StringIO(yaml.dump({"elements": [{"placeholder": 1}]}))

    with pytest.raises(OE.BadDefinitionError) as exc:
        OE.load_klei_definitions_from_file(contents)

    assert "<unknown>" in str(exc)


def test_missing_key():
    contents = StringIO(yaml.dump({"elements": [{"elementId": "foo"}]}))

    with pytest.raises(OE.BadDefinitionError) as exc:
        OE.load_klei_definitions_from_file(contents)

    assert "foo" in str(exc)


def test_missing_elements():
    contents = StringIO(yaml.dump({}))

    with pytest.raises(OE.MissingElementsError):
        OE.load_klei_definitions_from_file(contents)


def test_load_all(klei_definitions_dir, water_states):
    result = OE.load_klei_definitions(klei_definitions_dir)

    assert result['Ice'] == water_states[0]
    assert result['Water'] == water_states[1]
    assert result['Steam'] == water_states[2]


def test_load_str_path(klei_definitions_dir):
    OE.load_klei_definitions(str(klei_definitions_dir))
