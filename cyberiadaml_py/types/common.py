"""Module contains common geometry classes."""
from dataclasses import dataclass
from typing import Optional, TypeAlias


@dataclass
class Point:
    """Point data class."""

    x: float
    y: float


@dataclass
class Rectangle:
    """Rectangle data class."""

    x: float
    y: float
    width: Optional[float] = None
    height: Optional[float] = None


Key: TypeAlias = str
