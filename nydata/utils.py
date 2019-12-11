# -*- coding: utf-8 -*-
"""Helper utilities and decorators."""
import re
import sys
from typing import Callable, Dict, TypeVar

# Generic Type variable
T = TypeVar("T")

#                       params   generic return_type
TransformerFn = Callable[[Dict], T]


def extract_and_transform(
    pattern: re.Pattern, transform: TransformerFn, line: str
) -> T:
    """
    Extract something out of a string and transform it.
    """
    matched = pattern.match(line)

    if matched is None:
        return None

    extracted = matched.groupdict()
    return transform(extracted)


def eprint(*args, **kwargs):
    """
    Print to standard error
    """
    print(*args, file=sys.stderr, **kwargs)
