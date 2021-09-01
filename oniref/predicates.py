from __future__ import annotations

from typing import Any, Callable

from oniref.elements import Element

SimplePredicate = Callable[[Element], bool]
SimpleAttribute = Callable[[Element], Any]


class Predicate:
    def __init__(self, pred: SimplePredicate):
        self._pred = pred

    def __call__(self, e: Element) -> bool:
        return self._pred(e)

    def __and__(self, o: 'Predicate') -> 'Predicate':
        return Predicate(lambda e: self(e) and o(e))

    def __or__(self, o: 'Predicate') -> 'Predicate':
        return Predicate(lambda e: self(e) or o(e))

    def __invert__(self) -> 'Predicate':
        return Predicate(lambda e: not self(e))


class Attribute:
    def __init__(self, attr: SimpleAttribute):
        self._attr = attr

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

    def __call__(self, e: Element) -> Any:
        return self._attr(e)

    def Is(self, v: Any) -> Predicate:
        return Predicate(lambda e: self(e) is v)

    def __getattr__(self, name) -> Attribute:
        def attr(e: Element) -> Any:
            return getattr(self(e), name)

        return Attribute(attr)


def And(l: Predicate, r: Predicate) -> Predicate:
    return l & r


def Or(l: Predicate, r: Predicate) -> Predicate:
    return l | r


def Not(p: Predicate) -> Predicate:
    return ~p
