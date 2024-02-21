from pydantic.dataclasses import dataclass
from pydantic import Field
from typing import List, Optional


@dataclass
class CGMLDataNode:
    key: str = Field(alias='@key')
    x: str | None = Field(default=None, alias='@x')
    y: str | None = Field(default=None, alias='@y')
    width: str | None = Field(default=None, alias='@width')
    height: str | None = Field(default=None, alias='@height')


@dataclass
class CGMLKeyNode:
    id: str = Field(alias='@id')
    for_: str = Field(alias='@for')
    attr_name: Optional[str] = Field(default=None, alias='@attr.name')
    attr_type: Optional[str] = Field(default=None, alias='@attr.type')


@dataclass
class CGMLNode:
    id: str = Field(alias='@id')
    data: List[CGMLDataNode] | CGMLDataNode | None = None


@dataclass
class CGMLEdge:
    source: str = Field(alias='@source')
    target: str = Field(alias='@target')
    data: Optional[List[CGMLDataNode] | CGMLDataNode] = None


@dataclass
class CGMLGraph:
    id: str = Field(alias='@id')
    edgedefault: str = Field(alias='@edgedefault')
    node: List[CGMLNode] | CGMLNode | None = None
    edge: List[CGMLEdge] | CGMLEdge | None = None


@dataclass
class CGMLGraphml:
    data: CGMLDataNode
    xmlns: str = Field(alias='@xmlns')
    key: List[CGMLKeyNode] | CGMLKeyNode | None = None
    graph: List[CGMLGraph] | CGMLGraph | None = None


@dataclass
class CGML:
    graphml: CGMLGraphml
