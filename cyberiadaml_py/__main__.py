from .cyberiadaml import CGMLParser

if __name__ == '__main__':
    with open('demos/CyberiadaFormat-Blinker.graphml', 'r') as f:
        print(CGMLParser().parseCGML(f.read()).initial_state)
