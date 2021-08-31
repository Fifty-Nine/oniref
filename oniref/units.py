from typing import Optional
from pint import UnitRegistry, Quantity as BaseQ

registry = UnitRegistry()
registry.define('DTU = J')

Q = registry.Quantity
Unit = registry.Unit
shc_units = registry.parse_units('J/g/°C')
tc_units = registry.parse_units('J/(m s)/°C')


def maybeQ(mag: Optional[float], dim) -> Optional[BaseQ]:
    return Q(mag, dim) if mag is not None else None
