from oniref.predicates import (Predicate, Attribute,
                               And, Or, Not)


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


def test_attr_chain(water_elements):
    attr = Attribute(lambda e: e.low_transition)

    assert attr.target(water_elements['Water']) is water_elements['Ice']
    assert attr.target.name(water_elements['Water']) == 'Ice'


def test_attr_is(water_elements):
    pred = (Attribute(lambda e: e.low_transition)
            .target.Is(water_elements['Ice']))
    assert pred(water_elements['Water'])
    assert not pred(water_elements['Steam'])
