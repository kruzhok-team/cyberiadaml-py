"""Module contains types, that representing unprocessed CyberiadaML scheme."""

from typing import List, Optional

from pydantic.dataclasses import dataclass
from pydantic import Field, ConfigDict


@dataclass(config=ConfigDict(extra='forbid'))
class CGMLDataNode:
    """Type representing <data> node."""

    key: str = Field(alias='@key')
    content: Optional[str] = Field(default=None, alias='#text')
    x: Optional[str] = Field(default=None, alias='@x')
    y: Optional[str] = Field(default=None, alias='@y')
    width: Optional[str] = Field(default=None, alias='@width')
    height: Optional[str] = Field(default=None, alias='@height')


@dataclass(config=ConfigDict(extra='forbid'))
class CGMLKeyNode:
    """Type representing <key> node."""

    id: str = Field(alias='@id')
    for_: str = Field(alias='@for')
    attr_name: Optional[str] = Field(default=None, alias='@attr.name')
    attr_type: Optional[str] = Field(default=None, alias='@attr.type')


@dataclass(config=ConfigDict(extra='forbid'))
class CGMLEdge:
    """Type representing <edge> node."""

    source: str = Field(alias='@source')
    target: str = Field(alias='@target')
    data: Optional[List[CGMLDataNode] | CGMLDataNode] = None


@dataclass(config=ConfigDict(extra='forbid'))
class CGMLGraph:
    """Type representing <graph> node."""

    edgedefault: Optional[str] = Field(alias='@edgedefault', default=None)
    id: Optional[str] = Field(alias='@id', default=None)
    node: Optional[List['CGMLNode'] | 'CGMLNode'] = None
    edge: Optional[List[CGMLEdge] | CGMLEdge] = None


@dataclass(config=ConfigDict(extra='forbid'))
class CGMLNode:
    """Type representing <node> node."""

    id: str = Field(alias='@id')
    graph: Optional[CGMLGraph | List[CGMLGraph]] = None
    data: List[CGMLDataNode] | CGMLDataNode | None = None


@dataclass(config=ConfigDict(extra='forbid'))
class CGMLGraphml:
    """Type representing <graphml> node."""

    data: CGMLDataNode | List[CGMLDataNode]
    xmlns: str = Field(alias='@xmlns')
    key: Optional[List[CGMLKeyNode] | CGMLKeyNode] = None
    graph: Optional[List[CGMLGraph] | CGMLGraph] = None


@dataclass(config=ConfigDict(extra='forbid'))
class CGML:
    """Root type of CyberiadaML scheme."""

    graphml: CGMLGraphml
