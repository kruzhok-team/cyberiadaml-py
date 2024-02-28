from collections import defaultdict

import pytest
from cyberiadaml_py.cyberiadaml_builder import CGMLBuilder

from cyberiadaml_py.types.cgml_scheme import CGMLKeyNode
from cyberiadaml_py.cyberiadaml_parser import CGMLParser
from cyberiadaml_py.types.elements import (
    CGMLTransition,
    CGMLDataNode,
    CGMLElements
)


@pytest.mark.parametrize(
    'transition, expected',
    [
        pytest.param(
            CGMLTransition(
                source='source',
                target='target',
                actions='',
                unknownDatanodes=[]
            ),
            CGMLTransition(
                source='source',
                target='target',
                actions='',
                unknownDatanodes=[]
            ),
            id='Empty transition'
        ),
        pytest.param(
            CGMLTransition(
                source='source',
                target='target',
                actions='',
                unknownDatanodes=[
                    CGMLDataNode(
                        'dData',
                        'actions'
                    )
                ]
            ),
            CGMLTransition(
                source='source',
                target='target',
                actions='actions',
                unknownDatanodes=[]
            ),
            id='With dData node'
        ),
        pytest.param(
            CGMLTransition(
                source='source',
                target='target',
                actions='',
                unknownDatanodes=[
                    CGMLDataNode(
                        'dColor',
                        '#FFFFFF'
                    )
                ]
            ),
            CGMLTransition(
                source='source',
                target='target',
                actions='',
                color='#FFFFFF',
                unknownDatanodes=[]
            ),
            id='With dColor node'
        ),
        pytest.param(
            CGMLTransition(
                source='source',
                target='target',
                actions='',
                unknownDatanodes=[
                    CGMLDataNode(
                        'dExtension',
                        'my information'
                    )
                ]
            ),
            CGMLTransition(
                source='source',
                target='target',
                actions='',
                unknownDatanodes=[
                    CGMLDataNode(
                        'dExtension',
                        'my information'
                    )
                ]
            ),
            id='With dExtension node'
        ),
        pytest.param(
            CGMLTransition(
                source='source',
                target='target',
                actions='',
                unknownDatanodes=[
                    CGMLDataNode(
                        'dUnknown',
                        'my information'
                    )
                ]
            ),
            CGMLTransition(
                source='source',
                target='target',
                actions='',
                unknownDatanodes=[
                    CGMLDataNode(
                        'dUnknown',
                        'my information'
                    )
                ]
            ),
            marks=pytest.mark.xfail(reason='keys dont have dUnknown key'),
            id='With unknown node'
        ),

    ]
)
def test_processEdgeData(
        transition: CGMLTransition, expected: CGMLTransition) -> None:
    parser = CGMLParser()
    parser.elements.keys = defaultdict(lambda: [])
    parser.elements.keys['edge'].extend([
        CGMLKeyNode(
            'dColor', 'edge'
        ),
        CGMLKeyNode(
            'dData', 'edge'
        ),
        CGMLKeyNode(
            'dExtension', 'edge',
        ),
        CGMLKeyNode(
            'dGeometry', 'edge',
        )
    ]
    )

    assert parser._processEdgeData(transition) == expected


@pytest.mark.parametrize(
    'path', [
        pytest.param(
            'demos/CyberiadaFormat-Autoborder.graphml',
            id='Bearloga'
        ),
        pytest.param(
            'demos/CyberiadaFormat-Blinker.graphml',
            id='ArduinoUno'
        )
    ]
)
def test_parse_build_cycle(path: str) -> None:
    parser = CGMLParser()
    builder = CGMLBuilder()

    with open(path) as demo:
        data: str = demo.read()
        elements: CGMLElements = parser.parseCGML(data)
        builded: str = builder.build(elements)
        new_elements: CGMLElements = parser.parseCGML(builded)
        assert new_elements == elements
