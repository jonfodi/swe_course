from dataclasses import dataclass
from typing import Any, Optional

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
