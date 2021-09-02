import pytest

from oniref import Quantity
from oniref.predicates import (Predicate, Attribute, OptionalAttribute,
                               And, Or, Not,
                               optional,
                               is_solid, is_liquid, is_gas,
                               low_temp, high_temp,
                               stable_at, stable_over,
                               Element)


def test_simple_predicate(water):
    pred = Predicate(lambda e: True)
    assert pred(water)


def test_pred_and(water):
    pred = And(Predicate(lambda e: True),
               Predicate(lambda e: False))
    assert not pred(water)

    pred = And(Predicate(lambda e: False),
               Predicate(lambda e: True))
    assert not pred(water)

    pred = And(Predicate(lambda e: True),
               Predicate(lambda e: True))
    assert pred(water)

    pred = And(Predicate(lambda e: False),
               Predicate(lambda e: False))
    assert not pred(water)


def test_pred_or(water):
    pred = Or(Predicate(lambda e: True),
              Predicate(lambda e: False))
    assert pred(water)

    pred = Or(Predicate(lambda e: False),
              Predicate(lambda e: True))
    assert pred(water)

    pred = Or(Predicate(lambda e: True),
              Predicate(lambda e: True))
    assert pred(water)

    pred = Or(Predicate(lambda e: False),
              Predicate(lambda e: False))
    assert not pred(water)


def test_pred_not(water):
    pred = Not(Predicate(lambda e: True))

    pred = Not(Predicate(lambda e: False))
    assert pred(water)


def test_simple_attr(water):
    attr = Attribute(lambda e: e.name)
    assert attr(water) == water.name


def test_attr_lt(water):
    pred = Attribute(lambda e: 0) < 1
    assert pred(water)

    pred = Attribute(lambda e: 1) < 1
    assert not pred(water)

    pred = Attribute(lambda e: 2) < 1
    assert not pred(water)


def test_attr_le(water):
    pred = Attribute(lambda e: 0) <= 1
    assert pred(water)

    pred = Attribute(lambda e: 1) <= 1
    assert pred(water)

    pred = Attribute(lambda e: 2) <= 1
    assert not pred(water)


def test_attr_eq(water):
    pred = Attribute(lambda e: 0) == 1
    assert not pred(water)

    pred = Attribute(lambda e: 1) == 1
    assert pred(water)

    pred = Attribute(lambda e: 2) == 1
    assert not pred(water)


def test_attr_gt(water):
    pred = Attribute(lambda e: 0) > 1
    assert not pred(water)

    pred = Attribute(lambda e: 1) > 1
    assert not pred(water)

    pred = Attribute(lambda e: 2) > 1
    assert pred(water)


def test_attr_ge(water):
    pred = Attribute(lambda e: 0) >= 1
    assert not pred(water)

    pred = Attribute(lambda e: 1) >= 1
    assert pred(water)

    pred = Attribute(lambda e: 2) >= 1
    assert pred(water)


def test_attr_in(water):
    pred = Attribute(lambda e: 0).In([0, 1, 2])
    assert pred(water)

    pred = Attribute(lambda e: 0).In(0, 1, 2)
    assert pred(water)

    pred = Attribute(lambda e: 0).In(0)
    assert pred(water)

    pred = Attribute(lambda e: 1).In(0)
    assert not pred(water)


def test_attr_chain(water_elements):
    attr = Attribute(lambda e: e.low_transition)

    assert attr.target(water_elements['Water']) is water_elements['Ice']
    assert attr.target.name(water_elements['Water']) == 'Ice'


def test_attr_is(water_elements):
    pred = (Attribute(lambda e: e.low_transition)
            .target.Is(water_elements['Ice']))
    assert pred(water_elements['Water'])
    assert not pred(water_elements['Steam'])


def test_attr_str():
    assert str(Element.pretty_name) == 'Element.pretty_name'
    assert repr(Element.pretty_name) == 'Attribute(Element.pretty_name)'


