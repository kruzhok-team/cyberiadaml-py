from typing import Any
import xmltodict


class CGMLParser:

    def parseCGML(self):
        def _postprocessor(path: str, key: str, value: Any):
            key = key.replace('.', '_')
            if key.startswith('@') or key.startswith('#'):
                return f'_{key[1:]}', value
            return key, value

        with open('demos/CyberiadaFormat-Autoborder.graphml', 'r') as f:
            data = f.read()
            print(xmltodict.parse(data, postprocessor=_postprocessor))
