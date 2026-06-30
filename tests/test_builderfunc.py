"""Tests for function graph generation in CGMLBuilder."""
import pytest
import xml.etree.ElementTree as ET

from cyberiadaml_py.cyberiadaml_builder import CGMLBuilder
from cyberiadaml_py.types.common import Rectangle
from cyberiadaml_py.types.elements import (
    CGMLElements,
    CGMLFunction,
    CGMLInput,
    CGMLOutput,
    CGMLBlock,
    CGMLTransition,
)


def test_build_function_graph():
    """Test generation of a graph for a function with blocks and edges."""
    func = CGMLFunction(
        id='func_sum',
        type='function',
        parameters={'description': 'sum function'},
        inputs={
            'func_sum_input_a': CGMLInput(
                type='input',
                data='a',
                data_type='int',
                position=Rectangle(x=50, y=100, width=40, height=40)
            ),
            'func_sum_input_b': CGMLInput(
                type='input',
                data='b',
                data_type='int',
                position=Rectangle(x=50, y=200, width=40, height=40)
            )
        },
        outputs={
            'func_sum_output_result': CGMLOutput(
                type='output',
                data='result',
                data_type='int',
                position=Rectangle(x=450, y=150, width=40, height=40)
            )
        },
        body={
            'func_sum_block_Сложение': CGMLBlock(
                type='block',
                data='Сложение',
                block_type='ADD',
                position=Rectangle(x=200, y=150, width=150, height=50)
            )
        },
        edges={
            'e1': CGMLTransition(
                id='e1',
                source='func_sum_input_a',
                target='func_sum_block_Сложение',
                actions='a',
                unknown_datanodes=[]
            ),
            'e2': CGMLTransition(
                id='e2',
                source='func_sum_input_b',
                target='func_sum_block_Сложение',
                actions='b',
                unknown_datanodes=[]
            ),
            'e3': CGMLTransition(
                id='e3',
                source='func_sum_block_Сложение',
                target='func_sum_output_result',
                actions='result',
                unknown_datanodes=[]
            )
        },
        name='Функция сложения'
    )

    elements = CGMLElements(
        state_machines={},
        format='Cyberiada-GraphML-1.0',
        keys={},
        functions={'func_sum': func}
    )

    builder = CGMLBuilder()
    xml_str = builder.build(elements)

    # Сохраняем для отладки (опционально)
    with open('func_sum.xml', 'w', encoding='utf-8') as f:
        f.write(xml_str)

    root = ET.fromstring(xml_str)
    ns = {'g': 'http://graphml.graphdrawing.org/xmlns'}
    graph = root.find(".//g:graph[@id='func_sum']", ns)
    assert graph is not None

    # Проверяем узлы
    nodes = graph.findall('g:node', ns)
    node_ids = [n.get('id') for n in nodes]
    expected_nodes = [
        'func_sum_input_a',
        'func_sum_input_b',
        'func_sum_output_result',
        'func_sum_block_Сложение'
    ]
    for expected in expected_nodes:
        assert expected in node_ids

    # Проверяем data-узлы графа
    data_nodes = graph.findall('g:data', ns)
    data_dict = {d.get('key'): d.text for d in data_nodes}
    assert data_dict.get('dName') == 'CGML_FUNCTION'
    assert data_dict.get('description') == 'sum function'
    assert 'dStateMachine' not in data_dict

    # Проверяем рёбра
    edges = graph.findall('g:edge', ns)
    assert len(edges) == 3
    edge_sources = [e.get('source') for e in edges]
    edge_targets = [e.get('target') for e in edges]
    assert 'func_sum_input_a' in edge_sources
    assert 'func_sum_input_b' in edge_sources
    assert 'func_sum_block_Сложение' in edge_targets
    assert any(e.get('source') == 'func_sum_block_Сложение'
               and e.get('target') == 'func_sum_output_result'
               for e in edges)

    print('test_build_function_graph passed')


def test_build_function_without_blocks():
    """Test function without blocks – direct input‑output connection."""
    func = CGMLFunction(
        id='func_direct',
        type='function',
        parameters={},
        inputs={
            'func_direct_input_x': CGMLInput(
                type='input',
                data='x',
                data_type='int'
            )
        },
        outputs={
            'func_direct_output_y': CGMLOutput(
                type='output',
                data='y',
                data_type='int'
            )
        },
        body={},
        edges={
            'e1': CGMLTransition(
                id='e1',
                source='func_direct_input_x',
                target='func_direct_output_y',
                actions='x_to_y',
                unknown_datanodes=[]
            )
        },
        name='Прямая функция'
    )

    elements = CGMLElements(
        state_machines={},
        format='Cyberiada-GraphML-1.0',
        keys={},
        functions={'func_direct': func}
    )

    builder = CGMLBuilder()
    xml_str = builder.build(elements)

    with open('func_direct.xml', 'w', encoding='utf-8') as f:
        f.write(xml_str)

    root = ET.fromstring(xml_str)
    ns = {'g': 'http://graphml.graphdrawing.org/xmlns'}
    graph = root.find(".//g:graph[@id='func_direct']", ns)
    assert graph is not None

    edges = graph.findall('g:edge', ns)
    assert len(edges) == 1
    assert edges[0].get('source') == 'func_direct_input_x'
    assert edges[0].get('target') == 'func_direct_output_y'
    # Проверяем наличие data с действием
    edge_data = edges[0].find('g:data', ns)
    if edge_data is not None:
        assert edge_data.get('key') == 'dData'
        assert edge_data.text == 'x_to_y'


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
