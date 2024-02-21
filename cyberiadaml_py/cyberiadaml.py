import xmltodict

from .types.cgml_schema import CGML


class CGMLParser:

    def parseCGML(self):
        with open('demos/CyberiadaFormat-Autoborder.graphml', 'r') as f:
            data = f.read()
            a = CGML(**xmltodict.parse(data))
            print(a.graphml.data.key)
