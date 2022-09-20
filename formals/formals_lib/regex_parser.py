from __future__ import annotations
from curses import nonl
from tkinter import N
import typing
import io
import dataclasses
import enum

from . import regex


class RegexTokenType(enum.Enum):
    number = enum.auto()
    letter = enum.auto()
    star = enum.auto()
    add = enum.auto()
    lpar = enum.auto()
    rpar = enum.auto()
    pow = enum.auto()


@dataclasses.dataclass
class RegexToken:
    token_type: RegexTokenType
    value: typing.Any = None


class RegexParser:
    _src: io.TextIOBase
    
    def __init__(self, src: str | io.TextIOBase):
        if isinstance(src, str):
            src = io.StringIO(src)
        
        self._src = src
    
    def tokenize(self) -> typing.Generator[RegexToken, None, None]:
        def next_ch():
            nonlocal ch
            ch = self._src.read(1)

        ch: str = ""

        lookup: typing.Final[typing.MappingView] = {
            "*": RegexTokenType.star,
            "+": RegexTokenType.add,
            "(": RegexTokenType.lpar,
            ")": RegexTokenType.rpar,
            "^": RegexTokenType.pow,
        }

        next_ch()
        while ch:
            if ch in lookup:
                yield RegexToken(lookup[ch])
                next_ch()
                continue
            if ch.isdigit():
                raise NotImplementedError()
                continue
            raise NotImplementedError()
            # TODO

            
    
    def parse(self) -> regex.Regex:
        return self.parse_either()

