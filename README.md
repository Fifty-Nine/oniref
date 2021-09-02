This is just a quick little library I wrote for parsing the YAML files that
define the elements in the game. The main entry point is
`oniref.load_klei_definitions` which takes the path to the game's
installation directory. The function returns a dict that
maps the game's internal name for the element (e.g. `MoltenLead`) to
an instance of the `Element` type which records the various properties.

Here is an example program that will list all the liquid elements
which are stable between 30°C and 95°C sorted in order of their
thermal conductivity.

```python
#!/usr/bin/env python3

import dataclasses
import sys
from tabulate import tabulate

from oniref import load_klei_definitions, Quantity, State
from oniref import predicates as OP


# Defines the table format. The key is the column header text and the value
# is a function that describes how to get the values for the column.
columns = {
    'Name'             : OP.Element.pretty_name,
    'SHC (DTU/g/°C)'   : OP.Element.specific_heat_capacity.to('DTU/g/°C').m,
    'TC (DTU/(m*s)/°C)': OP.Element.thermal_conductivity.to('DTU/(m*s)/°C').m,
    'TD (mm^2/s)'      : (OP.optional(OP.Element.thermal_diffusivity)
                          .to('mm^2/s').m),
    'MM (g/mol)'       : OP.Element.molar_mass.to('g/mol').m,
    'TLow (°C)'        : OP.low_temp().to('°C').m,
    'THigh (°C)'       : OP.high_temp().to('°C').m
}


def main(args):
    result = sorted(
        load_klei_definitions(args[0]).find(
            OP.is_liquid() & OP.stable_over(Quantity(30, '°C'),
                                            Quantity(90, '°C'))
        ),
        key=OP.Element.thermal_conductivity
    )

    print(
        tabulate(
            {k: [v(e) for e in result] for k, v in columns.items()},
            headers='keys'
        )
    )

if __name__ == "__main__":
    main(sys.argv[1:])
```

Which produces something like:

```
Name              SHC (DTU/g/°C)    TC (DTU/(m*s)/°C)    TD (mm^2/s)    MM (g/mol)    TLow (°C)    THigh (°C)
--------------  ----------------  -------------------  -------------  ------------  -----------  ------------
Resin                      1.11                 0.15        0.146886       52.5           20           125
Naphtha                    2.191                0.2         0.123355      102.2          -50.15        538.85
Visco-Gel                  1.55                 0.45        2.90323        10            -30.65        479.85
Polluted Water             4.179                0.58        0.138789       20            -20.65        119.35
Brine                      3.4                  0.609       0.149265       22            -22.5         102.75
Salt Water                 4.1                  0.609       0.135033       21             -7.5          99.69
Water                      4.179                0.609       0.145729       18.0153        -0.65         99.35
Crude Oil                  1.69                 2           1.36027       500            -40.15        399.85
Petroleum                  1.76                 2           1.53563        82.2          -57.15        538.85
Nuclear Waste              7.44                 6           0.806452      196.967         26.85        526.85
Mercury                    0.14                 8.3        59.2857        200.59         -38.85        356.75
Super Coolant              8.44                 9.46        1.23171       250           -271.15        436.85
```
