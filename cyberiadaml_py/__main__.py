from .cyberiadaml import CGMLParser
from pprint import pprint
if __name__ == '__main__':
    with open('demos/CyberiadaFormat-Blinker.graphml', 'r') as f:
        pprint(CGMLParser().parseCGML(f.read()))
