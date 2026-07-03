"""Tests for the _split_graph method in CGMLParser."""
import pytest
from cyberiadaml_py.cyberiadaml_parser import CGMLParser
from cyberiadaml_py.types.cgml_scheme import CGMLGraph, CGMLDataNode


def test_split_graph_components_and_functions():
    """Split a list with both state machine and function graphs."""
    parser = CGMLParser()

    sm_graph = CGMLGraph(
        'state_machine_1',
        [
            CGMLDataNode('dStateMachine', 'StateMachine'),
            CGMLDataNode('dName', 'CGML_COMPONENT')
        ],
        'directed'
    )

    func_graph = CGMLGraph(
        'function_1',
        [
            CGMLDataNode('dFunction')
        ],
        'directed'
    )

    result = parser._split_graph([sm_graph, func_graph])

    assert len(result['state_machines']) == 1
    assert len(result['functions']) == 1
    assert result['state_machines'][0].id == 'state_machine_1'
    assert result['functions'][0].id == 'function_1'

    print('test_split_graph_components_and_functions passed')


def test_split_graph_without_dname():
    """Graph without dName but with dStateMachine should be a state machine."""
    parser = CGMLParser()

    graph = CGMLGraph(
        'no_dname_graph',
        [CGMLDataNode('dStateMachine', 'StateMachine')],
        'directed'
    )

    result = parser._split_graph([graph])

    assert len(result['state_machines']) == 1
    assert len(result['functions']) == 0
    assert result['state_machines'][0].id == 'no_dname_graph'

    print('test_split_graph_without_dname passed')


def test_split_graph_component_only():
    """Only state machine graphs."""
    parser = CGMLParser()

    sm_graph = CGMLGraph(
        'sm1',
        [
            CGMLDataNode('dStateMachine', 'StateMachine'),
            CGMLDataNode('dName', 'CGML_COMPONENT')
        ],
        'directed'
    )

    result = parser._split_graph([sm_graph])

    assert len(result['state_machines']) == 1
    assert len(result['functions']) == 0
    assert result['state_machines'][0].id == 'sm1'

    print('test_split_graph_component_only passed')


def test_split_graph_functions_only():
    """Only function graphs (without dStateMachine)."""
    parser = CGMLParser()

    func_graph = CGMLGraph(
        'func1',
        [
            CGMLDataNode('dFunction')
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
    """Mixed graphs: some with dStateMachine, some with dFunction."""
    parser = CGMLParser()

    graphs = [
        CGMLGraph(
            'sm1',
            [
                CGMLDataNode('dStateMachine', 'SM'),
                CGMLDataNode('dName', 'CGML_COMPONENT')
            ],
            'directed'
        ),
        CGMLGraph(
            'func1',
            [
                CGMLDataNode('dFunction')
            ],
            'directed'
        ),
        CGMLGraph(
            'func2',
            [
                CGMLDataNode('dFunction'),
                CGMLDataNode('dName', 'SOMETHING_ELSE')
            ],
            'directed'
        ),
    ]

    result = parser._split_graph(graphs)

    assert len(result['state_machines']) == 1
    assert len(result['functions']) == 2
    assert result['state_machines'][0].id == 'sm1'
    assert [g.id for g in result['functions']] == ['func1', 'func2']

    print('test_split_graph_mixed passed')


def test_split_graph_data_as_single_object():
    """Data can be a single object, with dFunction."""
    parser = CGMLParser()

    graph = CGMLGraph(
        'single_data_graph',
        CGMLDataNode('dFunction'),
        'directed'
    )

    result = parser._split_graph([graph])

    assert len(result['state_machines']) == 0
    assert len(result['functions']) == 1
    assert result['functions'][0].id == 'single_data_graph'


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
