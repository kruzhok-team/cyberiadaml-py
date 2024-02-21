from dataclasses import dataclass
from typing import List, Dict

from .cgml_schema import CGMLKeyNode, CGMLDataNode
from .common import Point


@dataclass
class Rectangle:
    x: float
    y: float
    width: float
    height: float


@dataclass
class CGMLState:
    name: str
    actions: str
    parent: str | None
    unknownDatanodes: List[CGMLDataNode]
    bounds: Rectangle


@dataclass
class CGMLComponent:
    id: str
    parameters: str


@dataclass
class CGMLInitialState:
    position: Point | None
    id: str
    target: str


@dataclass
class CGMLTransition:
    source: str
    target: str
    actions: str
    color: str | None
    position: Point | None
    unknownDatanodes: List[CGMLDataNode]


@dataclass
class CGMLElements:
    states: Dict[str, CGMLState]
    transitions: List[CGMLTransition]
    components: List[CGMLComponent]
    initial_state: CGMLInitialState | None
    platform: str
    meta: str
    format: str
    keys: List[CGMLKeyNode]