def test_opt_attr_attr(water_elements):
    attr = OptionalAttribute(lambda e: e.low_transition)

    assert attr(water_elements['Ice']) is None
    assert attr.temperature(water_elements['Ice']) is None

    assert attr(water_elements['Water']) is not None
    assert attr.target(water_elements['Water']) is water_elements['Ice']


def test_opt_attr_str():
    assert (str(optional(Element.low_transition).target)
            == 'Element.low_transition.?target')
    assert (repr(optional(Element.low_transition).target)
            == 'OptionalAttribute(Element.low_transition.?target)')


def test_liquid(water_elements):
    pred = is_liquid()
    assert pred(water_elements['Water'])
    assert not pred(water_elements['Ice'])
    assert not pred(water_elements['Steam'])


def test_solid(water_elements):
    pred = is_solid()
    assert not pred(water_elements['Water'])
    assert pred(water_elements['Ice'])
    assert not pred(water_elements['Steam'])


def test_gas(water_elements):
    pred = is_gas()
    assert not pred(water_elements['Water'])
    assert not pred(water_elements['Ice'])
    assert pred(water_elements['Steam'])


def test_low_temp(water_elements):
    pred = low_temp() > Quantity(10, '°C')
    assert not pred(water_elements['Water'])
    assert pred(water_elements['Steam'])

    with pytest.raises(ValueError):
        pred(water_elements['Ice'])


def test_high_temp(water_elements):
    pred = high_temp() > Quantity(10, '°C')
    assert pred(water_elements['Water'])
    assert not pred(water_elements['Ice'])

    with pytest.raises(ValueError):
        pred(water_elements['Steam'])


def test_stable_at(water_elements):
    pred110 = stable_at(Quantity(110, '°C'))
    pred50 = stable_at(Quantity(50, '°C'))
    predn10 = stable_at(Quantity(-10, '°C'))

    assert not pred110(water_elements['Water'])
    assert pred110(water_elements['Steam'])
    assert not pred110(water_elements['Ice'])

    assert pred50(water_elements['Water'])
    assert not pred50(water_elements['Steam'])
    assert not pred50(water_elements['Ice'])

    assert not predn10(water_elements['Water'])
    assert not predn10(water_elements['Steam'])
    assert predn10(water_elements['Ice'])


def test_stable_over(water_elements):
    icy = stable_over(Quantity(-273, '°C'), Quantity(-10, '°C'))
    watery = stable_over(Quantity(10, '°C'), Quantity(90, '°C'))
    steamy = stable_over(Quantity(110, '°C'), Quantity(1000, '°C'))

    assert icy(water_elements['Ice'])
    assert not icy(water_elements['Water'])
    assert not icy(water_elements['Steam'])

    assert not watery(water_elements['Ice'])
    assert watery(water_elements['Water'])
    assert not watery(water_elements['Steam'])

    assert not steamy(water_elements['Ice'])
    assert not steamy(water_elements['Water'])
    assert steamy(water_elements['Steam'])

    melt = stable_over(Quantity(-10, '°C'), Quantity(10, '°C'))
    boil = stable_over(Quantity(90, '°C'), Quantity(110, '°C'))

    assert not melt(water_elements['Ice'])
    assert not melt(water_elements['Water'])
    assert not melt(water_elements['Steam'])

    assert not boil(water_elements['Ice'])
    assert not boil(water_elements['Water'])
    assert not boil(water_elements['Steam'])


def test_element_predicate(water):
    assert (Element.name == 'Water')(water)
    assert isinstance(Element.specific_heat_capacity, Attribute)

    bad_pred = Element.name_that_does_not_exist
    with pytest.raises(AttributeError):
        bad_pred(water)


def test_call_expr(water):
    attr = Element.molar_mass.to('ounce/mol').m
    assert attr(water) == pytest.approx(water.molar_mass.to('ounce/mol').m)


def test_opt_call_expr(water):
    attr = optional(Element.mass_per_tile).to('pound').m
    assert attr(water) == pytest.approx(water.mass_per_tile.to('pound').m)
