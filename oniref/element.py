from __future__ import annotations
from typing import Tuple, Optional

from oniref.units import Q


Transition = Tuple[float, 'Element']


class Element:
    def __init__(self, name: str,
                 specific_heat_capacity: Q,
                 thermal_conductivity: Q,
                 density: Q,
                 low_transition: Optional[Transition] = None,
                 high_transition: Optional[Transition] = None):
        self.name = name
        self.specific_heat_capacity = specific_heat_capacity
        self.thermal_conductivity = thermal_conductivity
        self.density = density
        self.low_transition = low_transition
        self.high_transition = high_transition

    @property
    def thermal_diffusivity(self):
        return self.thermal_conductivity / self.specific_heat_capacity
