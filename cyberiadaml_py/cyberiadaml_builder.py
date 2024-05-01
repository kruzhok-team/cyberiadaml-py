"""Module implements building CyberiadaML schemes."""
from typing import Dict, Iterable, List, Mapping
from copy import deepcopy
from itertools import chain

from xmltodict import unparse
from pydantic import RootModel
from cyberiadaml_py.types.cgml_scheme import (
    CGMLNode,
    CGMLPointNode,
    CGMLRectNode,
    CGML,
    CGMLDataNode,
    CGMLEdge,
    CGMLGraph,
    CGMLGraphml,
    CGMLKeyNode,
)
from cyberiadaml_py.types.elements import (
    CGMLBaseVertex,
    CGMLInitialState,
    CGMLMeta,
    CGMLNoteType,
    CGMLVertexType,
    AvailableKeys,
    CGMLComponent,
    CGMLElements,
    CGMLNote,
    CGMLState,
    CGMLTransition,
    Vertex
)
from cyberiadaml_py.types.common import Point, Rectangle
from cyberiadaml_py.utils import to_list


class CGMLBuilderException(Exception):
    """Logical errors during building CGML scheme."""

    ...


class CGMLBuilder:
    """Contains functions to build CGML scheme."""

    def __init__(self) -> None:
        self.scheme: CGML = CGMLBuilder.create_empty_scheme()

    @staticmethod
    def create_empty_scheme() -> CGML:
        """Create empty CyberiadaML scheme."""
        return CGML(graphml=CGMLGraphml(
            [],
            'http://graphml.graphdrawing.org/xmlns',
        ))

    def _get_state_machine_datanode(self) -> CGMLDataNode:
        return CGMLDataNode('dStateMachine')

    def build(self, elements: CGMLElements) -> str:
        """Build CGML scheme from elements."""
        self.scheme.graphml.key = self._get_keys(elements.keys)
        self.scheme.graphml.data = self._get_format_node(elements.format)
        self.scheme.graphml.graph = CGMLGraph(
            'directed',
            'G',
            data=self._get_state_machine_datanode()
        )
        cgml_states: Dict[str, CGMLNode] = self._get_state_nodes(
            elements.states)
        initials: List[CGMLNode] = self._get_vertex_nodes(
            elements.initial_states, 'initial')
        finals: List[CGMLNode] = self._get_vertex_nodes(
            elements.finals, 'final')
        terminates: List[CGMLNode] = self._get_vertex_nodes(
            elements.terminates, 'terminate')
        choices: List[CGMLNode] = self._get_vertex_nodes(
            elements.choices, 'choice'
        )
        vertexes: Dict[str, Vertex] = (
            elements.finals |
            elements.choices |
            elements.initial_states |
            elements.terminates
        )
        vertexes_nodes: List[CGMLNode] = list(
            chain(initials, finals, terminates, choices))
        states_with_vertexes, independent_vertexes = (
            self._add_vertexes_to_states(
                vertexes_nodes, vertexes, cgml_states)
        )
        nodes: List[CGMLNode] = [
            *independent_vertexes,
            *states_with_vertexes.values(),
            self._get_meta_node(
                elements.meta,
                elements.platform,
                elements.standard_version
            ),
            *self._get_components_nodes(elements.components),
            *self._get_note_nodes(elements.notes)
        ]
        edges: List[CGMLEdge] = self._get_edges(elements.transitions)
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

    def _get_vertex_nodes(self, vertexes: Mapping[str, Vertex],
                          vertex_type: CGMLVertexType) -> List[CGMLNode]:
        vertex_nodes: List[CGMLNode] = []
        for vertex_id, vertex in vertexes.items():
            vertex_node: CGMLNode = CGMLNode(vertex_id)
            data: List[CGMLDataNode] = []
            data.append(self._get_vertex_datanode(vertex_type))
            if isinstance(vertex.position, Point):
                data.append(self._point_to_data(vertex.position))
            elif isinstance(vertex.position, Rectangle):
                data.append(self._bounds_to_data(vertex.position))
            vertex_node.data = data
            vertex_nodes.append(vertex_node)
        return vertex_nodes

    def _add_vertexes_to_states(
        self,
        vertex_nodes: List[CGMLNode],
        vertexes: Dict[str, Vertex],
        cgml_states: Dict[str, CGMLNode]
    ) -> tuple[Dict[str, CGMLNode], List[CGMLNode]]:
        new_states = deepcopy(cgml_states)
        independent_vertexes: List[CGMLNode] = []
        for node in vertex_nodes:
            vertex: CGMLBaseVertex = vertexes[node.id]
            if vertex.parent is None:
                independent_vertexes.append(node)
                continue
            parent_node: CGMLNode = new_states[vertex.parent]
            if parent_node.graph is None:
                parent_node.graph = CGMLGraph(
                    f'g{parent_node.id}', node=[node])
                continue
            if isinstance(parent_node.graph, CGMLGraph):
                graph_nodes = to_list(parent_node.graph.node)
                graph_nodes.append(node)
                parent_node.graph.node = graph_nodes
            new_states[vertex.parent] = parent_node
        return new_states, independent_vertexes

    def _get_components_nodes(self,
                              components: Dict[str, CGMLComponent]
                              ) -> List[CGMLNode]:
        nodes: List[CGMLNode] = []
        for component_id, component in components.items():
            node: CGMLNode = CGMLNode(component_id)
            data: List[CGMLDataNode] = []
            data.append(self._get_note_datanode('formal'))
            data.append(self._name_to_data('CGML_COMPONENT'))
            str_parameters = self._get_actions_string(
                component.parameters | {'id': component.id,
                                        'type': component.type
                                        }
            )
            data.append(self._actions_to_data(str_parameters))
            node.data = data
            nodes.append(node)
        return nodes

    def _get_edges(self,
                   transitions: Dict[str, CGMLTransition]) -> List[CGMLEdge]:
        edges: List[CGMLEdge] = []
        for transition in list(transitions.values()):
            edge: CGMLEdge = CGMLEdge(
                transition.id, transition.source, transition.target)
            data: List[CGMLDataNode] = []
            data.append(self._actions_to_data(transition.actions))
            if transition.color is not None:
                data.append(self._colorToData(transition.color))
            if isinstance(transition.position, Point):
                data.append(self._point_to_data(transition.position))
            if isinstance(transition.label_position, Point):
                data.append(self._point_label(transition.label_position))
            data.extend(transition.unknown_datanodes)
            edge.data = data
            edges.append(edge)
        return edges

    def _get_vertex_datanode(
            self,
            vertex_type: CGMLVertexType
    ) -> CGMLDataNode:
        return CGMLDataNode('dVertex', vertex_type)

    def _get_initial_nodes(
            self,
            initial_states: Dict[str, CGMLInitialState]
    ) -> List[CGMLNode]:
        initial_nodes: List[CGMLNode] = []
        for initial_id, initial_state in initial_states.items():
            initial_node: CGMLNode = CGMLNode(initial_id)
            data: List[CGMLDataNode] = []
            data.append(self._get_vertex_datanode('initial'))
            if isinstance(initial_state.position, Point):
                data.append(self._point_to_data(initial_state.position))
            elif isinstance(initial_state.position, Rectangle):
                data.append(self._bounds_to_data(initial_state.position))
            initial_node.data = data
            initial_nodes.append(initial_node)
        return initial_nodes

    def _get_actions_string(self, values: Dict[str, str]) -> str:
        parameters = ''
        for name, value in values.items():
            parameters += f'{name}/{value}\n\n'
        return parameters

    def _get_note_datanode(self, note_type: CGMLNoteType) -> CGMLDataNode:
        return CGMLDataNode('dNote', note_type)

    def _get_meta_node(
        self,
        meta: CGMLMeta,
        platform: str,
        standard_version: str
    ) -> CGMLNode:
        meta_node: CGMLNode = CGMLNode(meta.id)
        data: List[CGMLDataNode] = []
        meta_parameters: str = self._get_actions_string(
            meta.values | {
                'platform': platform,
                'standardVersion': standard_version
            }
        )
        print(meta_parameters)
        data.append(self._get_note_datanode('formal'))
        data.append(self._name_to_data('CGML_META'))
        data.append(self._actions_to_data(meta_parameters))
        meta_node.data = data
        return meta_node

    def _get_note_nodes(self, notes: Dict[str, CGMLNote]) -> List[CGMLNode]:
        nodes: List[CGMLNode] = []
        for note_id, note in notes.items():
            data: List[CGMLDataNode] = []
            data.append(self._get_note_datanode('informal'))
            data.append(self._actions_to_data(note.text))
            if isinstance(note.position, Point):
                data.append(self._point_to_data(note.position))
            else:
                data.append(self._bounds_to_data(note.position))
            data.extend(note.unknown_datanodes)
            nodes.append(CGMLNode(
                note_id,
                data=data
            ))
        return nodes

    def _point_label(self, point: Point) -> CGMLDataNode:
        return CGMLDataNode(
            'dLabelGeometry', None, None, CGMLPointNode(point.x, point.y))

    def _point_to_data(self, point: Point) -> CGMLDataNode:
        return CGMLDataNode(
            'dGeometry', None, None, CGMLPointNode(point.x, point.y))

    def _get_state_nodes(self,
                         states: Dict[str, CGMLState]) -> Dict[str, CGMLNode]:
        def _getCGMLNode(nodes: Dict[str, CGMLNode],
                         state: CGMLState, stateId: str) -> CGMLNode:
            if nodes.get(stateId) is not None:
                return nodes[stateId]
            else:
                node = CGMLNode(stateId)
                data: List[CGMLDataNode] = []
                if isinstance(state.bounds, Rectangle):
                    data.append(self._bounds_to_data(state.bounds))
                elif isinstance(state.bounds, Point):
                    data.append(self._point_to_data(state.bounds))
                if state.color is not None:
                    data.append(self._colorToData(state.color))
                data.append(self._actions_to_data(state.actions))
                data.append(self._name_to_data(state.name))
                data.extend(state.unknown_datanodes)
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
        return nodes

    def _name_to_data(self, name: str) -> CGMLDataNode:
        return CGMLDataNode('dName', name)

    def _colorToData(self, color: str) -> CGMLDataNode:
        return CGMLDataNode('dColor', color)

    def _actions_to_data(self, actions: str) -> CGMLDataNode:
        return CGMLDataNode(
            'dData', actions
        )

    def _bounds_to_data(self, bounds: Rectangle) -> CGMLDataNode:
        return CGMLDataNode(
            'dGeometry',
            None,
            CGMLRectNode(
                bounds.x,
                bounds.y,
                bounds.width,
                bounds.height
            )
        )

    def _get_format_node(self, format: str) -> CGMLDataNode:
        return CGMLDataNode('gFormat', format)

    def _get_keys(self, awaialaibleKeys: AvailableKeys) -> List[CGMLKeyNode]:
        keyNodes: List[CGMLKeyNode] = []
        for key in list(awaialaibleKeys.keys()):
            keyNodes.extend(awaialaibleKeys[key])

        return keyNodes
