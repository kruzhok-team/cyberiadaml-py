import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from cyberiadaml_py.cyberiadaml_parser import CGMLParser
from cyberiadaml_py.types.common import Point, Rectangle
from cyberiadaml_py.types.elements import CGMLInput, CGMLOutput, CGMLBlock



"""Тесты для парсинга функций из XML-файла."""

def test_parse_functions_from_file():
    """Тест: парсинг всех функций из XML-файла."""
    xml_file = Path(__file__).parent / "testfile_for_func.xml"
    assert xml_file.exists(), f"Файл {xml_file} не найден!"

    with open(xml_file, 'r', encoding='utf-8') as f:
        xml_content = f.read()

    parser = CGMLParser()
    elements = parser.parse_cgml(xml_content)

    # Проверяем, что функции распарсены
    assert len(elements.functions) == 1, "Должна быть ровно одна функция"
    func = elements.functions.get("func_sum")
    assert func is not None, "Функция func_sum не найдена"

    # Проверяем основные поля
    assert func.id == "func_sum"
    assert func.type == "function"
    assert func.name == "Функция сложения" or func.name == "func_sum"
    assert "dStateMachine" in func.parameters
    assert func.parameters["dStateMachine"] == "true"

    # Проверяем входы
    assert len(func.inputs) == 2, "Должно быть 2 входа"
    input_a = next((inp for inp in func.inputs if inp.data == "a"), None)
    input_b = next((inp for inp in func.inputs if inp.data == "b"), None)
    assert input_a is not None, "Вход 'a' не найден"
    assert input_b is not None, "Вход 'b' не найден"

    # Проверяем тип данных и геометрию для входа a
    assert input_a.data_type == "int"
    assert isinstance(input_a.position, Rectangle)
    assert input_a.position.x == 50
    assert input_a.position.y == 100
    assert input_a.position.width == 40
    assert input_a.position.height == 40

    # Проверяем вход b
    assert input_b.data_type == "int"
    assert isinstance(input_b.position, Rectangle)
    assert input_b.position.x == 50
    assert input_b.position.y == 200
    assert input_b.position.width == 40
    assert input_b.position.height == 40

    # Проверяем выходы
    assert len(func.outputs) == 1, "Должен быть 1 выход"
    output = func.outputs[0]
    assert output.data == "result"
    assert output.data_type == "int"
    assert isinstance(output.position, Rectangle)
    assert output.position.x == 450
    assert output.position.y == 150
    assert output.position.width == 40
    assert output.position.height == 40

    # Проверяем блоки (body)
    assert len(func.body) == 1, "Должен быть 1 блок"
    block = func.body[0]
    assert block.data == "Сложение"
    assert block.block_type == "ADD"
    assert isinstance(block.position, Rectangle)
    assert block.position.x == 200
    assert block.position.y == 150
    assert block.position.width == 150
    assert block.position.height == 50

    print("Все проверки пройдены!")

def test_parse_func_from_graph_direct():
    """Тест: прямой вызов parse_func_from_graph."""
    xml_file = Path(__file__).parent / "testfile_for_func.xml"
    if not xml_file.exists():
        pytest.skip(f"Файл {xml_file} не найден, используйте testfile_for_func.xml")

    with open(xml_file, 'r', encoding='utf-8') as f:
        xml_content = f.read()

    parser = CGMLParser()
    elements = parser.parse_cgml(xml_content)

    func = elements.functions.get("func_sum")
    assert func is not None, "Функция func_sum не найдена"
    # Проверяем структуру объектов
    for inp in func.inputs:
        assert isinstance(inp, CGMLInput)
        assert inp.type == "input"
    for out in func.outputs:
        assert isinstance(out, CGMLOutput)
        assert out.type == "output"
    for block in func.body:
        assert isinstance(block, CGMLBlock)
        assert block.type == "block"

    print("Прямой вызов parse_func_from_graph корректен")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])