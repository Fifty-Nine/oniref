This is just a quick little library I wrote for parsing the YAML files that
define the elements in the game. The main entry point is
`oniref.load_klei_definitions` which takes the path to the game's `elements`
directory containing the YAML files. The function returns a dict that
maps the game's internal name for the element (e.g. `MoltenLead`) to
an instance of the `Element` type which records the various properties.

Here is an example program that will list all the liquid elements
which can reach -100C without freezing, sorted by their thermal diffusivity.

```
#!/usr/bin/env python3

import sys
from tabulate import tabulate

from oniref import load_klei_definitions, Quantity, State


def interesting(elem):
    return (elem.state == State.Liquid
            and elem.low_transition is not None
            and elem.low_transition.temperature < Quantity(-100, '°C'))


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
Name              SHC (DTU/g/°C)    TC (DTU/(m*s)/°C)    TD (mm^2/s)    TLow (°C)    THigh (°C)
--------------  ----------------  -------------------  -------------  -----------  ------------
LiquidMethane              2.191               0.03        0.0136924      -182.6        -161.5
Chlorine                   0.48                0.0081      0.016875       -100.98        -34.6
LiquidHydrogen             2.4                 0.1         0.0416667      -259.15       -252.15
LiquidPropane              2.4                 0.1         0.0416667      -188.15        -42.15
MoltenSyngas               2.4                 0.1         0.0416667      -259.15       -252.15
Ethanol                    2.46                0.171       0.0695122      -114.05         78.35
SuperCoolant               8.44                9.46        1.23171        -271.15        436.85
LiquidOxygen               1.01                2           3.9604         -218.79       -182.96
$
```
