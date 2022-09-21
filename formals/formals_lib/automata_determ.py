from __future__ import annotations
import typing
import copy
from collections import deque, frozenset

from .automata import *
from .automata_ops import *


class MakeEdges01(BaseAutomataTransform):
    def apply(self) -> Automata:
        result: Automata = self.raw_copy()
        
        # Copying to avoid messing up the iteration
        for edge in list(Automata.get_edges()):
            edge: Edge

            self.split_edge(result, edge)

        return result
    
    @staticmethod
    def split_edge(aut: Automata, edge: Edge) -> None:
        if len(edge.label) <= 1:
            return
        
        aut.unlink(edge)
        
        prev: Node = edge.src
        cur: Node
        for i in range(len(edge.label) - 1):
            cur = aut.make_node()
            aut.link(prev, cur, edge.label[i])
            prev = cur


class MakeEdges1(MakeEdges01):
    def apply(self) -> Automata:
        result: Automata = super().apply()
        
        self.propagate_terms(result)

        for node in result.get_nodes():
            node: Node

            self.handle_epsilon_subtree(result, node)
        
        # Copying to avoid messing up the iteration
        for edge in list(result.get_edges()):
            edge: Edge

            if len(edge.label) > 0:
                continue
            
            result.unlink(edge)

        return result
    
    @staticmethod
    def propagate_terms(aut: Automata) -> None:
        reverse_edges: typing.Dict[Node, typing.List[Node]] = {}

        for edge in aut.get_edges():
            reverse_edges.setdefault(edge.dst, []).append(edge.src)
        
        queue: typing.Deque[Node] = deque()
        queue.extend(aut.get_terms())

        while queue:
            node: Node = queue.popleft()

            node.is_term = True

            for child in reverse_edges.get(node, []):
                if child.is_term:
                    continue
                queue.append(child)
        
        return aut
    
    @staticmethod
    def handle_epsilon_subtree(aut: Automata, start: Node) -> None:
        queue: typing.Deque[Node] = deque()
        queue.append(start)

        epsilon_reachable: typing.Set[Node] = set()

        while queue:
            node: Node = queue.popleft()

            if node in epsilon_reachable:
                continue
            epsilon_reachable.add(node)

            for child in node.out:
                if len(child.label) > 0:
                    continue
                queue.append(child.dst)
        
        epsilon_reachable.remove(start)

        for node in epsilon_reachable:
            for edge in node.out:
                if len(edge.label) == 0:
                    continue
                aut.link(start, edge.dst, edge.label)


class UnifyTerm(BaseAutomataTransform):
    def apply(self) -> Automata:
        result: Automata = self.raw_copy()
        
        end: Node = result.make_node(term=True)

        for node in result.get_terms():
            if node is end:
                continue

            node.is_term = False
            result.link(node, end, "")

        return result


class MakeDeterministic(BaseAutomataTransform):
    def apply(self) -> Automata:
        # We'll use that for our guideline, not the result
        self.aut = MakeEdges1(self.aut).apply()
        self.aut = AutomataTrimmer(self.aut).apply()

        result = Automata(self.aut.alphabet)

        result.change_key(result.start, frozenset([self.aut.start.key]))
        
        self.bfs(result)

        return result
    
    def bfs(self, result: Automata) -> Automata:
        # TODO: Finish!

        return result
