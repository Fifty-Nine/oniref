from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional

from oniref.units import Q


Transition = Tuple[float, str]


@dataclass
class Element:
    name: str
    specific_heat_capacity: Q
    thermal_conductivity: Q
    density: Q
    mass_per_tile: Q
    low_transition: Optional[Transition] = None
    high_transition: Optional[Transition] = None

    @staticmethod
    def from_klei(klei_dict: dict) -> Element:
        return Element(
            name=klei_dict['elementId'],
            specific_heat_capacity=Q(
                klei_dict['specificHeatCapacity'], 'DTU/g/°C'
            ),
            thermal_conductivity=Q(
                klei_dict['thermalConductivity'], 'DTU/(m s)/°C'
            ),
            density=Q(
                klei_dict['molarMass'], 'g/mol'
            ),
            mass_per_tile=Q(
                klei_dict['defaultMass'], 'g'
            ),
            low_transition=(
                klei_dict['lowTemp'], klei_dict['lowTempTransitionTarget']
            ) if 'lowTemp' in klei_dict else None,
            high_transition=(
                klei_dict['highTemp'], klei_dict['highTempTransitionTarget']
            ) if 'highTemp' in klei_dict else None
        )

    @property
    def thermal_diffusivity(self) -> Q:
        return self.thermal_conductivity / self.specific_heat_capacity
