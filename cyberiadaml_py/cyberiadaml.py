from xmltodict import parse

from cyberiadaml_py.types.elements import CGMLElements, AwailableKeys

from collections import defaultdict
from collections.abc import Iterable
from .types.cgml_schema import CGML


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

        return self.elements

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
        # DRY
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
