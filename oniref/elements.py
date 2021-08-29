from __future__ import annotations
from dataclasses import dataclass
import math
from os import PathLike
from pathlib import Path
from typing import Tuple, Optional, Union
import yaml

from oniref.units import Q, maybeQ, registry


Transition = Tuple[float, str]

class BadDefinitionError(Exception):
    def __init__(self, elem, inner):
        self.elem = elem
        self.inner = inner

    def __str__(self):
        return f'Encountered bad definition for {self.elem}: {self.inner!s}'

    def __repr__(self):
        return f'BadDefinitionError(elem={self.elem!r}, inner={self.inner!r}'


def _read_transition(klei_dict: dict, prefix: str) -> Optional[Transition]:
    temp = klei_dict.get(f'{prefix}Temp')
    target = klei_dict.get(f'{prefix}TempTransitionTarget')

    return (temp, target) if temp is not None and target is not None else None


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
                low_transition=_read_transition(klei_dict, 'low'),
                high_transition=_read_transition(klei_dict, 'high')
            )
        except KeyError as e:
            raise BadDefinitionError(
                klei_dict.get('elementId', '<unknown>'), e
            ) from e

    @property
    def thermal_diffusivity(self) -> Optional[Q]:
        if self.specific_heat_capacity.m == 0: return None

        density = self.density or Q(1, 'kg/m^3')
        return (self.thermal_conductivity
                / (self.specific_heat_capacity * density))

    @property
    def density(self) -> Optional[Q]:
        return (self.mass_per_tile / registry.parse_expression('1 m^3')
                if self.mass_per_tile is not None else None)


def load_klei_definitions(data_path: Union[PathLike, str]):
    if isinstance(data_path, str):
        data_path = Path(data_path)

    def load_one(name):
        return yaml.load((data_path / name).open('r'))['elements']

    result = {}
    all_defs = (load_one("gas.yaml")
                + load_one("liquid.yaml")
                + load_one("solid.yaml"))
    for elem in all_defs:
        result[elem['elementId']] = Element.from_klei(elem)

    return result
