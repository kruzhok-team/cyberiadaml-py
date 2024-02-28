"""Module containing the types of schema elements."""
from typing import (
    List,
    Dict,
    DefaultDict,
    Optional,
    TypeAlias
)

from pydantic.dataclasses import dataclass
from pydantic import Field

try:
    from .cgml_scheme import CGMLDataNode, CGMLKeyNode
    from .common import Point, Rectangle
except ImportError:
    from cyberiadaml_py.types.cgml_scheme import CGMLDataNode, CGMLKeyNode
    from cyberiadaml_py.types.common import Point, Rectangle
#  { node: ['dGeometry', ...], edge: ['dData', ...]}
AwailableKeys: TypeAlias = DefaultDict[str, List[CGMLKeyNode]]


@dataclass
class CGMLState:
    name: str
    actions: str
    unknownDatanodes: List[CGMLDataNode]
    parent: Optional[str] = None
    bounds: Optional[Rectangle] = None
    color: Optional[str] = None


@dataclass
class CGMLComponent:
    id: str
    parameters: str


@dataclass
class CGMLInitialState:
    """
    Data class with information about initial state (pseudo node).

    Intiial state is <node>, that contains data node with key 'dInitial'.
    id: state's id.
    target: state's id, thats connetcted with initial state\
        (<edge source="initial state id" target="target state's id">)
    position: x, y properties of data node with 'dGeometry' key.
    """

    id: str
    target: str
    position: Optional[Point] = None


@dataclass
class CGMLTransition:
    """
    Data class with information about transition(<edge>).

    source: <edge> source property's content.
    target: <edge> target property's content.
    actions: content of data node with 'dData' key.
    color: content of data node with 'dColor' key.
    position: x, y properties of data node with 'dGeometry' key.
    unknownDatanodes: all datanodes, whose information\
    is not included in the type.
    """

    source: str
    target: str
    actions: str
    unknownDatanodes: List[CGMLDataNode]
    color: Optional[str] = None
    position: Optional[Point] = None


@dataclass
class CGMLNote:
    """
    Dataclass with infromation about note.

    Note is <node> containing data node with key 'dNote'
    unknownDatanodes: all datanodes, whose information\
        is not included in the type.
    """

    position: Point
    text: str
    unknownDatanodes: List[CGMLDataNode]
    id: str = Field(serialization_alias='@id')


@dataclass
class CGMLElements:
    """
    Dataclass with elements of parsed scheme.

    Contains dict of states, where the key is state's id.
    Also contains trainstions, components, awaialable keys, notes.

    meta: content of data node\
        with key 'dData' inside <node id="">

    format: content of data node with key 'gFormat'.

    platform: content of data node with key 'dName'\
        inside <node id="">

    States doesn't contains components nodes and initial state.

    Transitions doesn't contains edges from meta-node(with id='')\
        to components nodes.
    """

    states: Dict[str, CGMLState]
    transitions: List[CGMLTransition]
    components: List[CGMLComponent]
    platform: str
    meta: str
    format: str
    keys: AwailableKeys
    notes: List[CGMLNote]
    initial_state: Optional[CGMLInitialState] = None
