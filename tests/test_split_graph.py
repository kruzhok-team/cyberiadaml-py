"""Tests for the _split_graph method in CGMLParser."""
import pytest
from cyberiadaml_py.cyberiadaml_parser import CGMLParser
from cyberiadaml_py.types.cgml_scheme import CGMLGraph, CGMLDataNode


def test_split_graph_components_and_functions():
    """Split a list with both component and function graphs."""
    parser = CGMLParser()

    comp_graph = CGMLGraph(
        'graph_components',
        [
            CGMLDataNode('dStateMachine', 'StateMachine'),
            CGMLDataNode('dName', 'CGML_COMPONENT')
        ],
        'directed'
    )

    func_graph = CGMLGraph(
        'graph_functions',
        [
            CGMLDataNode('dStateMachine', 'StateMachine'),
            CGMLDataNode('dName', 'CGML_FUNCTION')
        ],
        'directed'
    )

    result = parser._split_graph([comp_graph, func_graph])

    assert len(result['state_machines']) == 1
    assert len(result['functions']) == 1
    assert result['state_machines'][0].id == 'graph_components'
    assert result['functions'][0].id == 'graph_functions'

    print('test_split_graph_components_and_functions passed')


def test_split_graph_without_dname():
    """Graph without dName should be treated as a function."""
    parser = CGMLParser()

    graph = CGMLGraph(
        'no_dname_graph',
        [CGMLDataNode('dStateMachine', 'StateMachine')],
        'directed'
    )

    result = parser._split_graph([graph])

    assert len(result['state_machines']) == 0
    assert len(result['functions']) == 1
    assert result['functions'][0].id == 'no_dname_graph'

    print('test_split_graph_without_dname passed')


def test_split_graph_component_only():
    """Only component graphs."""
    parser = CGMLParser()

    comp_graph = CGMLGraph(
        'comp1',
        [
            CGMLDataNode('dStateMachine', 'StateMachine'),
            CGMLDataNode('dName', 'CGML_COMPONENT')
        ],
        'directed'
    )

    result = parser._split_graph([comp_graph])

    assert len(result['state_machines']) == 1
    assert len(result['functions']) == 0
    assert result['state_machines'][0].id == 'comp1'

    print('test_split_graph_component_only passed')


def test_split_graph_functions_only():
    """Only function graphs."""
    parser = CGMLParser()

    func_graph = CGMLGraph(
        'func1',
        [
            CGMLDataNode('dStateMachine', 'StateMachine'),
            CGMLDataNode('dName', 'CGML_FUNCTION')
        ],
        'directed'
    )

    result = parser._split_graph([func_graph])

    assert len(result['state_machines']) == 0
    assert len(result['functions']) == 1
    assert result['functions'][0].id == 'func1'

    print('test_split_graph_functions_only passed')


def test_split_graph_empty_list():
    """Empty graph list."""
    parser = CGMLParser()
    result = parser._split_graph([])

    assert result['state_machines'] == []
    assert result['functions'] == []

    print('test_split_graph_empty_list passed')


def test_split_graph_mixed():
    """Mixed graphs including unknown and no‑dName."""
    parser = CGMLParser()

    graphs = [
        CGMLGraph(
            'comp1',
            [
                CGMLDataNode('dStateMachine', 'SM'),
                CGMLDataNode('dName', 'CGML_COMPONENT')
            ],
            'directed'
        ),
        CGMLGraph(
            'func1',
            [
                CGMLDataNode('dStateMachine', 'SM'),
                CGMLDataNode('dName', 'CGML_FUNCTION')
            ],
            'directed'
        ),
        CGMLGraph(
            'unknown1',
            [
                CGMLDataNode('dStateMachine', 'SM'),
                CGMLDataNode('dName', 'SOMETHING_ELSE')
            ],
            'directed'
        ),
        CGMLGraph(
            'no_name1',
            [CGMLDataNode('dStateMachine', 'SM')],
            'directed'
        ),
    ]

    result = parser._split_graph(graphs)

    assert len(result['state_machines']) == 1
    assert len(result['functions']) == 3
    assert result['state_machines'][0].id == 'comp1'
    assert [g.id for g in result['functions']] == [
        'func1', 'unknown1', 'no_name1'
    ]

    print('test_split_graph_mixed passed')


def test_split_graph_data_as_single_object():
    """Data can be a single object, not a list."""
    parser = CGMLParser()

    graph = CGMLGraph(
        'single_data_graph',
        CGMLDataNode('dName', 'CGML_COMPONENT'),
        'directed'
    )

    result = parser._split_graph([graph])

    assert len(result['state_machines']) == 1
    assert result['state_machines'][0].id == 'single_data_graph'

    print('test_split_graph_data_as_single_object passed')


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
