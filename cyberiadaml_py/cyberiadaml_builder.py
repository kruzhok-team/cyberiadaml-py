from cyberiadaml_py.cyberiadaml_parser import CGMLParserException
from cyberiadaml_py.types.cgml_schema import CGML, CGMLDataNode, CGMLGraph, CGMLGraphml, CGMLKeyNode, CGMLNode
from cyberiadaml_py.types.common import Rectangle
from cyberiadaml_py.types.elements import AwailableKeys, CGMLElements, CGMLNote, CGMLState
from typing import Iterable, List, Dict
from xmltodict import unparse
from pydantic import RootModel


class CGMLBuilder:
    def __init__(self) -> None:
        self.schema: CGML = CGMLBuilder.createEmptySchema()

    @staticmethod
    def createEmptySchema() -> CGML:
        return CGML(graphml=CGMLGraphml(
            [],
            'http://graphml.graphdrawing.org/xmlns',
        ))

    def build(self, elements: CGMLElements) -> str:
        # У model_dump неправильный возвращаемый тип (CGML),
        # поэтому приходится явно показывать линтеру, что это dict
        self.schema.graphml.key = self._getKeys(elements.keys)
        self.schema.graphml.data = self._getFormatNode(elements.format)
        self.schema.graphml.graph = CGMLGraph(
            'directed',
            'G',
            node=[*self._getStateNodes(elements.states),
                  *self._getNoteNodes(elements.notes)
                  ]
        )

        schema: CGML = RootModel[CGML](self.schema).model_dump(
            by_alias=True, exclude_defaults=True)
        if isinstance(schema, dict):
            return unparse(schema, pretty=True)
        else:
            raise CGMLParserException('Internal error: Schema is not dict')

    def _getNoteNodes(self, notes: List[CGMLNote]) -> List[CGMLNode]:
        nodes: List[CGMLNode] = []

        return nodes

    def _getStateNodes(self, states: Dict[str, CGMLState]) -> List[CGMLNode]:
        def _getCGMLNode(nodes: Dict[str, CGMLNode], state: CGMLState, stateId: str) -> CGMLNode:
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
                parent = _getCGMLNode(nodes, parentState, state.parent)
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
        return CGMLDataNode('dFormat', format)

    def _getKeys(self, awaialaibleKeys: AwailableKeys) -> List[CGMLKeyNode]:
        keyNodes: List[CGMLKeyNode] = []
        for key in list(awaialaibleKeys.keys()):
            keyNodes.extend(awaialaibleKeys[key])

        return keyNodes
