from cyberiadaml_py.types.cgml_schema import CGML, CGMLGraphml
from cyberiadaml_py.types.elements import CGMLElements


class CGMLBuilder:
    def __init__(self) -> None:
        self.schema: CGML = CGMLBuilder.createEmptySchema()

    @staticmethod
    def createEmptySchema() -> CGML:
        return CGML(graphml=CGMLGraphml(
            data=[],
            xmlns='http://graphml.graphdrawing.org/xmlns',
        ))

    def build(self, elements: CGMLElements) -> str:
        return ''
