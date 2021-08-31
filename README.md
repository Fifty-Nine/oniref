This is just a quick little library I wrote for parsing the YAML files that
define the elements in the game. The main entry point is
`oniref.load_klei_definitions` which takes the path to the game's
installation directory. The function returns a dict that
maps the game's internal name for the element (e.g. `MoltenLead`) to
an instance of the `Element` type which records the various properties.

Here is an example program that will list all the liquid elements
which are stable between 30°C and 95°C sorted in order of their
thermal conductivity.

```
#!/usr/bin/env python3

import sys
from tabulate import tabulate

from oniref import load_klei_definitions, Quantity, State


def interesting(elem):
    return (elem.state == State.Liquid
            and (elem.high_transition is None or
                 elem.high_transition.temperature > Quantity(95, '°C'))
            and (elem.low_transition is None or
                 elem.low_transition.temperature <= Quantity(30, '°C')))


def format(elem):
    return [elem.pretty_name,
            elem.specific_heat_capacity.to('DTU/g/°C').m,
            elem.thermal_conductivity.to('DTU/(m*s)/°C').m,
            (elem.thermal_diffusivity.to('mm^2/s').m
             if elem.thermal_diffusivity is not None else None),
            (elem.low_transition.temperature.to('°C').m
             if elem.low_transition is not None else None),
            (elem.high_transition.temperature.to('°C').m
             if elem.high_transition is not None else None),
            elem.molar_mass.m]



def main(args):
    elements = sorted(
        load_klei_definitions(args[0]).find(interesting),
        key=lambda e: e.thermal_conductivity or Quantity(1, 'DTU/m*s/degC')
    )

    print(tabulate([format(e) for e in elements],
                   headers=['Name',
                            'SHC (DTU/g/°C)',
                            'TC (DTU/(m*s)/°C)',
                            'TD (mm^2/s)',
                            'TLow (°C)',
                            'THigh (°C)',
                            'MM (g/mol)']))

if __name__ == "__main__":
    main(sys.argv[1:])
```

Which produces something like:

```
$ ./example.py [path to ONI installation]
Name              SHC (DTU/g/°C)    TC (DTU/(m*s)/°C)    TD (mm^2/s)    TLow (°C)    THigh (°C)    MM (g/mol)
--------------  ----------------  -------------------  -------------  -----------  ------------  ------------
Resin                      1.11                 0.15        0.146886        20           125          52.5
Naphtha                    2.191                0.2         0.123355       -50.15        538.85      102.2
Visco-Gel                  1.55                 0.45        2.90323        -30.65        479.85       10
Polluted Water             4.179                0.58        0.138789       -20.65        119.35       20
Brine                      3.4                  0.609       0.149265       -22.5         102.75       22
Salt Water                 4.1                  0.609       0.135033        -7.5          99.69       21
Water                      4.179                0.609       0.145729        -0.65         99.35       18.0153
Crude Oil                  1.69                 2           1.36027        -40.15        399.85      500
Petroleum                  1.76                 2           1.53563        -57.15        538.85       82.2
Nuclear Waste              7.44                 6           0.806452        26.85        526.85      196.967
Mercury                    0.14                 8.3        59.2857         -38.85        356.75      200.59
Super Coolant              8.44                 9.46        1.23171       -271.15        436.85      250
```
