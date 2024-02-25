from cyberiadaml_py.cyberiadaml_parser import CGMLParserException
from cyberiadaml_py.types.cgml_schema import CGML, CGMLGraphml, CGMLKeyNode
from cyberiadaml_py.types.elements import AwailableKeys, CGMLElements
from typing import List
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
        schema: CGML = RootModel[CGML](self.schema).model_dump(
            by_alias=True, exclude_defaults=True)
        if isinstance(schema, dict):
            return unparse(schema, pretty=True)
        else:
            raise CGMLParserException('Internal error: Schema is not dict')

    def _getKeys(self, awaialaibleKeys: AwailableKeys) -> List[CGMLKeyNode]:
        keyNodes: List[CGMLKeyNode] = []
        for key in list(awaialaibleKeys.keys()):
            keyNodes.extend(awaialaibleKeys[key])

        return keyNodes
