from __future__ import annotations
from hashlib import new
from re import A, L
import typing
import dataclasses
from collections import deque


KeyType = typing.Any


@dataclasses.dataclass
class Node:
    id: int
    out: typing.List["Edge"] = dataclasses.field(default_factory=lambda: [])
    is_term: bool = False
    key: KeyType | None = None

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


class Automata:
    alphabet: str
    _nodes: typing.List[Node]
    _edges: typing.List[Edge]
    _node_keys: typing.Dict[KeyType, Node]
    start: Node  # Attention: start's id isn't always zero!


    def __init__(self, alphabet: str):
        self.alphabet = alphabet
        self._nodes = []
        self._edges = []
        self._node_keys = {}
        self.start = self.make_node()

    def make_node(self, key=None, term=False) -> Node:
        """
        If key is None, i is used by default
        """

        node = Node(self._next_id(), is_term=term, key=key)
        
        self._nodes.append(node)

        self.set_key(node, key)

        return node
    
    def set_start(self, new_start: Node | KeyType) -> None:
        """
        Changes the start to be new_start
        """

        if not isinstance(new_start, Node):
            new_start = self.node(new_start)

        self.start = new_start

    def id_node(self, id: int) -> Node:
        if id not in range(len(self._nodes)):
            raise IndexError("Invalid id")
        return self._nodes[id]
    
    def node(self, key: KeyType) -> Node:
        return self._node_keys[key]

    def link(self, src: Node | KeyType, dst: Node | KeyType, label: str) -> Edge:
        if not isinstance(src, Node):
            src = self.node(src)
        if not isinstance(dst, Node):
            dst = self.node(dst)
        
        edge: Edge = Edge(label, src, dst)
        self._edges.append(edge)
        src.out.append(edge)
        return edge
    
    def set_key(self, node: Node | KeyType | None, key: KeyType) -> None:
        if not isinstance(node, Node):
            node = self.node(node)
        
        if node in self._node_keys.values():
            for k, v in self._node_keys.items():
                if v is node:
                    self._node_keys.pop(k)
        
        if key is None:
            key = node.id

        assert key not in self._node_keys, "Duplicate key detected"
        self._node_keys[key] = node

    def _next_id(self) -> int:
        return len(self._nodes)

    def get_nodes(self) -> typing.Iterable[Node]:
        return self._nodes

    def get_edges(self) -> typing.Iterable[Edge]:
        return self._edges
    
    def get_terms(self) -> typing.Iterable[Node]:
        return (node for node in self.get_nodes() if node.is_term)
    
    def is_deterministic(self) -> bool:
        raise NotImplementedError()
    
    def copy(self) -> Automata:
        result = Automata(self.alphabet)

        result.start.is_term = self.start.is_term
        result.start.key = self.start.key

        for node in self.get_nodes():
            result.make_node(key=node.key, term=node.is_term)
        
        for edge in self.get_edges():
            result.link(result.id_node(edge.src.id), result.id_node(edge.dst.id), edge.label)
        
        return result

    def __copy__(self) -> Automata:
        return self.copy()
    
    def __deepcopy__(self) -> Automata:
        return self.copy()
    
    def __len__(self) -> int:
        return len(self._nodes)


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


# TODO: Maybe a Transformer class?
# class Transformer(Visitor):
#     pass

