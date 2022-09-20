from __future__ import annotations
from re import A
import typing
import dataclasses
from collections import deque


@dataclasses.dataclass
class Node:
    id: int
    out: typing.List["Edge"] = dataclasses.field(default_factory=lambda: [])
    is_term: bool = False

    def get_edges(self, *,
                  label_full:  str | None = None,
                  label_start: str | None = None) -> typing.Generator[Edge, None, None]:
        raise NotImplementedError()
    
    def get_unique_edge(self, *,
                        label_full:  str | None = None,
                        label_start: str | None = None,
                        or_none: bool = True) -> Edge | None:
        raise NotImplementedError()
    
    def is_deterministic(self) -> bool:
        raise NotImplementedError()


@dataclasses.dataclass
class Edge:
    label: str
    src: "Node"
    dst: "Node"

    def __len__(self) -> int:
        return len(self.label)


@dataclasses.dataclass
class Automata:
    alphabet: typing.Container[str]
    # nodes: typing.List[AutomataNode]
    # edges: typing.List[AutomataEdge]
    start: Node


    def get_nodes(self) -> typing.Iterable[Node]:
        raise NotImplementedError()

    def get_edges(self) -> typing.Iterable[Edge]:
        raise NotImplementedError()
    
    def get_terms(self) -> typing.Iterable[Node]:
        return (node for node in self.get_nodes() if node.is_term)


class Visitor:
    _queue: typing.Deque[typing.Tuple[Edge | None, Node]]
    _seen: typing.Set[Node]


    def __init__(self):
        self.reset()
    
    def reset(self) -> None:
        self._queue = deque()
        self._seen = set()

    def visit(self, automata: Automata) -> None:
        self.enqueue(None, automata.start)

        while self._queue:
            edge, node = self._queue.popleft()

            if self.was_seen(node):
                continue
            self.mark_seen(node)

            self.visit_node(edge, node)
    
    def visit_node(self, edge: Edge | None, node: Node) -> None:
        self.enqueue(node)
    
    def was_seen(self, node: Node) -> bool:
        return node in self._seen
    
    def mark_seen(self, node: Node) -> None:
        self._seen.add(node)

    @typing.overload
    def enqueue(self, edge: Edge | None, node: Node) -> None:
        ...
    
    @typing.overload
    def enqueue(self, edge: Edge) -> None:
        ...
    
    @typing.overload
    def enqueue(self, node: Node) -> None:
        """
        Note: enqueues all children of given node!
        """
        ...

    def enqueue(self, *args):
        edge: Edge
        node: Node

        if len(args) == 2:
            edge, node = args
            assert isinstance(edge, (Edge, None))
            assert isinstance(node, Node)
            assert edge is None or edge.dst is node, "Invalid edge/node pair"

            self._queue.append((edge, node))
            return
        
        assert len(args) == 1

        if isinstance(args[0], Edge):
            edge = args[0]

            self._queue.append((edge, edge.out))
            return
        
        if isinstance(args[0], Node):
            node = args[0]

            for edge in node.out:
                self.enqueue(edge)
            return
        
        assert False
    
    def popqueue(self) -> typing.Tuple[Edge | None, Node]:
        return self._queue.popleft()


class Transformer(Visitor):
    pass
