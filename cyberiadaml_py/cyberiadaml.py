# TODO: organize import
from xmltodict import parse
from cyberiadaml_py.types.common import Rectangle

from cyberiadaml_py.types.elements import CGMLElements, AwailableKeys, CGMLState, CGMLTransition

from collections import defaultdict
from collections.abc import Iterable
from .types.cgml_schema import CGML, CGMLEdge, CGMLGraph, CGMLNode
from typing import Any, List, Dict, Optional


class CGMLParserException(Exception):
    ...


class CGMLParser:
    def __init__(self) -> None:
        self.elements: CGMLElements = CGMLParser.createEmptyElements()

    @staticmethod
    def createEmptyElements() -> CGMLElements:
        return CGMLElements(
            states={},
            transitions=[],
            components=[],
            platform='',
            format='',
            meta='',
            keys=defaultdict(),
        )

    def parseCGML(self, graphml: str) -> CGMLElements:
        cgml = CGML(**parse(graphml))
        self.elements.format = self._getFormat(cgml)
        if self.elements.format != 'Cyberiada-GraphML':
            raise CGMLParserException(
                ('Format must be '
                 f'Cyberiada-GraphML, but got {self.elements.format}'))
        self.elements.keys = self._getAwaialbleKeys(cgml)
        graphs: List[CGMLGraph] = self._toList(cgml.graphml.graph)
        states: Dict[str, CGMLState] = {}
        transitions: List[CGMLTransition] = []
        for graph in graphs:
            states = states | self._parseGraphNodes(graph)
            transitions = [*transitions, *self._parseGraphEdges(graph)]
        self.elements.transitions = transitions
        self.elements.states = states
        return self.elements

    def _toList(self, nodes: List | None | Any) -> List:
        if nodes is None:
            return []
        if isinstance(nodes, list):
            return nodes
        else:
            return [nodes]

    def _parseGraphEdges(self, root: CGMLGraph) -> List[CGMLTransition]:
        def _parseEdge(edge: CGMLEdge, cgmlTransitions: List[CGMLTransition]) -> None:
            cgmlTransitions.append(CGMLTransition(source=edge.source,
                                                  target=edge.target,
                                                  actions='',
                                                  unknownDatanodes=self._toList(
                                                      edge.data),
                                                  )
                                   )

        cgmlTransitions: List[CGMLTransition] = []
        if root.edge is not None:
            if isinstance(root.edge, Iterable):
                for edge in root.edge:
                    _parseEdge(edge, cgmlTransitions)
            else:
                _parseEdge(root.edge, cgmlTransitions)
        return cgmlTransitions

    def _parseGraphNodes(self, root: CGMLGraph, parent: Optional[str] = None) -> Dict[str, CGMLState]:
        def parseNode(node: CGMLNode, cgmlStates: Dict[str, CGMLState]) -> None:
            cgmlStates[node.id] = CGMLState(
                name='',
                actions='',
                unknownDatanodes=self._toList(node.data),
                bounds=Rectangle(0, 0, -1, -1),
            )
            if parent is not None:
                cgmlStates[node.id].parent = parent
            graphs: List[CGMLGraph] = self._toList(node.graph)
            for graph in graphs:
                cgmlStates = cgmlStates | self._parseGraphNodes(
                    graph, node.id)

        cgmlStates: Dict[str, CGMLState] = {}
        if root.node is not None:
            if isinstance(root.node, Iterable):
                for node in root.node:
                    parseNode(node, cgmlStates)
            else:
                parseNode(root.node, cgmlStates)
        return cgmlStates

    def _checkDataNodeKey(self, node_name: str, key: str, awaialableKeys: AwailableKeys) -> bool:
        return key in awaialableKeys[node_name]

    # key nodes to comfortable dict
    def _getAwaialbleKeys(self, cgml: CGML) -> AwailableKeys:
        keyNodeDict: AwailableKeys = defaultdict(lambda: [])
        if cgml.graphml.key is not None:
            if isinstance(cgml.graphml.key, Iterable):
                for keyNode in cgml.graphml.key:
                    keyNodeDict[keyNode.for_].append(keyNode.id)
            else:
                keyNodeDict[cgml.graphml.key.for_].append(cgml.graphml.key.id)
        return keyNodeDict

    def _getFormat(self, cgml: CGML) -> str:
        # TODO: DRY
        if isinstance(cgml.graphml.data, Iterable):
            for dataNode in cgml.graphml.data:
                print(dataNode)
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
