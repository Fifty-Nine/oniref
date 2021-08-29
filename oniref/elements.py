from __future__ import annotations
from dataclasses import dataclass
from os import PathLike
from pathlib import Path
from typing import (Any,
                    IO,
                    Optional,
                    Union)
from weakref import proxy, ProxyType

import yaml

from oniref.units import Q, maybeQ, registry

#  pylint: disable=protected-access


class Transition:
    temperature: Q
    target: Union[str, ProxyType['Element']]

    def __init__(self, temperature: Q, target: Union[str, Element]):
        self.temperature = temperature
        self.target = target if isinstance(target, str) else proxy(target)

    def _name(self):
        return (self.target if isinstance(self.target, str)
                else self.target.name)

    def _resolve(self, mapping):
        self.target = proxy(mapping[self._name()])

    def __eq__(self, o):
        return (o.temperature == self.temperature
                and o._name() == self._name())

    @staticmethod
    def read(klei_dict: dict[str, Any], prefix: str) -> Optional[Transition]:
        temp = klei_dict.get(f'{prefix}Temp')
        target = klei_dict.get(f'{prefix}TempTransitionTarget')

        if temp is None or target is None:
            return None

        return Transition(Q(temp, '°K').to('°C'), target)


class MissingElementsError(Exception):
    def __init__(self):
        super().__init__(
            self, 'YAML file did not contain the expected "elements" key.'
        )


class BadDefinitionError(Exception):
    def __init__(self, elem, inner):
        super().__init__(
            self, f'Encountered bad definition for {elem}: {inner!s}'
        )
        self.elem = elem
        self.inner = inner


@dataclass
class Element:
    name: str
    specific_heat_capacity: Q
    thermal_conductivity: Q
    molar_mass: Q
    mass_per_tile: Optional[Q]
    low_transition: Optional[Transition] = None
    high_transition: Optional[Transition] = None

    @staticmethod
    def from_klei(klei_dict: dict) -> Element:
        try:
            return Element(
                name=klei_dict['elementId'],
                specific_heat_capacity=Q(
                    klei_dict['specificHeatCapacity'], 'DTU/g/°C'
                ),
                thermal_conductivity=Q(
                    klei_dict['thermalConductivity'], 'DTU/(m s)/°C'
                ),
                molar_mass=Q(
                    klei_dict['molarMass'], 'g/mol'
                ),
                mass_per_tile=maybeQ(klei_dict.get('maxMass'), 'kg'),
                low_transition=Transition.read(klei_dict, 'low'),
                high_transition=Transition.read(klei_dict, 'high')
            )
        except KeyError as e:
            raise BadDefinitionError(
                klei_dict.get('elementId', '<unknown>'), e
            ) from e

    @property
    def thermal_diffusivity(self) -> Optional[Q]:
        if self.specific_heat_capacity.m == 0:
            return None

        density = self.density or Q(1, 'kg/m^3')
        return (self.thermal_conductivity
                / (self.specific_heat_capacity * density)).to_base_units()

    @property
    def density(self) -> Optional[Q]:
        return ((self.mass_per_tile
                 / registry.parse_expression('1 m^3').to_base_units())
                if self.mass_per_tile is not None else None)

    def _resolve(self, mapping):
        if self.low_transition:
            self.low_transition._resolve(mapping)

        if self.high_transition:
            self.high_transition._resolve(mapping)


def load_klei_definitions_from_file(yaml_in: IO) -> list[Element]:
    try:
        return [Element.from_klei(d) for d
                in yaml.safe_load(yaml_in)['elements']]
    except KeyError as e:
        raise MissingElementsError from e


def load_klei_definitions(data_path: Union[PathLike, str]) \
        -> dict[str, Element]:
    if isinstance(data_path, str):
        data_path = Path(data_path)

    def load_one(name):
        return load_klei_definitions_from_file((data_path / name).open('r'))

    result = {}
    all_defs = (load_one("gas.yaml")
                + load_one("liquid.yaml")
                + load_one("solid.yaml"))
    for elem in all_defs:
        result[elem.name] = elem

    for elem in result.values():
        elem._resolve(result)

    return result
