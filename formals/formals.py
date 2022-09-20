from __future__ import annotations
import typing
import argparse
import cmd

from formals_lib import regex, regex_parser


parser = argparse.ArgumentParser(
    description="""
    A tool for various common manipulations related to the formal languages course
    """
)

# parser.add_argument()


def main():
    args = parser.parse_args()

    print(regex.reconstruct(regex_parser.parse("a(bc)*d")))

    return 0


if __name__ == "__main__":
    exit(main())
