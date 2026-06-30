"""Tests for parsing functions from XML using CGMLParser."""
from pathlib import Path
import pytest
from cyberiadaml_py.cyberiadaml_parser import CGMLParser
from cyberiadaml_py.types.common import Rectangle
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

    # Проверяем входы (словарь)
    assert len(func.inputs) == 2, 'Should have 2 inputs'
    # Проверяем, что все входы имеют правильные атрибуты
    for input_id, inp in func.inputs.items():
        assert inp.data in ('a', 'b')
        assert inp.data_type == 'int'
        assert isinstance(inp.position, Rectangle)

    # Проверяем выходы
    assert len(func.outputs) == 1, 'Should have 1 output'
    output = next(iter(func.outputs.values()))
    assert output.data == 'result'
    assert output.data_type == 'int'
    assert isinstance(output.position, Rectangle)
    assert output.position.x == 450
    assert output.position.y == 150
    assert output.position.width == 40
    assert output.position.height == 40

    # Проверяем блоки
    assert len(func.body) == 1, 'Should have 1 block'
    block = next(iter(func.body.values()))
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

    for inp in func.inputs.values():
        assert isinstance(inp, CGMLInput)
        assert inp.type == 'input'
    for out in func.outputs.values():
        assert isinstance(out, CGMLOutput)
        assert out.type == 'output'
    for block in func.body.values():
        assert isinstance(block, CGMLBlock)
        assert block.type == 'block'


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
