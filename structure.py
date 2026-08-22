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
            self._unlink(key)
            self._append_as_newest(key)
            return node.value
        value = compute()
        self.nodes[key] = Node(value=value, prev=None, next=None)
        self._append_as_newest(key)
        self._evict_until_within_capacity()
        return value

    def _unlink(self, key: Key) -> None:
        node = self.nodes[key]
        prev, next = node.prev, node.next

        if prev is None and next is None:
            self.ends = None
            return

        if prev is None:
            self.ends.oldest = next
        else:
            self.nodes[prev].next = next

        if next is None:
            self.ends.newest = prev
        else:
            self.nodes[next].prev = prev

    def _append_as_newest(self, key: Key) -> None:
        node = self.nodes[key]
        node.next = None

        if self.ends is None:
            node.prev = None
            self.ends = Ends(oldest=key, newest=key)
            return

        previous_newest = self.ends.newest
        node.prev = previous_newest
        self.nodes[previous_newest].next = key
        self.ends.newest = key

    def _evict_until_within_capacity(self) -> None:
        while len(self.nodes) > self.capacity and self.ends is not None:
            victim = self.ends.oldest
            self._unlink(victim)
            del self.nodes[victim]
