"""XMLTV Model."""

from .channel import TVChannel
from .program import TVProgram
from .guide import TVGuide

__all__ = [
    "TVChannel",
    "TVProgram",
    "TVGuide",
]
