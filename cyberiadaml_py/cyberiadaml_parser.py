"""The module implements parsing CyberiadaML schemes."""
from collections import defaultdict
from collections.abc import Iterable
from typing import Any, Dict, List, Optional

from xmltodict import parse

from cyberiadaml_py.types.elements import CGMLMeta

try:
    from .types.common import Point, Rectangle
    from .types.cgml_scheme import (
        CGML,
        CGMLDataNode,
        CGMLEdge,
        CGMLGraph,
        CGMLNode
    )
    from .types.elements import (
        CGMLComponent,
        CGMLElements,
        AwailableKeys,
        CGMLInitialState,
        CGMLNote,
        CGMLState,
        CGMLTransition
    )
except ImportError:
    from cyberiadaml_py.types.cgml_scheme import (
        CGML,
        CGMLDataNode,
        CGMLEdge,
        CGMLGraph,
        CGMLNode
    )
    from cyberiadaml_py.types.common import Point, Rectangle
    from cyberiadaml_py.types.elements import (
        CGMLComponent,
        CGMLElements,
        AwailableKeys,
        CGMLInitialState,
        CGMLNote,
        CGMLState,
        CGMLTransition
    )


class CGMLParserException(Exception):
    """Logical errors during parsing CGML scheme."""

    ...


