from cyberiadaml_py.cyberiadaml_parser import CGMLParserException
from cyberiadaml_py.types.cgml_schema import CGML, CGMLGraphml
from cyberiadaml_py.types.elements import CGMLElements
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
        schema: CGML = RootModel[CGML](self.schema).model_dump(
            by_alias=True, exclude_defaults=True)
        if isinstance(schema, dict):
            print(unparse(schema, pretty=True))
        else:
            raise CGMLParserException('Schema is not dict')
        return ''
