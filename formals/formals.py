from __future__ import annotations
from re import L
import typing
import argparse
import cmd
import pathlib

from formals_lib import *


parser = argparse.ArgumentParser(
    description="""
    A tool for various common manipulations related to the formal languages course
    """
)

# parser.add_argument()


def test_regex():
    data = "a(bc)*d"  # + " + (e+f)^5"
    print(regex.reconstruct(regex_parser.parse()))


def test_automata():
    aut = automata.Automata("abcd")
    q0 = aut.start
    q1 = aut.make_node()
    q2 = aut.make_node(term=True)

    aut.link(q0, q1, "a")
    aut.link(q1, q1, "bc")
    aut.link(q1, q2, "d")

    automata_dot.dump(aut, pathlib.Path("~/Desktop/automata.svg").expanduser())


def main():
    args = parser.parse_args()

    # test_regex()
    test_automata()

    return 0


if __name__ == "__main__":
    exit(main())
