from dataclasses import dataclass
from typing import Optional, TypeAlias


@dataclass
class Point:
    x: float
    y: float


@dataclass
class Rectangle:
    x: float
    y: float
    width: Optional[float] = None
    height: Optional[float] = None


Key: TypeAlias = str
