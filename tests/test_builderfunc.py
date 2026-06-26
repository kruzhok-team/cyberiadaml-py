import sys
from pathlib import Path
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from cyberiadaml_py.cyberiadaml_builder import CGMLBuilder
from cyberiadaml_py.types.common import Point, Rectangle
from cyberiadaml_py.types.elements import (
    CGMLElements,
    CGMLFunction,
    CGMLInput,
    CGMLOutput,
    CGMLBlock,
)


def test_build_function_graph():
    """Тест: генерация графа для функции."""
    func = CGMLFunction(
        id="func_sum",
        type="function",
        parameters={"description": "sum function"},
        inputs=[
            CGMLInput(
                type="input",
                data="a",
                data_type="int",
                position=Rectangle(x=50, y=100, width=40, height=40)
            ),
            CGMLInput(
                type="input",
                data="b",
                data_type="int",
                position=Rectangle(x=50, y=200, width=40, height=40)
            )
        ],
        outputs=[
            CGMLOutput(
                type="output",
                data="result",
                data_type="int",
                position=Rectangle(x=450, y=150, width=40, height=40)
            )
        ],
        body=[
            CGMLBlock(
                type="block",
                data="Сложение",
                block_type="ADD",
                position=Rectangle(x=200, y=150, width=150, height=50)
            )
        ],
        name="Функция сложения"
    )

    elements = CGMLElements(
        state_machines={},
        format="Cyberiada-GraphML-1.0",
        keys={},
        functions={"func_sum": func}
    )

    builder = CGMLBuilder()
    xml_str = builder.build(elements)

    # Сохраняем XML в файл
    output_file = Path(__file__).parent / "func_sum.xml"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(xml_str)
    print(f"XML сохранён в: {output_file}")

    # Проверяем сгенерированный XML
    root = ET.fromstring(xml_str)
    ns = {'g': 'http://graphml.graphdrawing.org/xmlns'}
    graph = root.find(".//g:graph[@id='func_sum']", ns)
    assert graph is not None

    # Проверяем узлы
    nodes = graph.findall('g:node', ns)
    node_ids = [n.get('id') for n in nodes]
    assert 'func_sum_input_a' in node_ids
    assert 'func_sum_input_b' in node_ids
    assert 'func_sum_output_result' in node_ids
    assert 'func_sum_block_Сложение' in node_ids

    # Проверяем data-узлы графа
    data_nodes = graph.findall('g:data', ns)
    data_dict = {d.get('key'): d.text for d in data_nodes}
    assert data_dict.get('dName') == 'CGML_FUNCTION'
    assert data_dict.get('description') == 'sum function'
    assert 'dStateMachine' not in data_dict

    # Проверяем рёбра
    edges = graph.findall('g:edge', ns)
    assert len(edges) == 3

    print("Тест генерации функции пройден!")


def test_build_function_without_blocks():
    """Тест: функция без блоков (прямое соединение входов с выходами)."""
    func = CGMLFunction(
        id="func_direct",
        type="function",
        parameters={},
        inputs=[
            CGMLInput(type="input", data="x", data_type="int")
        ],
        outputs=[
            CGMLOutput(type="output", data="y", data_type="int")
        ],
        body=[],
        name="Прямая функция"
    )

    elements = CGMLElements(
        state_machines={},
        format="Cyberiada-GraphML-1.0",
        keys={},
        functions={"func_direct": func}
    )

    builder = CGMLBuilder()
    xml_str = builder.build(elements)

    # Сохраняем XML в файл
    output_file = Path(__file__).parent / "func_direct.xml"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(xml_str)
    print(f"XML сохранён в: {output_file}")

    root = ET.fromstring(xml_str)
    ns = {'g': 'http://graphml.graphdrawing.org/xmlns'}
    graph = root.find(".//g:graph[@id='func_direct']", ns)
    assert graph is not None

    edges = graph.findall('g:edge', ns)
    assert len(edges) == 1
    assert edges[0].get('source') == 'func_direct_input_x'
    assert edges[0].get('target') == 'func_direct_output_y'

    print("Тест функции без блоков пройден!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])