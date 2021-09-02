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
