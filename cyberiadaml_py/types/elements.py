from pydantic.dataclasses import dataclass
from typing import (
    List,
    Dict,
    DefaultDict,
    Optional,
    TypeAlias
)

from .cgml_schema import CGMLDataNode
from .common import Point, Rectangle

#  { node: ['dGeometry', ...], edge: ['dData', ...]}
AwailableKeys: TypeAlias = DefaultDict[str, List[str]]


@dataclass
class CGMLState:
    name: str
    actions: str
    unknownDatanodes: List[CGMLDataNode]
    bounds: Rectangle
    parent: Optional[str] = None


@dataclass
class CGMLComponent:
    id: str
    parameters: str


@dataclass
class CGMLInitialState:
    id: str
    target: str
    position: Optional[Point] = None


@dataclass
class CGMLTransition:
    source: str
    target: str
    actions: str
    color: Optional[str]
    position: Optional[Point]
    unknownDatanodes: List[CGMLDataNode]


@dataclass
class CGMLElements:
    states: Dict[str, CGMLState]
    transitions: List[CGMLTransition]
    components: List[CGMLComponent]
    platform: str
    meta: str
    format: str
    keys: AwailableKeys
    initial_state: Optional[CGMLInitialState] = None
