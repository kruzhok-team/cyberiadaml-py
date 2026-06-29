"""Tests for parsing functions from XML using CGMLParser."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from cyberiadaml_py.cyberiadaml_parser import CGMLParser
from cyberiadaml_py.types.common import Point, Rectangle
from cyberiadaml_py.types.elements import CGMLInput, CGMLOutput, CGMLBlock


def test_parse_functions_from_file():
    """Parse all functions from the test XML file and verify their content."""
    xml_file = Path(__file__).parent / 'testfile_for_func.xml'
    assert xml_file.exists(), f'File {xml_file} not found'

    with open(xml_file, 'r', encoding='utf-8') as f:
        xml_content = f.read()

    parser = CGMLParser()
    elements = parser.parse_cgml(xml_content)

    assert len(elements.functions) == 1, 'Should have exactly one function'
    func = elements.functions.get('func_sum')
    assert func is not None, 'Function func_sum not found'

    assert func.id == 'func_sum'
    assert func.type == 'function'
    assert func.name, 'Function name should not be empty'

    # Проверяем входы
    assert len(func.inputs) == 2, 'Should have 2 inputs'
    input_a = next((inp for inp in func.inputs if inp.data == 'a'), None)
    input_b = next((inp for inp in func.inputs if inp.data == 'b'), None)
    assert input_a is not None, 'Input a not found'
    assert input_b is not None, 'Input b not found'

    assert input_a.data_type == 'int'
    assert isinstance(input_a.position, Rectangle)
    assert input_a.position.x == 50
    assert input_a.position.y == 100
    assert input_a.position.width == 40
    assert input_a.position.height == 40

    assert input_b.data_type == 'int'
    assert isinstance(input_b.position, Rectangle)
    assert input_b.position.x == 50
    assert input_b.position.y == 200
    assert input_b.position.width == 40
    assert input_b.position.height == 40

    # Проверяем выходы
    assert len(func.outputs) == 1, 'Should have 1 output'
    output = func.outputs[0]
    assert output.data == 'result'
    assert output.data_type == 'int'
    assert isinstance(output.position, Rectangle)
    assert output.position.x == 450
    assert output.position.y == 150
    assert output.position.width == 40
    assert output.position.height == 40

    # Проверяем блоки
    assert len(func.body) == 1, 'Should have 1 block'
    block = func.body[0]
    assert block.data == 'Сложение'
    assert block.block_type == 'ADD'
    assert isinstance(block.position, Rectangle)
    assert block.position.x == 200
    assert block.position.y == 150
    assert block.position.width == 150
    assert block.position.height == 50

    print('test_parse_functions_from_file passed')


def test_parse_func_from_graph_direct():
    """Directly verify the structure of parsed functions."""
    xml_file = Path(__file__).parent / 'testfile_for_func.xml'
    if not xml_file.exists():
        pytest.skip(f'File {xml_file} not found, use testfile_for_func.xml')

    with open(xml_file, 'r', encoding='utf-8') as f:
        xml_content = f.read()

    parser = CGMLParser()
    elements = parser.parse_cgml(xml_content)

    func = elements.functions.get('func_sum')
    assert func is not None, 'Function func_sum not found'

    for inp in func.inputs:
        assert isinstance(inp, CGMLInput)
        assert inp.type == 'input'
    for out in func.outputs:
        assert isinstance(out, CGMLOutput)
        assert out.type == 'output'
    for block in func.body:
        assert isinstance(block, CGMLBlock)
        assert block.type == 'block'

    print('test_parse_func_from_graph_direct passed')


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])