from __future__ import annotations

from typing import Any, Callable, Optional

from oniref.elements import Element as OElement, State
from oniref.units import Q

SimplePredicate = Callable[[OElement], bool]
SimpleAttribute = Callable[[OElement], Any]


class Predicate:
    def __init__(self, pred: SimplePredicate):
        self._pred = pred

    def __call__(self, e: OElement) -> bool:
        return self._pred(e)

    def __and__(self, o: 'Predicate') -> 'Predicate':
        return Predicate(lambda e: self(e) and o(e))

    def __or__(self, o: 'Predicate') -> 'Predicate':
        return Predicate(lambda e: self(e) or o(e))

    def __invert__(self) -> 'Predicate':
        return Predicate(lambda e: not self(e))


class Attribute:
    def __init__(self, attr: SimpleAttribute, desc: Optional[str] = None):
        self._attr = attr
        self._desc = desc

    def __repr__(self):
        return f'Attribute({self._desc})'

    def __str__(self):
        return self._desc

    def __lt__(self, v: object) -> Predicate:
        return Predicate(lambda e: self(e) < v)

    def __le__(self, v: object) -> Predicate:
        return Predicate(lambda e: self(e) <= v)

    def __eq__(self, v: object) -> Predicate:  # type: ignore[override]
        return Predicate(lambda e: self(e) == v)

    def __gt__(self, v: object) -> Predicate:
        return Predicate(lambda e: self(e) > v)

    def __ge__(self, v: object) -> Predicate:
        return Predicate(lambda e: self(e) >= v)

    def __call__(self, e: OElement) -> Any:
        return self._attr(e)

    def Is(self, v: Any) -> Predicate:
        return Predicate(lambda e: self(e) is v)

    def In(self, *v: Any) -> Predicate:
        def result(e: OElement):
            attr = self(e)
            if len(v) == 1:
                try:
                    return attr in v[0]
                except TypeError:
                    pass

            return attr in v

        return Predicate(result)

    def __getattr__(self, name) -> Attribute:
        def attr(e: OElement) -> Any:
            return getattr(self(e), name)

        return Attribute(attr, f'{self._desc}.{name}')


def _make_element_type():
    class ElementType:
        def __getattr__(self, name):
            return Attribute(lambda e: getattr(e, name), f'Element.{name}')

    return ElementType()


Element = _make_element_type()


def And(l: Predicate, r: Predicate) -> Predicate:
    return l & r


def Or(l: Predicate, r: Predicate) -> Predicate:
    return l | r


def Not(p: Predicate) -> Predicate:
    return ~p


def is_solid():
    return Element.state == State.Solid


def is_liquid() -> Predicate:
    return Element.state == State.Liquid


def is_gas() -> Predicate:
    return Element.state == State.Gas


def low_temp() -> Attribute:
    return Attribute(
        lambda e: e.low_transition and e.low_transition.temperature,
        'e.low_transition.?temperature'
    )


def high_temp() -> Attribute:
    return Attribute(
        lambda e: e.high_transition and e.high_transition.temperature,
        'e.high_transition.?temperature'
    )


def stable_at(temp: Q):
    return ((low_temp().Is(None) | (low_temp() < temp))
            & (high_temp().Is(None) | (high_temp() > temp)))


def stable_over(tempLo: Q, tempHi: Q):
    return stable_at(tempLo) & stable_at(tempHi)
