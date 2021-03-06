from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from os import PathLike
from pathlib import Path
import re
from typing import (Any,
                    Callable,
                    IO,
                    Optional,
                    Sequence,
                    Union,
                    cast)
import yaml

from oniref.units import Q, maybeQ
from oniref.strings import load_strings, KleiStrings

#  pylint: disable=protected-access

Predicate = Callable[['Element'], bool]


class State(Enum):
    Vacuum = 0
    Solid = 1
    Liquid = 2
    Gas = 3


class Transition:
    temperature: Q
    target: Union[str, 'Element']
    ore: Optional[Union[str, 'Element']]
    ore_ratio: Optional[float]

    def __init__(
            self,
            temperature: Q,
            target: Union[str, Element],
            ore: Optional[Union[str, Element]] = None,
            ore_ratio: Optional[float] = None):
        self.temperature = temperature
        self.target = target
        self.ore = ore
        self.ore_ratio = ore_ratio

    def _name(self):
        return (self.target if isinstance(self.target, str)
                else self.target.name)

    def _ore_name(self):
        return self.ore.name if isinstance(self.ore, Element) else self.ore

    def _resolve(self, mapping):
        self.target = mapping[self._name()]
        self.ore = mapping.get(self._ore_name(), None)

    def __eq__(self, o):
        return (o.temperature == self.temperature
                and o._name() == self._name()
                and o._ore_name() == self._ore_name())

    @staticmethod
    def read(klei_dict: dict[str, Any], prefix: str) -> Optional[Transition]:
        temp = klei_dict.get(f'{prefix}Temp')
        target = klei_dict.get(f'{prefix}TempTransitionTarget')
        ore = klei_dict.get(f'{prefix}TempTransitionOreId')
        ore_ratio = klei_dict.get(f'{prefix}TempTransitionOreMassConversion')
        ore_ratio = float(ore_ratio) if ore_ratio is not None else None

        if temp is None or target is None:
            return None

        return Transition(
            Q(float(temp), '??K').to('??C'), target, ore, ore_ratio
        )

    def __str__(self):
        ore_str = f' + {self.ore.pretty_name}' if self.ore is not None else ''
        return f'{self.target.pretty_name}{ore_str} @ {self.temperature}'


class MissingElementsError(Exception):
    def __init__(self):
        super().__init__(
            self, 'YAML file did not contain the expected "elements" key.'
        )


class BadDefinitionError(Exception):
    def __init__(self, elem, inner):
        super().__init__(
            self, f'Encountered bad definition for {elem}: {inner!r}'
        )
        self.elem = elem
        self.inner = inner


@dataclass
class Element:
    name: str
    pretty_name: str
    state: State
    specific_heat_capacity: Q
    thermal_conductivity: Q
    molar_mass: Q
    radiation_absorption: Q
    radioactivity: Q
    mass_per_tile: Optional[Q] = None
    low_transition: Optional[Transition] = None
    high_transition: Optional[Transition] = None

    def __repr__(self):
        return f"Element(name='{self.name}')"

    def __str__(self):
        return self.pretty_name

    @staticmethod
    def from_klei(klei_dict: dict) -> Element:
        try:
            return Element(
                name=klei_dict['elementId'],
                pretty_name=klei_dict['localizationID'],
                state=State[klei_dict['state']],
                specific_heat_capacity=Q(
                    klei_dict['specificHeatCapacity'], 'DTU/g/??C'
                ),
                thermal_conductivity=Q(
                    klei_dict['thermalConductivity'], 'DTU/(m s)/??C'
                ),
                molar_mass=Q(
                    klei_dict['molarMass'], 'g/mol'
                ),
                radiation_absorption=Q(
                    klei_dict['radiationAbsorptionFactor'], 'dimensionless'
                ),
                radioactivity=Q(
                    klei_dict['radiationPer1000Mass'], 'rads/kg'
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
        return (self.mass_per_tile / Q(1, 'm^3')
                if self.mass_per_tile is not None else None)

    def _resolve(self, mapping, strings):
        if self.low_transition:
            self.low_transition._resolve(mapping)

        if self.high_transition:
            self.high_transition._resolve(mapping)

        self.pretty_name = strings.get(self.pretty_name, self.pretty_name)

    def ??Q(self, ??T: Q, mass: Q):
        """
        Compute the heat energy gained or lost when changing the temperature of
        'mass' units of this element by '??T' degrees.
        """
        return (self.specific_heat_capacity
                * ??T.to('delta_degC')
                * mass.to('g')).to_compact()

    def ??T(self, ??Q: Q, mass: Q):
        """
        Compute the temperature change when heating 'mass' units of
        this element with '??Q' units of heat.
        """
        return (??Q.to('DTU') / (self.specific_heat_capacity
                                * mass.to('g')))

    def __eq__(self, o):
        return self.name == o.name


class Elements:
    def __init__(self,
                 definitions: Sequence[Element],
                 strings: KleiStrings):
        self._defs = tuple(definitions)
        self._id_map = {}
        for elem in self._defs:
            self._id_map[elem.name] = elem

        for elem in self._id_map.values():
            elem._resolve(self, strings)

    def __len__(self):
        return len(self._defs)

    def __getitem__(self, key: Union[int, str]):
        if isinstance(key, int):
            return self._defs[cast(int, key)]

        return self._id_map[cast(str, key)]

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def find(self, needle: Union[str, re.Pattern, Predicate]):
        match: Predicate
        if isinstance(needle, str):
            needlestr = cast(str, needle)

            def match_str(elem):
                return needlestr in elem.name or needlestr in elem.pretty_name

            match = match_str
        elif isinstance(needle, re.Pattern):
            pattern = cast(re.Pattern, needle)

            def match_re(elem):
                return (pattern.search(elem.name)
                        or pattern.search(elem.pretty_name))

            match = match_re

        elif callable(needle):
            match = cast(Predicate, needle)

        else:
            raise TypeError(needle)

        return [elem for elem in self._defs if match(elem)]


def load_klei_definitions_from_file(yaml_in: IO) -> list[Element]:
    try:
        return [Element.from_klei(d) for d
                in yaml.safe_load(yaml_in)['elements']]
    except KeyError as e:
        raise MissingElementsError from e


def load_klei_definitions(oni_path: Union[PathLike, str]) -> Elements:
    assets_path: Path = (Path(oni_path) / 'OxygenNotIncluded_Data'
                         / 'StreamingAssets')

    elements_path = assets_path / 'elements'
    strings_path = assets_path / 'strings'

    def load_one(name):
        return load_klei_definitions_from_file(
            (elements_path / name).open('r')
        )

    return Elements(load_one('gas.yaml')
                    + load_one('liquid.yaml')
                    + load_one('solid.yaml'),
                    load_strings(strings_path / 'strings_template.pot'))
