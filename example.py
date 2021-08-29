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
