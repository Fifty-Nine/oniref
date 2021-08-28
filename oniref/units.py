from pint import UnitRegistry

registry = UnitRegistry()
registry.define('DTU = J')

Q = registry.Quantity

dtu = registry.joule
gram = registry.gram
meter = registry.meter
second = registry.second
degC = registry.degC

shc_units = registry.parse_units('J/g/°C')
tc_units = registry.parse_units('J/(m s)/°C')
