from cyberiadaml_py.cyberiadaml_builder import CGMLBuilder
from cyberiadaml_py.cyberiadaml_parser import CGMLParser

if __name__ == '__main__':
    with open('demos/CyberiadaFormat-Blinker.graphml', 'r') as f:
        a = CGMLParser().parseCGML(f.read())
        print(CGMLBuilder().build(a))
