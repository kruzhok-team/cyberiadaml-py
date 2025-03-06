"""The module implements parsing CyberiadaML schemes."""
from collections import defaultdict
from collections.abc import Iterable
from typing import (
    DefaultDict,
    Dict,
    List,
    Optional,
    get_args,
    TypeGuard,
    TypeVar
)

from xmltodict import parse
from cyberiadaml_py.utils import to_list
from cyberiadaml_py.types.cgml_scheme import (
    CGMLDataNode,
    CGMLKeyNode,
    CGMLPointNode,
    CGML,
    CGMLEdge,
    CGMLGraph,
    CGMLNode
)
from cyberiadaml_py.types.elements import (
    CGMLBaseVertex,
    CGMLChoice,
    CGMLFinal,
    CGMLMeta,
    CGMLNoteType,
    CGMLShallowHistory,
    CGMLStateMachine,
    CGMLTerminate,
    CGMLVertexType,
    CGMLComponent,
    CGMLElements,
    AvailableKeys,
    CGMLInitialState,
    CGMLNote,
    CGMLState,
    CGMLTransition
)
from cyberiadaml_py.types.common import Point, Rectangle

ListType = TypeVar('ListType')


class CGMLParserException(Exception):
    """Logical errors during parsing CGML scheme."""

    ...


def create_empty_elements() -> CGMLElements:
    """Create CGMLElements with empty fields."""
    return CGMLElements(
        state_machines={},
        format='',
        keys=defaultdict())


def create_empty_state_machine() -> CGMLStateMachine:
    """Create CGMLStateMachine with empty fields."""
    return CGMLStateMachine(
        standard_version='',
        platform='',
        meta=CGMLMeta(
            id='',
            values={},
        ),
        states={},
        transitions={},
        finals={},
        choices={},
        terminates={},
        initial_states={},
        components={},
        notes={},
        shallow_history={},
        unknown_vertexes={}
    )


def _is_empty_meta(meta: CGMLMeta) -> bool:
    return meta.values == {} and meta.id == ''


