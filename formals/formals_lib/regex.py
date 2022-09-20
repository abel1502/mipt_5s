from __future__ import annotations
import typing
import io

from . import itree


class Regex(itree.ITree["Regex"]):
    def __add__(self, other):
        if not isinstance(other, Regex):
            return NotImplemented
        if isinstance(other, Either):
            return other.__radd__(self)
        return Either(self, other)
    
    def __radd__(self, other):
        if not isinstance(other, Regex):
            return NotImplemented
        return other.__add__(self)
    
    def __mul__(self, other):
        if not isinstance(other, Regex):
            return NotImplemented
        if isinstance(other, Concat):
            return other.__rmul__(self)
        return Concat(self, other)
    
    def __rmul__(self, other):
        if not isinstance(other, Regex):
            return NotImplemented
        return other.__mul__(self)
    
    def repeat(self, n: int) -> Regex:
        return Concat(*([self] * n))
    
    def __pow__(self, power):
        if isinstance(power, int):
            return self.repeat(power)
        return NotImplemented


class Letter(Regex):
    letter: str
    
    def __init__(self, letter: str):
        assert len(letter) == 1
        
        self.letter = letter
    
    def get_children(self) -> typing.Iterable[Regex]:
        return ()


class Zero(Regex):
    def get_children(self) -> typing.Iterable[Regex]:
        return ()


class One(Regex):
    def get_children(self) -> typing.Iterable[Regex]:
        return ()


class Concat(Regex):
    _children: typing.List[Regex]
    
    def __init__(self, *children: Regex):
        self._children = children
    
    def get_children(self) -> typing.Iterable[Regex]:
        return tuple(self._children)


# TODO: Smart Repeat for optimization?


class Star(Regex):
    _child: Regex
    
    def __init__(self, child: Regex):
        self._child = child
    
    def get_children(self) -> typing.Iterable[Regex]:
        return (self._child,)


class Either(Regex):
    _children: typing.List[Regex]
    
    def __init__(self, *children: Regex):
        self._children = children
    
    def get_children(self) -> typing.Iterable[Regex]:
        return tuple(self._children)


class _RegexParser:
    _src: io.TextIOBase
    
    def __init__(self, src: str | io.TextIOBase):
        if isinstance(src, str):
            src = io.StringIO(src)
        
        self._src = src
