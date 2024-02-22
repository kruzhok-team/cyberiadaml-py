from pydantic.dataclasses import dataclass
from pydantic import Field
from typing import List, Optional


@dataclass
class CGMLDataNode:
    key: str = Field(alias='@key')
    content: Optional[str] = Field(default=None, alias='#text')
    x: Optional[str] = Field(default=None, alias='@x')
    y: Optional[str] = Field(default=None, alias='@y')
    width: Optional[str] = Field(default=None, alias='@width')
    height: Optional[str] = Field(default=None, alias='@height')


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
    node: Optional[List[CGMLNode] | CGMLNode] = None
    edge: Optional[List[CGMLEdge] | CGMLEdge] = None


@dataclass
class CGMLGraphml:
    data: CGMLDataNode | List[CGMLDataNode]
    xmlns: str = Field(alias='@xmlns')
    key: Optional[List[CGMLKeyNode] | CGMLKeyNode] = None
    graph: Optional[List[CGMLGraph] | CGMLGraph] = None


@dataclass
class CGML:
    graphml: CGMLGraphml
