from dataclasses import dataclass
from typing import Any, Callable, Optional

Key = tuple[Any, ...]


@dataclass
class Node:
    value: Any
    prev: Optional[Key]
    next: Optional[Key]


@dataclass
class Ends:
    oldest: Key
    newest: Key


@dataclass
class Cache:
    capacity: int
    nodes: dict[Key, Node]
    ends: Optional[Ends]

    def get_or_compute(self, key: Key, compute: Callable[[], Any]) -> Any:
        node = self.nodes.get(key)
        if node is not None:
            return node.value
        value = compute()
        self.nodes[key] = Node(value=value, prev=None, next=None)
        return value
