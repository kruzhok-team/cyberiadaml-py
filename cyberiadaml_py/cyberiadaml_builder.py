"""Module implements building CyberiadaML schemes."""
from typing import Dict, Iterable, List, get_args

from xmltodict import unparse
from pydantic import RootModel

try:
    from cyberiadaml_py.types.cgml_scheme import (
        CGML,
        CGMLDataNode,
        CGMLEdge,
        CGMLGraph,
        CGMLGraphml,
        CGMLKeyNode,
        CGMLNode
    )
    from cyberiadaml_py.types.common import Point, Rectangle
    from cyberiadaml_py.types.elements import (
        AvailableKeys,
        CGMLComponent,
        CGMLElements,
        CGMLInitialState,
        CGMLNote,
        CGMLState,
        CGMLTransition
    )
except ImportError:
    from .types.cgml_scheme import (
        CGML,
        CGMLDataNode,
        CGMLEdge,
        CGMLGraph,
        CGMLGraphml,
        CGMLKeyNode,
        CGMLNode
    )
    from .types.common import Point, Rectangle
    from .types.elements import (
        AvailableKeys,
        CGMLComponent,
        CGMLElements,
        CGMLInitialState,
        CGMLNote,
        CGMLState,
        CGMLTransition
    )


class CGMLBuilderException(Exception):
    """Logical errors during building CGML scheme."""

    ...