class CGMLParser:
    """Class that contains functions for parsing CyberiadaML."""

    def __init__(self) -> None:
        self.elements: CGMLElements = create_empty_elements()

    def parse_cgml(self, graphml: str) -> CGMLElements:
        """
        Parse CyberiadaGraphml scheme.

        Args:
            graphml (str): CyberiadaML scheme.

        Returns:
            CGMLElements: notes, states, transitions,\
                initial state and components
        Raises:
            CGMLParserExcpetion('First level graph doesn't contain\
                <data> with dStateMachine key!'): <graph>, that parent\
                is <graphml>, doesn't contain <data key="dStateMachine">\
                    on first level.
            CGMLParserException('Data node with key "gFormat" is empty'):\
                content of <data key='gFormat'> is None
            CGMLParserException('Data node with key "gFormat" is missing'):\
                <data key='gFormat'> doesn't exist in graphml->data
            CGMLParserException('No position for note!):\
                <node>, that contains <data key='dNote'>, graphml
                    doesn't contains <data key='dGeometry'>
            ValidationError(...): pydatinc's validation error, occurs when\
                the scheme doesn't match the format.
        """
        self.elements = create_empty_elements()
        cgml = CGML(**parse(graphml))
        graphs: List[CGMLGraph] = to_list(cgml.graphml.graph)
        format: str = self._get_format(cgml)
        for graph in graphs:
            keys: DefaultDict[str, List[CGMLKeyNode]
                              ] = self._get_available_keys(cgml)
            platform = ''
            standard_version = ''
            meta: CGMLMeta = CGMLMeta(
                id='',
                values={}
            )
            states: Dict[str, CGMLState] = {}
            transitions: Dict[str, CGMLTransition] = {}
            notes: Dict[str, CGMLNote] = {}
            terminates: Dict[str, CGMLTerminate] = {}
            finals: Dict[str, CGMLFinal] = {}
            choices: Dict[str, CGMLChoice] = {}
            initials: Dict[str, CGMLInitialState] = {}
            unknown_vertexes: Dict[str, CGMLBaseVertex] = {}
            components: Dict[str, CGMLComponent] = {}
            shallow_history: Dict[str, CGMLShallowHistory] = {}
            vertex_dicts: Dict[CGMLVertexType,
                               tuple[Dict[str, CGMLInitialState], type] |
                               tuple[Dict[str, CGMLFinal], type] |
                               tuple[Dict[str, CGMLChoice], type] |
                               tuple[Dict[str, CGMLTerminate], type] |
                               tuple[Dict[str, CGMLShallowHistory], type]] = {
                'initial': (initials, CGMLInitialState),
                'choice': (choices, CGMLChoice),
                'final': (finals, CGMLFinal),
                'terminate': (terminates, CGMLTerminate),
                'shallowHistory': (shallow_history, CGMLShallowHistory)
            }
            states = self._parse_graph_nodes(graph)
            transitions = self._parse_graph_edges(graph)
            for state_id in list(states.keys()):
                state = self._process_state_data(states[state_id])
                if isinstance(state, CGMLNote):
                    note = state
                    del states[state_id]
                    if note.type == 'informal':
                        notes[state_id] = state
                        continue
                    match note.name:
                        case 'CGML_META':
                            if not _is_empty_meta(meta):
                                raise CGMLParserException('Double meta nodes!')
                            meta.id = state_id
                            meta.values = self._parse_meta(note.text)
                            try:
                                platform = meta.values['platform']
                                standard_version = (
                                    meta.values['standardVersion'])
                            except KeyError:
                                raise CGMLParserException(
                                    'No platform or standardVersion.')
                        case 'CGML_COMPONENT':
                            component_parameters: Dict[str, str] = (
                                self._parse_meta(
                                    note.text
                                )
                            )
                            try:
                                component_id = (
                                    component_parameters['id'].strip(
                                    )
                                )
                                component_type = (
                                    component_parameters['type'].strip())
                                del component_parameters['id']
                                del component_parameters['type']
                            except KeyError:
                                raise CGMLParserException(
                                    "Component doesn't have type or id.")
                            components[state_id] = CGMLComponent(
                                id=component_id,
                                type=component_type,
                                parameters=component_parameters
                            )
                elif isinstance(state, CGMLState):
                    states[state_id] = state
                elif isinstance(state, CGMLBaseVertex):
                    vertex = state
                    del states[state_id]
                    if self.__is_vertex_type(vertex.type):
                        vertex_dict, vertex_type = vertex_dicts[vertex.type]
                        vertex_dict[state_id] = vertex_type(
                            type=vertex.type,
                            data=vertex.data,
                            position=vertex.position,
                            parent=vertex.parent
                        )
                    else:
                        unknown_vertexes[state_id] = CGMLBaseVertex(
                            type=vertex.type,
                            data=vertex.data,
                            position=vertex.position,
                            parent=vertex.parent
                        )
                else:
                    raise CGMLParserException(
                        'Internal error: Unknown type of node')

            component_ids: List[str] = []
            for transition in list(transitions.values()):
                processedTransition: CGMLTransition = self._process_edge_data(
                    transition)
                if transition.source == meta.id:
                    component_ids.append(transition.id)
                else:
                    transitions[transition.id] = processedTransition

            for component_id in component_ids:
                del transitions[component_id]
            self.elements.state_machines[graph.id] = CGMLStateMachine(
                states=states,
                transitions=transitions,
                components=components,
                initial_states=initials,
                finals=finals,
                unknown_vertexes=unknown_vertexes,
                terminates=terminates,
                notes=notes,
                choices=choices,
                name=self._get_state_machine_name(graph),
                meta=meta,
                shallow_history=shallow_history,
                platform=platform,
                standard_version=standard_version,
            )
        self.elements.keys = keys
        self.elements.format = format
        return self.elements

    def _get_state_machine_name(self, graph: CGMLGraph) -> str | None:
        graph_datas = to_list(graph.data)
        name: str | None = None
        is_state_machine = False
        for graph_data in graph_datas:
            if graph_data.key == 'dName':
                name = graph_data.content
            if graph_data.key == 'dStateMachine':
                is_state_machine = True
        if not is_state_machine:
            raise CGMLParserException(
                "First level graph doesn't contain"
                ' <data> with dStateMachine key!')
        return name

    def _parse_meta(self, meta: str) -> Dict[str, str]:
        splited_parameters: List[str] = meta.split('\n\n')
        parameters: Dict[str, str] = {}
        for parameter in splited_parameters:
            parameter_name, parameter_value = parameter.split('/')
            parameters[parameter_name.strip()] = parameter_value.strip()
        return parameters

    def _get_data_content(self, data_node: CGMLDataNode) -> str:
        return data_node.content if data_node.content is not None else ''

    def _process_edge_data(self, transition: CGMLTransition) -> CGMLTransition:
        new_transition = CGMLTransition(
            position=[],
            id=transition.id,
            source=transition.source,
            target=transition.target,
            actions=transition.actions,
            unknown_datanodes=[]
        )
        for data_node in transition.unknown_datanodes:
            match data_node.key:
                case 'dData':
                    new_transition.actions = self._get_data_content(data_node)
                case 'dGeometry':
                    if data_node.point is None:
                        raise CGMLParserException(
                            'Edge with key dGeometry\
                                doesnt have <point> node.')
                    points: List[CGMLPointNode] = (
                        to_list(data_node.point)
                    )
                    for point in points:
                        new_transition.position.append(Point(
                            x=point.x, y=point.y))
                case 'dColor':
                    new_transition.color = self._get_data_content(data_node)
                case 'dLabelGeometry':
                    if data_node.point is None:
                        raise CGMLParserException(
                            'Edge with key dGeometry\
                                doesnt have <point> node.')
                    if isinstance(data_node.point, list):
                        raise CGMLParserException(
                            'dLabelGeometry with several points!')
                    point = data_node.point
                    new_transition.label_position = Point(
                        x=point.x, y=point.y)
                case _:
                    new_transition.unknown_datanodes.append(data_node)
        return new_transition

    def __is_note_type(self, value: str) -> TypeGuard[CGMLNoteType]:
        return value in get_args(CGMLNoteType)

    def _get_note_type(self, value: str) -> CGMLNoteType:
        if self.__is_note_type(value):
            return value
        raise CGMLParserException(
            f'Unknown type of note! Expect {get_args(CGMLNoteType)}.')

    def __is_vertex_type(self, value: str) -> TypeGuard[CGMLVertexType]:
        return value in get_args(CGMLVertexType)

    def _process_state_data(self,
                            state: CGMLState
                            ) -> CGMLState | CGMLNote | CGMLBaseVertex:
        """Return tuple[CGMLState | CGMLNote, isInit]."""
        # no mutations? B^)
        new_state = CGMLState(
            name=state.name,
            actions=state.actions,
            unknown_datanodes=[],
            bounds=state.bounds,
            parent=state.parent
        )
        note_type: Optional[CGMLNoteType] = None
        vertex_type: Optional[str] = None
        is_note = False
        is_vertex = False
        for data_node in state.unknown_datanodes:
            match data_node.key:
                case 'dName':
                    new_state.name = self._get_data_content(data_node)
                case 'dGeometry':
                    if data_node.rect is None and data_node.point is None:
                        raise CGMLParserException(
                            'Node with key dGeometry\
                                doesnt have rect or point child')
                    if data_node.point is not None:
                        if isinstance(data_node.point, list):
                            raise CGMLParserException(
                                "State doesn't support several points.")
                        new_state.bounds = Point(x=data_node.point.x,
                                                 y=data_node.point.y)
                        continue

                    if (data_node.rect is not None):
                        new_state.bounds = Rectangle(
                            x=data_node.rect.x,
                            y=data_node.rect.y,
                            width=data_node.rect.width,
                            height=data_node.rect.height
                        )
                case 'dVertex':
                    is_vertex = True
                    vertex_type = self._get_data_content(data_node)
                case 'dData':
                    new_state.actions = self._get_data_content(data_node)
                case 'dNote':
                    is_note = True
                    if data_node.content is None:
                        note_type = 'informal'
                    else:
                        note_type = self._get_note_type(
                            self._get_data_content(data_node))
                case 'dColor':
                    new_state.color = self._get_data_content(data_node)
                case _:
                    new_state.unknown_datanodes.append(data_node)
        if is_note and note_type is not None:
            bounds: Optional[Rectangle | Point] = new_state.bounds
            x = 0.
            y = 0.
            if bounds is None:
                if note_type == 'informal':
                    raise CGMLParserException('No position for note!')
            else:
                x = bounds.x
                y = bounds.y
            return CGMLNote(
                parent=new_state.parent,
                name=new_state.name,
                position=Point(
                    x=x,
                    y=y,
                ),
                type=note_type,
                text=new_state.actions,
                unknown_datanodes=new_state.unknown_datanodes
            )
        if is_vertex and vertex_type is not None:
            return CGMLBaseVertex(
                type=vertex_type,
                position=new_state.bounds,
                parent=new_state.parent
            )
        return new_state

    def _get_meta(self, metaNode: CGMLState) -> tuple[str, str]:
        """Return tuple[platfrom, meta]."""
        dataNodes: List[CGMLDataNode] = to_list(
            metaNode.unknown_datanodes)
        platform: str = ''
        meta: str = ''
        for data_node in dataNodes:
            match data_node.key:
                case 'dName':
                    platform = self._get_data_content(data_node)
                case 'dData':
                    meta = self._get_data_content(data_node)
        return platform, meta

    def _parse_graph_edges(self, root: CGMLGraph) -> Dict[str, CGMLTransition]:
        def _parseEdge(edge: CGMLEdge,
                       cgmlTransitions: Dict[str, CGMLTransition]) -> None:
            cgmlTransitions[edge.id] = CGMLTransition(
                id=edge.id,
                source=edge.source,
                target=edge.target,
                actions='',
                unknown_datanodes=to_list(
                        edge.data),
            )

        cgmlTransitions: Dict[str, CGMLTransition] = {}
        if root.edge is not None:
            if isinstance(root.edge, Iterable):
                for edge in root.edge:
                    _parseEdge(edge, cgmlTransitions)
            else:
                _parseEdge(root.edge, cgmlTransitions)
        return cgmlTransitions

    def _parse_graph_nodes(
        self,
        root: CGMLGraph,
        parent: Optional[str] = None
    ) -> Dict[str, CGMLState]:
        def parseNode(node: CGMLNode) -> Dict[str, CGMLState]:
            cgmlStates: Dict[str, CGMLState] = {}
            cgmlStates[node.id] = CGMLState(
                name='',
                actions='',
                unknown_datanodes=to_list(node.data),
            )
            if parent is not None:
                cgmlStates[node.id].parent = parent
            graphs: List[CGMLGraph] = to_list(node.graph)
            for graph in graphs:
                cgmlStates = cgmlStates | self._parse_graph_nodes(
                    graph, node.id)

            return cgmlStates

        cgmlStates: Dict[str, CGMLState] = {}
        if root.node is not None:
            if isinstance(root.node, Iterable):
                for node in root.node:
                    cgmlStates = cgmlStates | parseNode(node)
            else:
                cgmlStates = cgmlStates | parseNode(root.node)
        return cgmlStates

    # key nodes to comfortable dict
    def _get_available_keys(self, cgml: CGML) -> AvailableKeys:
        keyNodeDict: AvailableKeys = defaultdict(lambda: [])
        if cgml.graphml.key is not None:
            if isinstance(cgml.graphml.key, Iterable):
                for keyNode in cgml.graphml.key:
                    keyNodeDict[keyNode.for_].append(keyNode)
            else:
                keyNodeDict[cgml.graphml.key.for_].append(cgml.graphml.key)
        return keyNodeDict

    def _get_format(self, cgml: CGML) -> str:
        # TODO: DRY
        if isinstance(cgml.graphml.data, Iterable):
            for data_node in cgml.graphml.data:
                if data_node.key == 'gFormat':
                    if data_node.content is not None:
                        return data_node.content
                    raise CGMLParserException(
                        'Data node with key "gFormat" is empty')
        else:
            if cgml.graphml.data.key == 'gFormat':
                if cgml.graphml.data.content is not None:
                    return cgml.graphml.data.content
                raise CGMLParserException(
                    'Data node with key "gFormat" is empty')
        raise CGMLParserException('Data node with key "gFormat" is missing')
