import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from cyberiadaml_py.cyberiadaml_builder import _split_graph
from cyberiadaml_py.types.cgml_scheme import CGMLGraph, CGMLDataNode


def test_split_graph_components_and_functions():
    """Тест: разделение графов на компоненты и функции."""
    # Создаём граф-компонент
    comp_graph = CGMLGraph(
        "graph_components",
        [
            CGMLDataNode("dStateMachine", "StateMachine"),
            CGMLDataNode("dName", "CGML_COMPONENT")
        ],
        "directed"
    )

    # Создаём граф-функцию
    func_graph = CGMLGraph(
        "graph_functions",
        [
            CGMLDataNode("dStateMachine", "StateMachine"),
            CGMLDataNode("dName", "CGML_FUNCTION")
        ],
        "directed"
    )

    # Вызываем функцию
    result = _split_graph([comp_graph, func_graph])

    # Проверяем результаты
    assert len(result['components']) == 1
    assert len(result['functions']) == 1
    assert result['components'][0].id == "graph_components"
    assert result['functions'][0].id == "graph_functions"

    print("Тест пройден: компоненты и функции разделены правильно")


def test_split_graph_without_dname():
    """Тест: граф без dName считается функцией."""
    graph = CGMLGraph(
        "no_dname_graph",
        [
            CGMLDataNode("dStateMachine", "StateMachine")
        ],
        "directed"
    )

    result = _split_graph([graph])

    assert len(result['components']) == 0
    assert len(result['functions']) == 1
    assert result['functions'][0].id == "no_dname_graph"

    print("Тест пройден: граф без dName попал в функции")


def test_split_graph_component_only():
    """Тест: только компоненты."""
    comp_graph = CGMLGraph(
        "comp1",
        [
            CGMLDataNode("dStateMachine", "StateMachine"),
            CGMLDataNode("dName", "CGML_COMPONENT")
        ],
        "directed"
    )

    result = _split_graph([comp_graph])

    assert len(result['components']) == 1
    assert len(result['functions']) == 0
    assert result['components'][0].id == "comp1"

    print("Тест пройден: только компоненты")


def test_split_graph_functions_only():
    """Тест: только функции."""
    func_graph = CGMLGraph(
        "func1",
        [
            CGMLDataNode("dStateMachine", "StateMachine"),
            CGMLDataNode("dName", "CGML_FUNCTION")
        ],
        "directed"
    )

    result = _split_graph([func_graph])

    assert len(result['components']) == 0
    assert len(result['functions']) == 1
    assert result['functions'][0].id == "func1"

    print("Тест пройден: только функции")


def test_split_graph_empty_list():
    """Тест: пустой список графов."""
    result = _split_graph([])

    assert result['components'] == []
    assert result['functions'] == []

    print("Тест пройден: пустой список")


def test_split_graph_mixed():
    """Тест: смесь разных графов."""
    graphs = [
        CGMLGraph("comp1", [CGMLDataNode("dStateMachine", "SM"), CGMLDataNode("dName", "CGML_COMPONENT")], "directed"),
        CGMLGraph("func1", [CGMLDataNode("dStateMachine", "SM"), CGMLDataNode("dName", "CGML_FUNCTION")], "directed"),
        CGMLGraph("unknown1", [CGMLDataNode("dStateMachine", "SM"), CGMLDataNode("dName", "SOMETHING_ELSE")],
                  "directed"),
        CGMLGraph("no_name1", [CGMLDataNode("dStateMachine", "SM")], "directed"),
    ]

    result = _split_graph(graphs)

    assert len(result['components']) == 1
    assert len(result['functions']) == 3
    assert result['components'][0].id == "comp1"
    assert [g.id for g in result['functions']] == ["func1", "unknown1", "no_name1"]

    print("Тест пройден: смесь графов")


def test_split_graph_data_as_single_object():
    """Тест: data может быть одиночным объектом, а не списком."""
    # Создаём граф с data как одиночный объект
    graph = CGMLGraph(
        "single_data_graph",
        CGMLDataNode("dName", "CGML_COMPONENT"),  # Не список, а одиночный объект
        "directed"
    )

    result = _split_graph([graph])

    assert len(result['components']) == 1
    assert result['components'][0].id == "single_data_graph"

    print("Тест пройден: data как одиночный объект")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])