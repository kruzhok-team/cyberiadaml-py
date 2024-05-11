"""Module implements small utility functions."""
from typing import List, TypeVar

ListType = TypeVar('ListType')


def to_list(
    nodes: List[ListType] | None | ListType
) -> List[ListType]:
    """Return list of objects."""
    if nodes is None:
        return []
    if isinstance(nodes, list):
        return nodes
    else:
        return [nodes]
