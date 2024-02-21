from dataclasses import dataclass


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
