from dataclasses import dataclass
from typing import List


@dataclass
class CGMLDataNode:
    _key: str
    _x: str | None
    _y: str | None
    _width: str | None
    _height: str | None


@dataclass
class CGMLKeyNode:
    _id: str
    _for: str
    _attr_name: str
    _atrr_type: str


@dataclass
class CGMLNode:
    _id: str
    data: List[CGMLDataNode] | CGMLDataNode | None


@dataclass
class CGMLEdge:
    _source: str
    _target: str
    data: List[CGMLDataNode] | CGMLDataNode | None


@dataclass
class CGMLGraph:
    _id: str
    node: List[CGMLNode] | CGMLNode | None
    edge: List[CGMLEdge] | CGMLEdge | None


@dataclass
class CGMLGraphml:
    _xmlns: str
    data: CGMLDataNode
    key: List[CGMLKeyNode] | CGMLKeyNode | None
    graph: List[CGMLGraph] | CGMLGraph | None


@dataclass
class CGML:
    graphml: CGMLGraphml
