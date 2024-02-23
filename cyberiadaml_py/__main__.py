from .cyberiadaml import CGMLParser

if __name__ == '__main__':
    with open('demos/CyberiadaFormat-Autoborder.graphml', 'r') as f:
        print(CGMLParser().parseCGML(f.read()).transitions)
