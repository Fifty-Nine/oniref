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
