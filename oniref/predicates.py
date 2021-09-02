from __future__ import annotations

import itertools
from typing import Any, Callable, Optional

from oniref.elements import Element as OElement, State
from oniref.units import Q

SimplePredicate = Callable[[OElement], bool]
SimpleAttribute = Callable[[OElement], Any]


class Attribute:
    def __init__(self, attr: SimpleAttribute, desc: Optional[str] = None):
        self._attr = attr
        self._desc = desc

    def __repr__(self):
        return f'Attribute({self._desc})'

    def __str__(self):
        return self._desc or '<unknown attribute>'

    def __lt__(self, v: object) -> Predicate:
        return Predicate(lambda e: self._attr(e) < v)

    def __le__(self, v: object) -> Predicate:
        return Predicate(lambda e: self._attr(e) <= v)

    def __eq__(self, v: object) -> Predicate:  # type: ignore[override]
        return Predicate(lambda e: self._attr(e) == v)

    def __gt__(self, v: object) -> Predicate:
        return Predicate(lambda e: self._attr(e) > v)

    def __ge__(self, v: object) -> Predicate:
        return Predicate(lambda e: self._attr(e) >= v)

    def _wrap_attr_call(self, *args, **kwargs) -> Any:
        def wrap(e):
            return self._attr(e)(*args, **kwargs)

        return wrap

    @staticmethod
    def _child(attr, desc):
        return Attribute(attr, desc)

    def __call__(self, *args, **kwargs) -> Any:
        # `Element.foo(element)` is ambiguous. It could mean the user
        # wants `element.foo`, or they may want `Element.foo(element)`.
        # We resolve the ambiguity by testing whether `foo` is callable.
        # If it is, we return a new attribute object instead of
        # `element.foo` since this is a much less common use case.
        if (len(args) != 1 or not isinstance(args[0], OElement)
                or callable(self._attr(args[0]))):
            arg_string = ','.join(
                itertools.chain(
                    (repr(arg) for arg in args),
                    (f'{key}={value!r}' for key, value in kwargs.items())
                )
            )

            return self._child(
                self._wrap_attr_call(*args, **kwargs),
                f'{self._desc}({arg_string})'
            )

        return self._attr(args[0])

    def Is(self, v: Any) -> Predicate:
        return Predicate(lambda e: self._attr(e) is v)

    def In(self, *v: Any) -> Predicate:
        def result(e: OElement):
            attr = self._attr(e)
            if len(v) == 1:
                try:
                    return attr in v[0]
                except TypeError:
                    pass

            return attr in v

        return Predicate(result)

    def __getattr__(self, name) -> Attribute:
        def attr(e: OElement) -> Any:
            return getattr(self._attr(e), name)

        return self._child(attr, f'{self._desc}.{name}')


class OptionalAttribute(Attribute):
    def __repr__(self):
        return f'OptionalAttribute({self._desc})'

    @staticmethod
    def _child(attr, desc):
        return OptionalAttribute(attr, desc)

    def _wrap_attr_call(self, *args, **kwargs) -> Callable[[OElement], Any]:
        base = super()._wrap_attr_call(*args, **kwargs)

        def wrap(e):
            # base calls _attr(e) so no need to wrap it.
            return base(e) if self._attr(e) is not None else None

        return wrap

    def __getattr__(self, name) -> Attribute:
        def attr(e: OElement) -> Any:
            parent = self._attr(e)
            return getattr(parent, name) if parent is not None else None

        return self._child(attr, f'{self._desc}.?{name}')


class Predicate(Attribute):
    @staticmethod
    def _cast_attr(attr: SimpleAttribute) -> SimplePredicate:
        return lambda e: bool(attr(e))

    def __and__(self, o: SimpleAttribute) -> Predicate:
        return Predicate(
            lambda e: self._attr(e) and self._cast_attr(o)(e),
            f'{self} and {o}'
        )

    def __or__(self, o: SimpleAttribute) -> Predicate:
        return Predicate(
            lambda e: self._attr(e) or self._cast_attr(o)(e),
            f'{self} or {o}'
        )

    def __invert__(self) -> Predicate:
        return Predicate(
            lambda e: not self._attr(e),
            f'not {self}'
        )


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


def optional(attr: Attribute) -> Attribute:
    return OptionalAttribute(attr, str(attr))


def is_solid():
    return Element.state == State.Solid


def is_liquid() -> Predicate:
    return Element.state == State.Liquid


def is_gas() -> Predicate:
    return Element.state == State.Gas


def low_temp() -> Attribute:
    return optional(Element.low_transition).temperature


def high_temp() -> Attribute:
    return optional(Element.high_transition).temperature


def stable_at(temp: Q):
    return ((low_temp().Is(None) | (low_temp() < temp))
            & (high_temp().Is(None) | (high_temp() > temp)))


def stable_over(tempLo: Q, tempHi: Q):
    return stable_at(tempLo) & stable_at(tempHi)
