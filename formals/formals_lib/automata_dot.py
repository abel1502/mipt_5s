from __future__ import annotations
import typing
import pydotplus as dot
import pathlib

from .automata import *


class AutomataDotDumper:
    _graph: dot.Dot

    def __init__(self, name="Automata", **kwargs):
        self._graph = dot.Dot(
            name,
            # rankdir="TD",
            # splines="spline",
            **kwargs,
        )
    
    def process(self, aut: Automata) -> None:
        self._add_start_edge(aut.start)

        for node in aut.get_nodes():
            self._add_node(self._make_dot_node(node, start=(node is aut.start)))
        
        for edge in aut.get_edges():
            self._add_edge(self._make_dot_edge(edge))
    
    @staticmethod
    def dot_node_name(node: Node) -> str:
        return f"q{node.id}"
    
    def _make_dot_node(self, node: Node, start: bool = False) -> dot.Node:
        name: str = self.dot_node_name(node)

        return dot.Node(
            name,
            label=f"{node.key}",
            shape="doublecircle" if node.is_term else "circle",
            color="black",
            fontcolor="black",
        )

    def _make_dot_edge(self, edge: Edge) -> dot.Edge:
        assert edge is not None

        return dot.Edge(
            self.dot_node_name(edge.src),
            self.dot_node_name(edge.dst),
            label=edge.label,
        )
    
    def _add_node(self, node: dot.Node) -> None:
        self._graph.add_node(node)
    
    def _add_edge(self, node: dot.Node) -> None:
        self._graph.add_edge(node)

    def _add_start_edge(self, dst: Node) -> None:
        self._add_node(dot.Node("_start", style="invis"))
        self._add_edge(dot.Edge("_start", self.dot_node_name(dst)))
    
    def render_graph(self, file: pathlib.Path | str, fmt="svg"):
        self._graph.write(
            str(file),
            prog="dot",
            format=fmt,
        )


def dump(aut: Automata, file: pathlib.Path | str, fmt="svg", **kwargs):
    dumper = AutomataDotDumper()
    dumper.process(aut)
    dumper.render_graph(file, fmt=fmt, **kwargs)
