This is just a quick little library I wrote for parsing the YAML files that
define the elements in the game. The main entry point is
`oniref.load_klei_definitions` which takes the path to the game's `elements`
directory containing the YAML files. The function returns a dict that
maps the game's internal name for the element (e.g. `MoltenLead`) to
an instance of the `Element` type which records the various properties.

Here is an example program that will list all the liquid elements
which can reach -20C without freezing, sorted by their thermal diffusivity.

```
#!/usr/bin/env python3

import sys
from tabulate import tabulate

from oniref import load_klei_definitions, Quantity, State


def interesting(elem):
    return (elem.state == State.Liquid
            and elem.low_transition is not None
            and elem.low_transition.temperature < Quantity(-20, '°C')
            and (elem.high_transition is None
                 or elem.high_transition.temperature > Quantity(-20, '°C')))


def format(elem):
    return [elem.name,
            elem.specific_heat_capacity.to('DTU/g/°C').m,
            elem.thermal_conductivity.to('DTU/(m*s)/°C').m,
            elem.thermal_diffusivity.to('mm^2/s').m,
            elem.low_transition.temperature.to('°C').m,
            (elem.high_transition.temperature.to('°C').m
             if elem.high_transition is not None else None)]



def main(args):
    elements = load_klei_definitions(args[0])

    filtered = sorted([elem for elem 
                       in elements.values()
                       if interesting(elem)
                      ],
                      key=lambda e: e.thermal_diffusivity
                     )

    print(tabulate([format(e) for e in filtered],
                   headers=['Name',
                            'SHC (DTU/g/°C)',
                            'TC (DTU/(m*s)/°C)',
                            'TD (mm^2/s)',
                            'TLow (°C)',
                            'THigh (°C)']))

if __name__ == "__main__":
    main(sys.argv[1:])
```

Which produces something like:

```
$ ./example.py [path to elements files]
Name            SHC (DTU/g/°C)    TC (DTU/(m*s)/°C)    TD (mm^2/s)    TLow (°C)    THigh (°C)                                                                                                                                                                                               
------------  ----------------  -------------------  -------------  -----------  ------------                                                                                                                                                                                               
Ethanol                  2.46                 0.171      0.0695122      -114.05         78.35                                                                                                                                                                                               
Naphtha                  2.191                0.2        0.123355        -50.15        538.85                                                                                                                                                                                               
DirtyWater               4.179                0.58       0.138789        -20.65        119.35                                                                                                                                                                                               
Brine                    3.4                  0.609      0.149265        -22.5         102.75                                                                                                                                                                                               
SuperCoolant             8.44                 9.46       1.23171        -271.15        436.85                                                                                                                                                                                               
CrudeOil                 1.69                 2          1.36027         -40.15        399.85                                                                                                                                                                                               
Petroleum                1.76                 2          1.53563         -57.15        538.85                                                                                                                                                                                               
ViscoGel                 1.55                 0.45       2.90323         -30.65        479.85                                                                                                                                                                                               
Mercury                  0.14                 8.3       59.2857          -38.85        356.75  
$
```
