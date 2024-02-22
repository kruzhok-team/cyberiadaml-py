from dataclasses import dataclass

from typing import TypeAlias


@dataclass
class Point:
    x: float
    y: float


@dataclass
class Rectangle:
    x: float
    y: float
    width: float
    height: float


Key: TypeAlias = str
