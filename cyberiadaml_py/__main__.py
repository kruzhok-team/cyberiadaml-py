from cyberiadaml_py.cyberiadaml_builder import CGMLBuilder
from .cyberiadaml_parser import CGMLParser
from pprint import pprint
if __name__ == '__main__':
    with open('demos/CyberiadaFormat-Autoborder.graphml', 'r') as f:
        pprint(CGMLParser().parseCGML(f.read()))
        # CGMLBuilder()