class CGMLParser:
    """Class that contains functions for parsing CyberiadaML."""

    def __init__(self) -> None:
        self.elements: CGMLElements = CGMLParser.createEmptyElements()

    @staticmethod
    def createEmptyElements() -> CGMLElements:
        """Create CGMLElements with empty fields."""
        return CGMLElements(
            states={},
            transitions={},
            finals={},
            choices={},
            initial_states={},
            standardVersion='',
            components=[],
            platform='',
            format='',
            meta=CGMLMeta(
                id='',
                values={},
            ),
            keys=defaultdict(),
            notes={},
        )

    def parseCGML(self, graphml: str) -> CGMLElements:
        """
        Parse CyberiadaGraphml scheme.

        Args:
            graphml (str): CyberiadaML scheme.

        Returns:
            CGMLElements: notes, states, transitions,\
                initial state and components
        Raises:
            CGMLParserException('Data node with key "gFormat" is empty'):\
                content of <data key='gFormat'> is None
            CGMLParserException('Data node with key "gFormat" is missing'):\
                <data key='gFormat'> doesn't exist in graphml->data.s
            CGMLParserException('No position for note!):\
                <node>, that contains <data key='dNote'>, graphml
                    doesn't contains <data key='dGeometry' x='...' y='...'>
            CGMLParserException('Unknown key "key" for "node-type",\
                                    did you forgot ...'):\
                                        using an undeclarated key
            CGMLParserException('<node-type> with key\
                dGeometry doesnt have x, y properties'): \
                    <data key='dGeometry'> must contain at least x and y\
                        properties (width and height are additional)
            ValidationError(...): pydatinc's validation error, occurs when\
                the scheme doesn't match the format.
        """
        self.elements = CGMLParser.createEmptyElements()
        cgml = CGML(**parse(graphml))
        self.elements.format = self._getFormat(cgml)
        if self.elements.format != 'Cyberiada-GraphML':
            raise CGMLParserException(
                ('Format must be '
                 f'Cyberiada-GraphML, but got {self.elements.format}'))
        self.elements.keys = self._getAwaialbleKeys(cgml)
        graphs: List[CGMLGraph] = self._toList(cgml.graphml.graph)
        states: Dict[str, CGMLState] = {}
        transitions: Dict[str, CGMLTransition] = {}
        notes: Dict[str, CGMLNote] = {}
        for graph in graphs:
            states = states | self._parseGraphNodes(graph)
            transitions = transitions | self._parseGraphEdges(graph)
        try:
            self.elements.platform, self.elements.meta = self._getMeta(
                states[''])
            del states['']
        except KeyError:
            raise CGMLParserException('Meta node is missing')
        for stateId in list(states.keys()):
            state, isInit = self._processStateData(states[stateId], stateId)
            if isinstance(state, CGMLNote):
                notes[state.id] = state
                del states[stateId]
            elif isinstance(state, CGMLState):
                if isInit:
                    if self.elements.initial_state is not None:
                        raise CGMLParserException('Double init states')
                    position: Point | None = None
                    if state.bounds is not None:
                        position = Point(state.bounds.x, state.bounds.y)
                    self.elements.initial_state = CGMLInitialState(
                        transitionId='', id=stateId,
                        target='', position=position)
                    del states[stateId]
                else:
                    states[stateId] = state
            else:
                raise CGMLParserException(
                    'Internal error: Unknown type of node')
        # TODO Вынести в отдельные функции
        componentIds: List[str] = []
        for transition in list(transitions.values()):
            processedTransition: CGMLTransition = self._processEdgeData(
                transition)
            if (self.elements.initial_state is not None and
                    (processedTransition.source ==
                        self.elements.initial_state.id)):
                self.elements.initial_state.target = processedTransition.target
                self.elements.initial_state\
                    .transitionId = processedTransition.id
            elif transition.source == '':
                componentIds.append(transition.target)
            else:
                self.elements.transitions[transition.id] = processedTransition
        for componentId in componentIds:
            componentState: CGMLState | None = states.get(componentId)
            if componentState is None:
                raise CGMLParserException('Unknown component node')
            self.elements.components.append(CGMLComponent(
                id=componentId,
                parameters=componentState.actions
            ))  # TODO: raise exception if smth else
            del states[componentId]
        self.elements.states = states
        self.elements.notes = notes
        return self.elements

    def _getDataContent(self, dataNode: CGMLDataNode) -> str:
        return dataNode.content if dataNode.content is not None else ''

    def _processEdgeData(self, transition: CGMLTransition) -> CGMLTransition:
        newTransition = CGMLTransition(
            id=transition.id,
            source=transition.source,
            target=transition.target,
            actions=transition.actions,
            unknownDatanodes=[]
        )
        for dataNode in transition.unknownDatanodes:
            for keyNode in self.elements.keys['edge']:
                if dataNode.key == keyNode.id:
                    break
            else:
                raise CGMLParserException(
                    (f'Unknown key {dataNode.key} for edge, did you forgot: '
                     f'"<key id="{dataNode.key}" for="edge"/>"?'))
            match dataNode.key:
                case 'dData':
                    newTransition.actions = self._getDataContent(dataNode)
                case 'dGeometry':
                    if dataNode.x is None or dataNode.y is None:
                        raise CGMLParserException(
                            'Edge with key dGeometry\
                                doesnt have x, y properties')
                    newTransition.position = Point(
                        float(dataNode.x), float(dataNode.y))
                case 'dColor':
                    newTransition.color = self._getDataContent(dataNode)
                case _:
                    newTransition.unknownDatanodes.append(dataNode)
        return newTransition

    def _processStateData(self,
                          state: CGMLState,
                          stateId: str) -> tuple[CGMLState | CGMLNote, bool]:
        """Return tuple[CGMLState | CGMLNote, isInit]."""
        # no mutations? B^)
        newState = CGMLState(
            name=state.name,
            actions=state.actions,
            unknownDatanodes=[],
            bounds=state.bounds,
            parent=state.parent
        )
        isNote: bool = False
        isInit: bool = False
        for dataNode in state.unknownDatanodes:
            match dataNode.key:
                case 'dName':
                    newState.name = self._getDataContent(dataNode)
                case 'dGeometry':
                    if dataNode.x is None or dataNode.y is None:
                        raise CGMLParserException(
                            'Node with key dGeometry\
                                doesnt have x, y properties')
                    x: float = float(dataNode.x)
                    y: float = float(dataNode.y)

                    if (dataNode.width is not None and
                            dataNode.height is not None):
                        newState.bounds = Rectangle(
                            x=x,
                            y=y,
                            width=float(dataNode.width),
                            height=float(dataNode.height)
                        )
                    else:
                        newState.bounds = Rectangle(
                            x=x,
                            y=y
                        )
                case 'dData':
                    newState.actions = self._getDataContent(dataNode)
                case 'dNote':
                    isNote = True
                    newState.actions = self._getDataContent(dataNode)
                case 'dInitial':
                    isInit = True
                    if isNote:
                        raise CGMLParserException('dInit in dNote')
                case 'dColor':
                    newState.color = self._getDataContent(dataNode)
                case _:
                    newState.unknownDatanodes.append(dataNode)
        if isNote:
            bounds: Rectangle | None = newState.bounds
            if bounds is None:
                raise CGMLParserException('No position for note!')
            else:
                return (CGMLNote(
                    id=stateId,
                    position=Point(
                        x=bounds.x,
                        y=bounds.y,
                    ),
                    text=newState.actions,
                    unknownDatanodes=newState.unknownDatanodes
                ), False)
        return (newState, isInit)

    def _getMeta(self, metaNode: CGMLState) -> tuple[str, str]:
        """Return tuple[platfrom, meta]."""
        dataNodes: List[CGMLDataNode] = self._toList(metaNode.unknownDatanodes)
        platform: str = ''
        meta: str = ''
        for dataNode in dataNodes:
            match dataNode.key:
                case 'dName':
                    platform = self._getDataContent(dataNode)
                case 'dData':
                    meta = self._getDataContent(dataNode)
        return platform, meta

    def _toList(self, nodes: List | None | Any) -> List:
        if nodes is None:
            return []
        if isinstance(nodes, list):
            return nodes
        else:
            return [nodes]

    def _parseGraphEdges(self, root: CGMLGraph) -> Dict[str, CGMLTransition]:
        def _parseEdge(edge: CGMLEdge,
                       cgmlTransitions: Dict[str, CGMLTransition]) -> None:
            cgmlTransitions[edge.id] = CGMLTransition(
                id=edge.id,
                source=edge.source,
                target=edge.target,
                actions='',
                unknownDatanodes=self._toList(
                        edge.data),
            )

        cgmlTransitions: Dict[str, CGMLTransition] = {}
        if root.edge is not None:
            if isinstance(root.edge, Iterable):
                for edge in root.edge:
                    _parseEdge(edge, cgmlTransitions)
            else:
                _parseEdge(root.edge, cgmlTransitions)
        return cgmlTransitions

    def _parseGraphNodes(self,
                         root: CGMLGraph,
                         parent: Optional[str] = None) -> Dict[str, CGMLState]:
        def parseNode(node: CGMLNode) -> Dict[str, CGMLState]:
            cgmlStates: Dict[str, CGMLState] = {}
            cgmlStates[node.id] = CGMLState(
                name='',
                actions='',
                unknownDatanodes=self._toList(node.data),
            )
            if parent is not None:
                cgmlStates[node.id].parent = parent
            graphs: List[CGMLGraph] = self._toList(node.graph)
            for graph in graphs:
                cgmlStates = cgmlStates | self._parseGraphNodes(
                    graph, node.id)

            return cgmlStates

        cgmlStates: Dict[str, CGMLState] = {}
        if root.node is not None:
            if isinstance(root.node, Iterable):
                for node in root.node:
                    cgmlStates = cgmlStates | parseNode(node)
            else:
                cgmlStates = cgmlStates | parseNode(root.node)
        return cgmlStates

    def _checkDataNodeKey(self, node_name: str, key: str,
                          awaialableKeys: AwailableKeys) -> bool:
        return key in awaialableKeys[node_name]

    # key nodes to comfortable dict
    def _getAwaialbleKeys(self, cgml: CGML) -> AwailableKeys:
        keyNodeDict: AwailableKeys = defaultdict(lambda: [])
        if cgml.graphml.key is not None:
            if isinstance(cgml.graphml.key, Iterable):
                for keyNode in cgml.graphml.key:
                    keyNodeDict[keyNode.for_].append(keyNode)
            else:
                keyNodeDict[cgml.graphml.key.for_].append(cgml.graphml.key)
        return keyNodeDict

    def _getFormat(self, cgml: CGML) -> str:
        # TODO: DRY
        if isinstance(cgml.graphml.data, Iterable):
            for dataNode in cgml.graphml.data:
                if dataNode.key == 'gFormat':
                    if dataNode.content is not None:
                        return dataNode.content
                    raise CGMLParserException(
                        'Data node with key "gFormat" is empty')
        else:
            if cgml.graphml.data.key == 'gFormat':
                if cgml.graphml.data.content is not None:
                    return cgml.graphml.data.content
                raise CGMLParserException(
                    'Data node with key "gFormat" is empty')
        raise CGMLParserException('Data node with key "gFormat" is missing')
