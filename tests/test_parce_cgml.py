import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from cyberiadaml_py.cyberiadaml_parser import CGMLParser


class TestFunctionsFromXML:
    """Тесты для парсинга функций из XML-файла."""

    def test_parse_functions_from_file(self):
        """Тест: парсинг всех функций из XML-файла."""

        xml_file = Path(__file__).parent / "testfile_for_func.xml"

        assert xml_file.exists(), f"Файл {xml_file} не найден!"

        with open(xml_file, 'r', encoding='utf-8') as f:
            xml_content = f.read()

        parser = CGMLParser()
        elements = parser.parse_cgml(xml_content)

        assert len(elements.functions) == 4, f"Ожидалось 4 функции, получено {len(elements.functions)}"

        func1 = elements.functions.get('simple_function')
        assert func1 is not None, "Функция 'simple_function' не найдена"
        assert func1.id == 'simple_function'
        assert func1.type == 'function'
        assert 'dData' in func1.parameters
        assert 'description/Простая функция' in func1.parameters['dData']
        assert func1.inputs == ['x']
        assert func1.outputs == ['result']
        assert 'result = x * 2' in func1.body
        assert 'print("x =", x)' in func1.body
        assert func1.name == 'simple_function'

        print("simple_function: OK")


        func2 = elements.functions.get('math_function')
        assert func2 is not None, "Функция 'math_function' не найдена"
        assert func2.id == 'math_function'
        assert func2.type == 'function'
        assert len(func2.inputs) == 2
        assert 'a' in func2.inputs
        assert 'b' in func2.inputs
        assert len(func2.outputs) == 2
        assert 'sum' in func2.outputs
        assert 'product' in func2.outputs
        assert 'sum = a + b' in func2.body
        assert 'product = a * b' in func2.body
        assert 'print("Sum:", sum, "Product:", product)' in func2.body

        print("math_function: OK")

        func3 = elements.functions.get('void_function')
        assert func3 is not None, "Функция 'void_function' не найдена"
        assert func3.id == 'void_function'
        assert func3.type == 'function'
        assert len(func3.inputs) == 0
        assert len(func3.outputs) == 0
        assert 'print("Hello World")' in func3.body
        assert 'print("Goodbye World")' in func3.body

        print("void_function: OK")

        func4 = elements.functions.get('nested_function')
        assert func4 is not None, "Функция 'nested_function' не найдена"
        assert func4.id == 'nested_function'
        assert func4.type == 'function'
        assert len(func4.inputs) == 1
        assert func4.inputs[0] == 'value'
        assert len(func4.outputs) == 1
        assert func4.outputs[0] == 'result'

        print("nested_function: OK")

        assert 'component_graph' in elements.state_machines, "Компонент 'component_graph' не найден"

        print("Компоненты: OK")
        print(f"\nВсего функций: {len(elements.functions)}")
        print("Все тесты пройдены!")

    def test_parse_func_from_graph_direct(self):
        """Тест: прямой вызов parse_func_from_graph."""

        xml_file = Path(__file__).parent / "testfile_for_func.xml"

        with open(xml_file, 'r', encoding='utf-8') as f:
            xml_content = f.read()

        parser = CGMLParser()
        elements = parser.parse_cgml(xml_content)

        # Проверяем, что каждая функция имеет правильную структуру
        for func_id, func in elements.functions.items():
            assert func.id == func_id
            assert func.type == 'function'
            assert isinstance(func.parameters, dict)
            assert isinstance(func.inputs, list)
            assert isinstance(func.outputs, list)
            assert isinstance(func.body, str)
            assert isinstance(func.name, str)

        print("Все функции имеют правильную структуру")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])