class CGMLBuilder:
    """Contains functions to build CGML scheme."""

    def __init__(self) -> None:
        self.scheme: CGML = CGMLBuilder.createEmptyscheme()

    @staticmethod
    def createEmptyscheme() -> CGML:
        """Create empty CyberiadaML scheme."""
        return CGML(graphml=CGMLGraphml(
            [],
            'http://graphml.graphdrawing.org/xmlns',
        ))

    def build(self, elements: CGMLElements) -> str:
        """Build CGML scheme from elements."""
        self.scheme.graphml.key = self._getKeys(elements.keys)
        self.scheme.graphml.data = self._getFormatNode(elements.format)
        self.scheme.graphml.graph = CGMLGraph(
            'directed',
            'G',
        )
        nodes: List[CGMLNode] = [*self._getStateNodes(elements.states),
                                 *self._getNoteNodes(
                                     list(elements.notes.values())),
                                 self._getMetaNode(
                                     elements.meta, elements.platform),
                                 *self._getComponentsNodes(elements.components)
                                 ]
        edges: List[CGMLEdge] = [
            *self._getEdges(elements.transitions),
            *self._getComponentsEdges(elements.components)
        ]
        if elements.initial_state is not None:
            nodes.append(
                self._getInitialNode(elements.initial_state))
            edges.append(self._getInitialEdge(
                elements.initial_state.transitionId,
                elements.initial_state.id,
                elements.initial_state.target))
        self.scheme.graphml.graph.node = nodes
        self.scheme.graphml.graph.edge = edges
        scheme: CGML = RootModel[CGML](self.scheme).model_dump(
            by_alias=True, exclude_defaults=True)
        # У model_dump неправильный возвращаемый тип (CGML),
        # поэтому приходится явно показывать линтеру, что это dict
        if isinstance(scheme, dict):
            return unparse(scheme, pretty=True)
        else:
            raise CGMLBuilderException('Internal error: scheme is not dict')

    def _getComponentsEdges(self,
                            components: List[CGMLComponent]) -> List[CGMLEdge]:
        edges: List[CGMLEdge] = []
        for component in components:
            edges.append(CGMLEdge(f'edge_{component.id}', '', component.id))
        return edges

    def _getComponentsNodes(self,
                            components: List[CGMLComponent]) -> List[CGMLNode]:
        nodes: List[CGMLNode] = []
        for component in components:
            node: CGMLNode = CGMLNode(component.id)
            data: List[CGMLDataNode] = []
            data.append(self._nameToData(component.id))
            data.append(self._actionsToData(component.parameters))
            node.data = data
            nodes.append(node)
        return nodes

    def _getInitialEdge(self, transitionId: str,
                        initId: str, target: str) -> CGMLEdge:
        return CGMLEdge(
            transitionId,
            initId,
            target
        )

    def _getEdges(self,
                  transitions: Dict[str, CGMLTransition]) -> List[CGMLEdge]:
        edges: List[CGMLEdge] = []
        for transition in list(transitions.values()):
            edge: CGMLEdge = CGMLEdge(
                transition.id, transition.source, transition.target)
            data: List[CGMLDataNode] = []
            data.append(self._actionsToData(transition.actions))
            if transition.color is not None:
                data.append(self._colorToData(transition.color))
            if transition.position is not None:
                data.append(self._pointToData(transition.position))
            data.extend(transition.unknownDatanodes)
            edge.data = data
            edges.append(edge)
        return edges

    def _getInitialNode(self, initialState: CGMLInitialState) -> CGMLNode:
        initialNode: CGMLNode = CGMLNode(initialState.id)
        data: List[CGMLDataNode] = []
        if initialState.position is not None:
            data.append(self._pointToData(initialState.position))
        data.append(self._getInitialDataNode())
        initialNode.data = data
        return initialNode

    def _getInitialDataNode(self) -> CGMLDataNode:
        return CGMLDataNode(
            'dInitial'
        )

    def _getMetaNode(self, meta: str, platform: str) -> CGMLNode:
        metaNode: CGMLNode = CGMLNode('')
        data: List[CGMLDataNode] = []
        data.append(self._nameToData(platform))
        data.append(self._actionsToData(meta))
        metaNode.data = data
        return metaNode

    def _getNoteNodes(self, notes: List[CGMLNote]) -> List[CGMLNode]:
        nodes: List[CGMLNode] = []
        for note in notes:
            data: List[CGMLDataNode] = []
            data.append(self._noteToData(note.text))
            data.append(self._pointToData(note.position))
            data.extend(note.unknownDatanodes)
            nodes.append(CGMLNode(
                note.id,
                data=data
            ))
        return nodes

    def _pointToData(self, point: Point) -> CGMLDataNode:
        return CGMLDataNode(
            'dGeometry', None, str(point.x), str(point.y)
        )

    def _noteToData(self, note_information: str) -> CGMLDataNode:
        return CGMLDataNode('dNote', note_information)

    def _getStateNodes(self, states: Dict[str, CGMLState]) -> List[CGMLNode]:
        def _getCGMLNode(nodes: Dict[str, CGMLNode],
                         state: CGMLState, stateId: str) -> CGMLNode:
            if nodes.get(stateId) is not None:
                return nodes[stateId]
            else:
                node = CGMLNode(stateId)
                data: List[CGMLDataNode] = []
                if state.bounds is not None:
                    data.append(self._boundsToData(state.bounds))
                if state.color is not None:
                    data.append(self._colorToData(state.color))
                data.append(self._actionsToData(state.actions))
                data.append(self._nameToData(state.name))
                data.extend(state.unknownDatanodes)
                node.data = data
                return node

        nodes: Dict[str, CGMLNode] = {}
        for stateId in list(states.keys()):
            state: CGMLState = states[stateId]
            node: CGMLNode = _getCGMLNode(nodes, state, stateId)
            if state.parent is not None:
                parentState: CGMLState = states[state.parent]
                parent: CGMLNode = _getCGMLNode(
                    nodes, parentState, state.parent)
                if parent.graph is None:
                    parent.graph = CGMLGraph(
                        node=[node]
                    )
                elif isinstance(parent.graph, CGMLGraph):
                    if (parent.graph.node is not None and
                            isinstance(parent.graph.node, Iterable)):
                        parent.graph.node.append(node)
                    else:
                        parent.graph.node = [node]
                nodes[state.parent] = parent
            else:
                nodes[stateId] = node
        return list(nodes.values())

    def _nameToData(self, name: str) -> CGMLDataNode:
        return CGMLDataNode('dName', name)

    def _colorToData(self, color: str) -> CGMLDataNode:
        return CGMLDataNode('dColor', color)

    def _actionsToData(self, actions: str) -> CGMLDataNode:
        return CGMLDataNode(
            'dData', actions
        )

    def _boundsToData(self, bounds: Rectangle) -> CGMLDataNode:
        return CGMLDataNode('dGeometry',
                            None,
                            str(bounds.x),
                            str(bounds.y),
                            str(bounds.width),
                            str(bounds.height))

    def _getFormatNode(self, format: str) -> CGMLDataNode:
        return CGMLDataNode('gFormat', format)

    def _getKeys(self, awaialaibleKeys: AvailableKeys) -> List[CGMLKeyNode]:
        keyNodes: List[CGMLKeyNode] = []
        for key in list(awaialaibleKeys.keys()):
            keyNodes.extend(awaialaibleKeys[key])

        return keyNodes
